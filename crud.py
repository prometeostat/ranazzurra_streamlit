"""
crud.py — scritture sull'anagrafica atleti.

Tutto passa da db.execute(), con lo stesso stile parametrizzato delle
letture. Regole che valgono qui:

  - nessuna cancellazione fisica: "elimina" significa is_deleted = TRUE,
    cosi' restano gare, risultati e storico;
  - ogni scrittura riempie i campi di audit gia' previsti dallo schema
    (creation_user_id, last_modification_*, deletion_*);
  - dopo ogni scrittura i cache dei dati vengono svuotati, altrimenti le
    pagine continuerebbero a mostrare la fotografia vecchia per un'ora.
"""
from __future__ import annotations

import datetime as _dt
import re

import pandas as pd
import streamlit as st

from db import execute, query_df
from queries import (ACCESS_LOG_DELETE_SQL, ATHLETE_DEACTIVATE_SQL, ATHLETE_FIN_TAKEN_SQL,
                     ATHLETE_INSERT_SQL, ATHLETE_REACTIVATE_SQL,
                     ATHLETE_UPDATE_SQL, ATHLETES_ADMIN_SQL, COMPANIES_SQL,
                     COMPETITION_DEACTIVATE_SQL, COMPETITION_INSERT_SQL,
                     COMPETITION_REACTIVATE_SQL, COMPETITION_UPDATE_SQL,
                     COMPETITIONS_ADMIN_SQL, COMP_RACES_SQL,
                     ENTRY_DEACTIVATE_SQL, ENTRY_INSERT_SQL, ENTRY_UPDATE_SQL,
                     RACE_DEACTIVATE_SQL, RACE_ENTRIES_SQL, RACE_EVENTS_SQL,
                     RACE_INSERT_SQL, RACE_UPDATE_SQL, TIMINGS_SQL)

MAX_NOME = 50        # varchar(50) su first_name, last_name ed email
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")


def _user_id() -> int:
    """
    Utente tecnico usato per i campi di audit. A DB esistono 1 = system e
    2 = devsupport; si puo' cambiare con db_user_id nei secrets [app].
    """
    try:
        return int(st.secrets["app"].get("db_user_id", 1))
    except Exception:
        return 1


def _svuota_cache() -> None:
    st.cache_data.clear()


# ══════════════════════════════════════════════════════════════════
# Letture di servizio
# ══════════════════════════════════════════════════════════════════

@st.cache_data(ttl=60, show_spinner=False)
def elenco_atleti() -> pd.DataFrame:
    """Anagrafica completa, attivi e non. TTL corto: qui si scrive spesso."""
    df = query_df(ATHLETES_ADMIN_SQL)
    for c in ("athlete_id", "fin_code", "n_gare"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


@st.cache_data(ttl=600, show_spinner=False)
def elenco_societa() -> pd.DataFrame:
    return query_df(COMPANIES_SQL)


def fin_occupato(fin_code: int | None, escludi_id: int = -1) -> str | None:
    """Nome dell'atleta che usa gia' quel codice FIN, se c'e'."""
    if fin_code is None:
        return None
    df = query_df(ATHLETE_FIN_TAKEN_SQL, (int(fin_code), int(escludi_id)))
    return None if df.empty else str(df.iloc[0]["full_name"])


# ══════════════════════════════════════════════════════════════════
# Validazione
# ══════════════════════════════════════════════════════════════════

def valida(dati: dict, athlete_id: int = -1) -> list[str]:
    """Restituisce la lista degli errori bloccanti. Vuota = si puo' salvare."""
    errori: list[str] = []

    nome = (dati.get("first_name") or "").strip()
    cognome = (dati.get("last_name") or "").strip()
    if not nome:
        errori.append("Il nome e' obbligatorio.")
    if not cognome:
        errori.append("Il cognome e' obbligatorio.")
    if len(nome) > MAX_NOME or len(cognome) > MAX_NOME:
        errori.append(f"Nome e cognome non possono superare i {MAX_NOME} caratteri.")

    email = (dati.get("email") or "").strip()
    if email:
        if len(email) > MAX_NOME:
            errori.append(f"L'e-mail non puo' superare i {MAX_NOME} caratteri.")
        elif not EMAIL_RE.match(email):
            errori.append("L'e-mail non sembra valida.")

    nascita = dati.get("birth_date")
    if nascita and nascita > _dt.date.today():
        errori.append("La data di nascita e' nel futuro.")

    atleta = bool(dati.get("is_athlete", True))
    staff = bool(dati.get("is_staff", False))
    if not atleta and not staff:
        errori.append("Serve almeno un ruolo: atleta, allenatore o tutti e due.")
    if staff and not atleta and not email:
        errori.append("Chi allena e basta entra solo con l'e-mail: e' obbligatoria.")

    fin = dati.get("fin_code")
    if fin is not None:
        altro = fin_occupato(fin, athlete_id)
        if altro:
            errori.append(f"Il codice FIN {fin} e' gia' assegnato a {altro}.")

    return errori


# ══════════════════════════════════════════════════════════════════
# Scritture
# ══════════════════════════════════════════════════════════════════

def _pulisci(dati: dict) -> tuple:
    return (
        int(dati["fin_code"]) if dati.get("fin_code") is not None else None,
        (dati.get("first_name") or "").strip(),
        (dati.get("last_name") or "").strip(),
        bool(dati.get("sex", True)),
        dati.get("birth_date"),
        ((dati.get("email") or "").strip() or None),
    )


def crea_atleta(dati: dict) -> int:
    """Inserisce una persona attiva in anagrafica e restituisce il nuovo id."""
    fin, nome, cognome, sesso, nascita, email = _pulisci(dati)
    riga = execute(
        ATHLETE_INSERT_SQL,
        (fin, nome, cognome, sesso, nascita, email,
         dati.get("company_id"), _user_id(),
         bool(dati.get("is_athlete", True)), bool(dati.get("is_staff", False))),
        returning=True,
    )
    _svuota_cache()
    return int(riga["id"]) if riga else -1


def aggiorna_atleta(athlete_id: int, dati: dict) -> int:
    fin, nome, cognome, sesso, nascita, email = _pulisci(dati)
    n = execute(ATHLETE_UPDATE_SQL,
                (fin, nome, cognome, sesso, nascita, email,
                 bool(dati.get("is_athlete", True)),
                 bool(dati.get("is_staff", False)),
                 _user_id(), int(athlete_id)))
    _svuota_cache()
    return n


def disattiva_atleta(athlete_id: int) -> int:
    """Soft delete: nessun DELETE, solo is_deleted = TRUE."""
    n = execute(ATHLETE_DEACTIVATE_SQL, (_user_id(), int(athlete_id)))
    _svuota_cache()
    return n


def riattiva_atleta(athlete_id: int) -> int:
    n = execute(ATHLETE_REACTIVATE_SQL, (_user_id(), int(athlete_id)))
    _svuota_cache()
    return n


# ══════════════════════════════════════════════════════════════════
# Manifestazioni
# ══════════════════════════════════════════════════════════════════
MAX_NOME_GARA = 100      # competitions.type e' varchar(100)
MAX_LINK = 500           # website_link e pdf_link sono varchar(500)


@st.cache_data(ttl=60, show_spinner=False)
def elenco_manifestazioni() -> pd.DataFrame:
    """Anagrafica manifestazioni, comprese le disattivate."""
    df = query_df(COMPETITIONS_ADMIN_SQL)
    for c in ("comp_id", "max_races_per_athlete", "n_gare"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


@st.cache_data(ttl=600, show_spinner=False)
def elenco_cronometraggi() -> list[str]:
    df = query_df(TIMINGS_SQL)
    return [] if df.empty else [str(v) for v in df["timing"].tolist()]


def _link_valido(url: str) -> bool:
    return (not url) or url.lower().startswith(("http://", "https://"))


def valida_manifestazione(dati: dict) -> list[str]:
    errori: list[str] = []
    nome = (dati.get("nome") or "").strip()
    if not nome:
        errori.append("Il nome della manifestazione e' obbligatorio.")
    if len(nome) > MAX_NOME_GARA:
        errori.append(f"Il nome non puo' superare i {MAX_NOME_GARA} caratteri.")

    inizio, fine = dati.get("start_date"), dati.get("end_date")
    if not inizio:
        errori.append("La data di inizio e' obbligatoria.")
    if inizio and fine and fine < inizio:
        errori.append("La data di fine viene prima di quella di inizio.")

    apertura, chiusura = dati.get("open_reg"), dati.get("close_reg")
    if apertura and chiusura and chiusura < apertura:
        errori.append("La chiusura iscrizioni viene prima dell'apertura.")
    if chiusura and inizio and chiusura > inizio:
        errori.append("Le iscrizioni chiudono dopo l'inizio della manifestazione.")

    for campo, etichetta in (("website_link", "link al sito"),
                             ("pdf_link", "link al PDF")):
        url = (dati.get(campo) or "").strip()
        if not _link_valido(url):
            errori.append(f"Il {etichetta} deve cominciare con http:// o https://.")
        if len(url) > MAX_LINK:
            errori.append(f"Il {etichetta} e' troppo lungo.")
    return errori


def _pulisci_manifestazione(dati: dict) -> tuple:
    def testo(k, limite):
        v = (dati.get(k) or "").strip()
        return v[:limite] or None
    massimo = dati.get("max_races")
    return (
        testo("nome", MAX_NOME_GARA),
        dati.get("start_date"),
        dati.get("end_date"),
        dati.get("open_reg"),
        dati.get("close_reg"),
        testo("timing", 50),
        testo("website_link", MAX_LINK),
        testo("pdf_link", MAX_LINK),
        int(massimo) if massimo else None,
        # Manifestazione del calendario federale: in dubbio vale si', come il
        # default della colonna a database.
        bool(dati.get("is_fin", True)),
    )


def crea_manifestazione(dati: dict) -> int:
    riga = execute(COMPETITION_INSERT_SQL,
                   _pulisci_manifestazione(dati) + (_user_id(),), returning=True)
    _svuota_cache()
    return int(riga["id"]) if riga else -1


def aggiorna_manifestazione(comp_id: int, dati: dict) -> int:
    n = execute(COMPETITION_UPDATE_SQL,
                _pulisci_manifestazione(dati) + (_user_id(), int(comp_id)))
    _svuota_cache()
    return n


def disattiva_manifestazione(comp_id: int) -> int:
    n = execute(COMPETITION_DEACTIVATE_SQL, (_user_id(), int(comp_id)))
    _svuota_cache()
    return n


def riattiva_manifestazione(comp_id: int) -> int:
    n = execute(COMPETITION_REACTIVATE_SQL, (_user_id(), int(comp_id)))
    _svuota_cache()
    return n


# ══════════════════════════════════════════════════════════════════
# Gare di una manifestazione
# ══════════════════════════════════════════════════════════════════

MAX_NOME_PROVA = 200     # races.name e' varchar(200)
MAX_CATEGORIA = 100      # athlete_races."group" e' varchar(100)
VASCHE = [25, 50]
PUNTI_MAX = 1500         # fin_score e' smallint, ma oltre il migliaio non si va


@st.cache_data(ttl=600, show_spinner=False)
def elenco_specialita() -> pd.DataFrame:
    """Le 32 combinazioni stile + distanza + staffetta gia' a database.

    L'app le propone e basta: non ne crea di nuove, cosi' non nascono
    doppioni e le query che raggruppano per specialita' restano pulite.
    """
    df = query_df(RACE_EVENTS_SQL)
    for c in ("race_event_id", "dist_num"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


@st.cache_data(ttl=60, show_spinner=False)
def gare_manifestazione(comp_id: int) -> pd.DataFrame:
    df = query_df(COMP_RACES_SQL, (int(comp_id),))
    for c in ("race_id", "pool_length", "race_event_id", "iscritti",
              "con_tempo", "dist_num"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def nome_gara_proposto(etichetta: str, dettaglio: str = "") -> str:
    """"50 Dorso" + "Assoluti Maschi" -> "50 Dorso - Assoluti Maschi".

    E' il formato che hanno le 2.867 gare gia' a database, meglio non
    inventarne un altro adesso.
    """
    dettaglio = (dettaglio or "").strip()
    nome = f"{etichetta} - {dettaglio}" if dettaglio else etichetta
    return nome[:MAX_NOME_PROVA]


def valida_gara(dati: dict) -> list[str]:
    errori: list[str] = []
    if not dati.get("race_event_id"):
        errori.append("Scegli la specialita'.")
    nome = (dati.get("nome") or "").strip()
    if not nome:
        errori.append("Il nome della gara e' obbligatorio.")
    if len(nome) > MAX_NOME_PROVA:
        errori.append(f"Il nome non puo' superare i {MAX_NOME_PROVA} caratteri.")
    if dati.get("pool_length") not in VASCHE:
        errori.append("La vasca puo' essere 25 o 50 metri.")
    return errori


def crea_gara(comp_id: int, dati: dict) -> int:
    riga = execute(RACE_INSERT_SQL, (
        (dati.get("nome") or "").strip()[:MAX_NOME_PROVA],
        int(dati["pool_length"]),
        int(comp_id),
        int(dati["race_event_id"]),
        _user_id(),
    ), returning=True)
    _svuota_cache()
    return int(riga["id"]) if riga else -1


def aggiorna_gara(race_id: int, dati: dict) -> int:
    n = execute(RACE_UPDATE_SQL, (
        (dati.get("nome") or "").strip()[:MAX_NOME_PROVA],
        int(dati["pool_length"]),
        int(dati["race_event_id"]),
        _user_id(),
        int(race_id),
    ))
    _svuota_cache()
    return n


def elimina_gara(race_id: int) -> tuple[bool, str]:
    """Soft delete, ma solo se la gara e' vuota.

    Con dei tempi dentro, cancellare la gara li porterebbe via tutti in un
    colpo solo senza che si veda: meglio dire quanti sono e lasciare che si
    tolgano da Inserisci tempi, uno per uno e con gli occhi aperti.
    """
    iscritti = iscritti_gara(int(race_id))
    if not iscritti.empty:
        return False, (f"La gara ha {len(iscritti)} iscritti: togli prima i "
                       "tempi da Inserisci tempi, poi la elimini.")
    execute(RACE_DEACTIVATE_SQL, (_user_id(), int(race_id)))
    _svuota_cache()
    return True, "Gara eliminata."


# ══════════════════════════════════════════════════════════════════
# Tempi degli atleti in gara
# ══════════════════════════════════════════════════════════════════

@st.cache_data(ttl=60, show_spinner=False)
def iscritti_gara(race_id: int) -> pd.DataFrame:
    df = query_df(RACE_ENTRIES_SQL, (int(race_id),))
    for c in ("entry_id", "athlete_id", "time_sec", "fin_score"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


# 29.45 · 1:02.35 · 1:01:02.35, con la virgola al posto del punto se capita
_TEMPO_RE = re.compile(r"^(?:(\d{1,2}):)?(?:(\d{1,2}):)?(\d{1,2})(?:[.,](\d{1,3}))?$")


def tempo_da_testo(testo: str | None) -> tuple[_dt.time | None, str | None]:
    """Testo digitato -> time di Postgres. Ritorna (valore, errore).

    Vuoto e' un valore buono: vuol dire iscritto senza tempo (non partito,
    ritirato o squalificato), che a database esiste gia' in 136 righe.
    """
    testo = (testo or "").strip()
    if not testo:
        return None, None
    m = _TEMPO_RE.match(testo)
    if not m:
        return None, (f"Tempo non valido: \"{testo}\". Usa 29.45, 1:02.35 "
                      "oppure 1:01:02.35.")
    a, b, sec, cent = m.groups()
    # Un solo gruppo prima dei secondi sono i minuti, due sono ore e minuti.
    ore, minuti = (int(a), int(b)) if b is not None else (0, int(a or 0))
    sec = int(sec)
    micro = int((cent or "0").ljust(3, "0")) * 1000
    if minuti > 59 or sec > 59:
        return None, f"Tempo non valido: \"{testo}\". Minuti e secondi vanno da 0 a 59."
    if ore > 23:
        return None, f"Tempo non valido: \"{testo}\"."
    if (ore, minuti, sec, micro) == (0, 0, 0, 0):
        return None, "Un tempo di zero non esiste: lascia vuoto se non c'e'."
    return _dt.time(ore, minuti, sec, micro), None


def tempo_in_testo(secondi) -> str:
    """Secondi -> testo editabile, senza le virgolette del formato a video."""
    if secondi is None or pd.isna(secondi):
        return ""
    s = float(secondi)
    ore, resto = int(s // 3600), s % 3600
    minuti, sec = int(resto // 60), resto % 60
    if ore:
        return f"{ore}:{minuti:02d}:{sec:05.2f}"
    if minuti:
        return f"{minuti}:{sec:05.2f}"
    return f"{sec:.2f}"


def _pulisci_punti(valore) -> tuple[int | None, str | None]:
    if valore is None or (isinstance(valore, float) and pd.isna(valore)):
        return None, None
    testo = str(valore).strip()
    if not testo:
        return None, None
    try:
        n = int(float(testo))
    except ValueError:
        return None, f"Punteggio non valido: \"{testo}\"."
    if n < 0 or n > PUNTI_MAX:
        return None, f"Punteggio fuori scala: {n}."
    return n, None


def salva_tempi(race_id: int, righe: list[dict],
                originali: list[dict]) -> tuple[dict, list[str]]:
    """Scrive la griglia dei tempi di una gara.

    righe: quello che si vede adesso, una voce per riga con athlete_id,
    tempo (testo), punti, categoria e entry_id (None se la riga e' nuova).
    originali: com'era prima, per capire cosa e' cambiato.

    Prima si controlla tutto, poi si scrive: se una riga sola e' sbagliata
    non parte nessuna query, se no si resterebbe a meta' strada.
    """
    errori: list[str] = []
    pronte: list[dict] = []
    visti: set[int] = set()

    for i, r in enumerate(righe, start=1):
        aid = r.get("athlete_id")
        if aid is None or (isinstance(aid, float) and pd.isna(aid)):
            errori.append(f"Riga {i}: manca l'atleta.")
            continue
        aid = int(aid)
        if aid in visti:
            errori.append(f"Riga {i}: l'atleta e' gia' in questa gara.")
            continue
        visti.add(aid)

        tempo, err = tempo_da_testo(r.get("tempo"))
        if err:
            errori.append(f"Riga {i}: {err}")
        punti, err_p = _pulisci_punti(r.get("punti"))
        if err_p:
            errori.append(f"Riga {i}: {err_p}")
        categoria = (str(r.get("categoria") or "").strip() or None)
        if categoria:
            categoria = categoria[:MAX_CATEGORIA]

        pronte.append({"entry_id": r.get("entry_id"), "athlete_id": aid,
                       "tempo": tempo, "punti": punti, "categoria": categoria})

    if errori:
        return {}, errori

    prima = {int(o["entry_id"]): o for o in originali
             if o.get("entry_id") is not None}
    conteggi = {"inseriti": 0, "modificati": 0, "eliminati": 0}
    rimaste: set[int] = set()

    for r in pronte:
        eid = r["entry_id"]
        if eid is None or (isinstance(eid, float) and pd.isna(eid)):
            execute(ENTRY_INSERT_SQL, (int(race_id), r["athlete_id"], r["tempo"],
                                       r["punti"], r["categoria"], _user_id()))
            conteggi["inseriti"] += 1
            continue
        eid = int(eid)
        rimaste.add(eid)
        vecchia = prima.get(eid)
        nuova = (r["athlete_id"], r["tempo"], r["punti"], r["categoria"])
        if vecchia is not None:
            tempo_vecchio, _ = tempo_da_testo(vecchia.get("tempo"))
            punti_vecchi, _ = _pulisci_punti(vecchia.get("punti"))
            cat_vecchia = (str(vecchia.get("categoria") or "").strip() or None)
            if nuova == (int(vecchia["athlete_id"]), tempo_vecchio,
                         punti_vecchi, cat_vecchia):
                continue          # niente da scrivere, la riga e' uguale
        execute(ENTRY_UPDATE_SQL, (r["athlete_id"], r["tempo"], r["punti"],
                                   r["categoria"], _user_id(), eid))
        conteggi["modificati"] += 1

    for eid in prima:
        if eid not in rimaste:
            execute(ENTRY_DEACTIVATE_SQL, (_user_id(), eid))
            conteggi["eliminati"] += 1

    _svuota_cache()
    return conteggi, []


# ══════════════════════════════════════════════════════════════════
# Registro accessi
# ══════════════════════════════════════════════════════════════════

def svuota_registro() -> int:
    """
    Cancella davvero le righe del registro accessi e restituisce quante ne
    ha tolte. Qui la cancellazione fisica ci sta: un log si svuota, non si
    disattiva, e tenere righe morte in giro non aiuterebbe nessuno.
    """
    return int(execute(ACCESS_LOG_DELETE_SQL) or 0)
