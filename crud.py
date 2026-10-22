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
                     COMPETITIONS_ADMIN_SQL, COMP_ENTRIES_ADMIN_SQL,
                     COMP_RACES_SQL, ENTRY_DEACTIVATE_SQL, ENTRY_INSERT_SQL,
                     ENTRY_OWNER_SQL, ENTRY_REACTIVATE_SQL, ENTRY_STATE_SQL,
                     ENTRY_UPDATE_SQL,
                     RACE_DEACTIVATE_SQL, RACE_ENTRIES_SQL, RACE_EVENTS_SQL,
                     RACE_INSERT_SQL, RACE_PROGRAM_UPDATE_SQL,
                     RACE_UPDATE_SQL, SIGNUP_COUNT_SQL,
                     GESTIONE_CONTEGGI_SQL, MY_SIGNUPS_SQL,
                     SIGNUP_INSERT_SQL, SIGNUP_MEETS_SQL,
                     SIGNUP_RACES_SQL,
                     SIGNUP_UPDATE_SQL, SIGNUP_WINDOW_SQL, TIMINGS_SQL,
                     FAVORITES_SQL, FAVORITE_DELETE_SQL,
                     FAVORITE_INSERT_SQL)

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
    """Inserisce una persona in anagrafica e restituisce il nuovo id.

    Lo stato arriva dal form: "Attivo" spuntato vuol dire is_deleted = FALSE,
    che e' anche il valore predefinito. La scadenza del certificato e'
    facoltativa e puo' restare nulla.
    """
    fin, nome, cognome, sesso, nascita, email = _pulisci(dati)
    riga = execute(
        ATHLETE_INSERT_SQL,
        (fin, nome, cognome, sesso, nascita, email,
         dati.get("company_id"), _user_id(),
         bool(dati.get("is_athlete", True)), bool(dati.get("is_staff", False)),
         not bool(dati.get("attivo", True)), dati.get("certificato")),
        returning=True,
    )
    _svuota_cache()
    return int(riga["id"]) if riga else -1


def aggiorna_atleta(athlete_id: int, dati: dict) -> int:
    """Aggiorna i dati anagrafici, certificato medico compreso.

    Lo stato Attivo NON passa di qui: ha le sue due funzioni, che riempiono
    anche i campi di cancellazione (deletion_user_id e la data). Il form lo
    gestisce chiamandole quando la spunta cambia.
    """
    fin, nome, cognome, sesso, nascita, email = _pulisci(dati)
    n = execute(ATHLETE_UPDATE_SQL,
                (fin, nome, cognome, sesso, nascita, email,
                 bool(dati.get("is_athlete", True)),
                 bool(dati.get("is_staff", False)),
                 dati.get("certificato"),
                 _user_id(), int(athlete_id)))
    _svuota_cache()
    return n


def imposta_stato_atleta(athlete_id: int, attivo: bool) -> int:
    """Attiva o disattiva, riusando le funzioni di soft delete di sempre."""
    return (riattiva_atleta(int(athlete_id)) if attivo
            else disattiva_atleta(int(athlete_id)))


def salva_anagrafica(righe: list[dict]) -> tuple[int, list[str]]:
    """
    Scrive piu' atleti in un colpo, come li ha lasciati la griglia.

    O passa tutto o non passa niente: prima si validano tutte le righe, e
    solo se non c'e' un errore si comincia a scrivere. Con una griglia da
    270 righe salvarne meta' e fermarsi su un errore lascerebbe
    l'anagrafica in uno stato che nessuno sa piu' ricostruire.

    Ogni voce ha athlete_id piu' i campi modificabili. Le righe che non
    risultano cambiate rispetto a database non vengono nemmeno toccate, cosi'
    un salvataggio a vuoto non riscrive 270 volte lo stesso dato.
    Restituisce quante righe ha cambiato e gli errori trovati.
    """
    attuale = elenco_atleti()
    if attuale.empty:
        return 0, ["Anagrafica non disponibile."]
    per_id = {int(r["athlete_id"]): r for r in attuale.to_dict("records")}

    errori: list[str] = []
    da_scrivere: list[tuple[int, dict, bool | None]] = []
    fin_nel_lotto: dict[int, str] = {}

    for r in righe:
        aid = _intero(r.get("athlete_id"))
        if aid is None or aid not in per_id:
            continue                      # riga che non e' di questa anagrafica
        prima = per_id[aid]
        chi = (f"{_testo_o_vuoto(r.get('last_name'))} "
               f"{_testo_o_vuoto(r.get('first_name'))}").strip() or f"id {aid}"

        dati = {
            "fin_code": _intero(r.get("fin_code")),
            "first_name": _testo_o_vuoto(r.get("first_name")),
            "last_name": _testo_o_vuoto(r.get("last_name")),
            "sex": bool(r.get("sex")),
            "birth_date": _data_pura(r.get("birth_date")),
            "email": _testo_o_vuoto(r.get("email")),
            "is_athlete": bool(r.get("is_athlete")),
            "is_staff": bool(r.get("is_staff")),
            "certificato": _data_pura(r.get("certificato")),
        }

        for e in valida(dati, aid):
            errori.append(f"{chi}: {e}")

        # Il codice FIN e' unico, ma valida() lo cerca a database e non vede
        # le altre righe della griglia: due atleti a cui si da' lo stesso
        # numero nello stesso salvataggio passerebbero il controllo.
        fin = dati["fin_code"]
        if fin is not None:
            if fin in fin_nel_lotto:
                errori.append(f"{chi}: il codice FIN {fin} e' stato dato anche "
                              f"a {fin_nel_lotto[fin]} in questa tabella.")
            fin_nel_lotto[fin] = chi

        attivo = bool(r.get("attivo", True))
        era_attivo = not bool(prima.get("is_deleted"))
        cambia_stato = attivo if attivo != era_attivo else None

        if _anagrafica_cambiata(prima, dati) or cambia_stato is not None:
            da_scrivere.append((aid, dati, cambia_stato))

    if errori:
        return 0, errori

    for aid, dati, cambia_stato in da_scrivere:
        aggiorna_atleta(aid, dati)
        if cambia_stato is not None:
            imposta_stato_atleta(aid, cambia_stato)
    return len(da_scrivere), []


def _testo_o_vuoto(v) -> str:
    """Stringa pulita, mai None: i campi di testo della griglia tornano
    stringa vuota quando si svuota la cella, e pd.NA quando non si tocca."""
    try:
        if v is None or pd.isna(v):
            return ""
    except (TypeError, ValueError):
        pass
    return str(v).strip()


def _anagrafica_cambiata(prima: dict, dopo: dict) -> bool:
    """Confronto campo per campo con quello che c'e' a database."""
    confronti = (
        (_intero(prima.get("fin_code")), dopo["fin_code"]),
        (_testo_o_vuoto(prima.get("first_name")), dopo["first_name"]),
        (_testo_o_vuoto(prima.get("last_name")), dopo["last_name"]),
        (bool(prima.get("sex")), dopo["sex"]),
        (_data_pura(prima.get("birth_date")), dopo["birth_date"]),
        (_testo_o_vuoto(prima.get("email")), dopo["email"]),
        (bool(prima.get("is_athlete")), dopo["is_athlete"]),
        (bool(prima.get("is_staff")), dopo["is_staff"]),
        (_data_pura(prima.get("certificato")), dopo["certificato"]),
    )
    return any(a != b for a, b in confronti)


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

# Fin dove si puo' datare una manifestazione. Non e' un vincolo del database,
# che sulle `date` accetta molto di piu': e' il calendario sensato per questa
# squadra, lo storico piu' vecchio a database e' del 2003.
#
# Serve soprattutto ai campi data dell'anagrafica: **st.date_input senza
# min_value e max_value ammette solo dieci anni intorno al valore che ha in
# mano**, e il calendario rifiutava una gara del 2003 con un "Date set outside
# allowed range" che non spiegava niente. I limiti vanno quindi messi a mano
# su ogni campo data, e qui ci sono una volta sola perche' il form di
# inserimento, quello di modifica e quello di clonazione dicano la stessa
# cosa. Li ricontrolla anche `valida_manifestazione`: l'interfaccia restringe
# quello che si puo' scegliere, non autorizza quello che si scrive.
PRIMA_DATA_GARA = _dt.date(1990, 1, 1)
ULTIMA_DATA_GARA = _dt.date(2999, 12, 31)


@st.cache_data(ttl=60, show_spinner=False)
def elenco_manifestazioni() -> pd.DataFrame:
    """Anagrafica manifestazioni, comprese le disattivate."""
    df = query_df(COMPETITIONS_ADMIN_SQL)
    for c in ("comp_id", "max_races_per_athlete", "n_gare",
              "organizer_company_id"):
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

    # Il calendario del campo data gia' non lascia scegliere fuori intervallo,
    # ma una data puo' arrivare anche da una griglia o da un clone: si
    # ricontrolla qui, dove la regola vale per tutti.
    for campo, etichetta in (("start_date", "data di inizio"),
                             ("end_date", "data di fine"),
                             ("open_reg", "apertura iscrizioni"),
                             ("close_reg", "chiusura iscrizioni")):
        quando = _data_pura(dati.get(campo))
        if quando is None:
            continue
        if not (PRIMA_DATA_GARA <= quando <= ULTIMA_DATA_GARA):
            errori.append(
                f"La {etichetta} deve stare fra il "
                f"{PRIMA_DATA_GARA.strftime('%d/%m/%Y')} e il "
                f"{ULTIMA_DATA_GARA.strftime('%d/%m/%Y')}.")

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


def _intero(v) -> int | None:
    """
    Intero oppure None. Passa da pd.isna per primo: i valori che arrivano da
    un data_editor con colonna Int64 sono pd.NA, e pd.NA dentro un confronto
    come `v in (None, "")` solleverebbe TypeError invece di dire "vuoto".
    """
    try:
        if v is None or pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(v, str) and not v.strip():
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _data_pura(v) -> _dt.date | None:
    """datetime.date oppure None: psycopg da' date, pandas a volte Timestamp
    o NaT, e un data_editor svuotato da' None."""
    try:
        if v is None or pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(v, pd.Timestamp):
        return v.date()
    if isinstance(v, _dt.datetime):
        return v.date()
    return v if isinstance(v, _dt.date) else None


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
        # organizer_company_id accetta NULL e buona parte dello storico ce
        # l'ha davvero vuoto: zero e pd.NA valgono "non indicato".
        _intero(dati.get("organizer_company_id")) or None,
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
# Fasce orarie di una giornata di gara, nell'ordine in cui si nuotano. Il
# numero e' quello che sta a database in races.session, con un CHECK che lo
# tiene fra 1 e 3. In una giornata ci possono essere solo il mattino, solo il
# pomeriggio, mattino e pomeriggio oppure pomeriggio e sera: l'app non
# impone quali combinazioni, le riconosce e basta.
SESSIONI = {1: "Mattino", 2: "Pomeriggio", 3: "Sera"}
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
              "con_tempo", "dist_num", "session", "race_order"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "race_date" in df.columns:
        df["race_date"] = pd.to_datetime(df["race_date"], errors="coerce")
    return df


def nome_gara_proposto(etichetta: str, dettaglio: str = "") -> str:
    """"50 Dorso" + "Assoluti Maschi" -> "50 Dorso - Assoluti Maschi".

    E' il formato che hanno le 2.867 gare gia' a database, meglio non
    inventarne un altro adesso.
    """
    dettaglio = (dettaglio or "").strip()
    nome = f"{etichetta} - {dettaglio}" if dettaglio else etichetta
    return nome[:MAX_NOME_PROVA]


def _sessione(v) -> int | None:
    """Numero di fascia oraria valido, oppure None. Accetta anche l'etichetta
    a video ('Mattino'), che e' quello che torna da un data_editor."""
    n = _intero(v)
    if n in SESSIONI:
        return n
    testo = "" if n is not None else str(v or "").strip().lower()
    for numero, nome in SESSIONI.items():
        if testo == nome.lower():
            return numero
    return None


def valida_gara(dati: dict, manifestazione: dict | None = None) -> list[str]:
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

    ordine = _intero(dati.get("race_order"))
    if ordine is not None and ordine < 1:
        errori.append("Il numero di programma parte da 1.")
    if dati.get("session") is not None and _sessione(dati.get("session")) is None:
        errori.append("La fascia oraria puo' essere mattino, pomeriggio o sera.")

    # La giornata deve cadere dentro la manifestazione. Il controllo si fa
    # qui e non con un CHECK: starebbe su due tabelle e vorrebbe un trigger.
    giorno = dati.get("race_date")
    if giorno is not None and manifestazione:
        inizio = manifestazione.get("start_date")
        fine = manifestazione.get("end_date") or inizio
        if inizio and (giorno < inizio or giorno > fine):
            errori.append(
                f"La giornata {giorno.strftime('%d/%m/%Y')} e' fuori dalla "
                f"manifestazione ({inizio.strftime('%d/%m/%Y')}"
                + (f" – {fine.strftime('%d/%m/%Y')}" if fine != inizio else "")
                + ").")
    return errori


def _programma(dati: dict) -> tuple:
    """(giornata, fascia, numero di programma) pronti per il database."""
    return (dati.get("race_date") or None,
            _sessione(dati.get("session")),
            _intero(dati.get("race_order")))


def _inserisci_gara(comp_id: int, dati: dict) -> int:
    """L'INSERT nudo, senza svuotare i cache: la clonazione ne fa molte di
    fila e li svuota una volta sola alla fine."""
    riga = execute(RACE_INSERT_SQL, (
        (dati.get("nome") or "").strip()[:MAX_NOME_PROVA],
        int(dati["pool_length"]),
        int(comp_id),
        int(dati["race_event_id"]),
    ) + _programma(dati) + (_user_id(),), returning=True)
    return int(riga["id"]) if riga else -1


def crea_gara(comp_id: int, dati: dict) -> int:
    nuovo = _inserisci_gara(int(comp_id), dati)
    _svuota_cache()
    return nuovo


def aggiorna_gara(race_id: int, dati: dict) -> int:
    # Niente utente di ultima modifica: races non ha quella colonna.
    n = execute(RACE_UPDATE_SQL, (
        (dati.get("nome") or "").strip()[:MAX_NOME_PROVA],
        int(dati["pool_length"]),
        int(dati["race_event_id"]),
    ) + _programma(dati) + (int(race_id),))
    _svuota_cache()
    return n


def salva_programma(comp_id: int, righe: list[dict]) -> tuple[int, list[str]]:
    """
    Scrive giornata, fascia e numero di programma di piu' gare in un colpo.

    Tocca solo quelle tre colonne: nome, vasca e specialita' restano quelle
    che sono, cosi' la griglia del programma non puo' rovinare il resto della
    gara. Le righe che non appartengono a questa manifestazione vengono
    scartate, non e' un controllo di cortesia: l'id arriva da un data_editor
    e una riga sbagliata riscriverebbe la gara di un'altra manifestazione.
    Restituisce quante ne ha aggiornate e gli errori trovati.
    """
    gare = gare_manifestazione(int(comp_id))
    ammesse = set(gare["race_id"].dropna().astype(int)) if not gare.empty else set()

    manif = elenco_manifestazioni()
    riga_m = manif[manif["comp_id"] == int(comp_id)]
    quale = riga_m.iloc[0].to_dict() if not riga_m.empty else {}
    limiti = {"start_date": _data_pura(quale.get("start_date")),
              "end_date": _data_pura(quale.get("end_date"))}

    errori: list[str] = []
    da_scrivere = []
    for r in righe:
        rid = _intero(r.get("race_id"))
        if rid is None or rid not in ammesse:
            continue
        giorno = _data_pura(r.get("race_date"))
        fascia = _sessione(r.get("session"))
        ordine = _intero(r.get("race_order"))
        if ordine is not None and ordine < 1:
            errori.append(f"Gara {rid}: il numero di programma parte da 1.")
            continue
        if giorno is not None and limiti["start_date"]:
            fine = limiti["end_date"] or limiti["start_date"]
            if giorno < limiti["start_date"] or giorno > fine:
                errori.append(f"Gara {rid}: la giornata "
                              f"{giorno.strftime('%d/%m/%Y')} e' fuori dalla "
                              "manifestazione.")
                continue
        da_scrivere.append((giorno, fascia, ordine, rid))

    if errori:
        return 0, errori

    fatte = 0
    for parametri in da_scrivere:
        fatte += execute(RACE_PROGRAM_UPDATE_SQL, parametri)
    _svuota_cache()
    return fatte, []


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
# Clonazione di una manifestazione
# ══════════════════════════════════════════════════════════════════

def clona_manifestazione(dati: dict, gare: list[dict]) -> tuple[int, int]:
    """
    Crea la manifestazione e ci riattacca le gare scelte.

    Si copia solo la struttura: nessun risultato viene duplicato, perche' i
    tempi appartengono all'edizione in cui sono stati nuotati. Restituisce
    l'id nuovo e quante gare sono state create; le righe senza specialita' o
    senza vasca valida vengono saltate, non fanno fallire tutto.
    """
    nuovo_id = crea_manifestazione(dati)
    if nuovo_id < 0:
        return -1, 0
    fatte = 0
    for g in gare:
        evento = _intero(g.get("race_event_id"))
        vasca = _intero(g.get("pool_length"))
        if not evento or vasca not in VASCHE:
            continue
        riga = {"nome": (g.get("nome") or "").strip(),
                "pool_length": vasca, "race_event_id": evento}
        if not riga["nome"]:
            continue
        if _inserisci_gara(nuovo_id, riga) > 0:
            fatte += 1
    _svuota_cache()
    return nuovo_id, fatte


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
# Iscrizioni alle gare
# ══════════════════════════════════════════════════════════════════
# L'iscrizione e' la riga di athlete_races con entry_time valorizzato e
# final_time ancora vuoto: quando la gara e' stata nuotata, Inserisci tempi
# scrive il risultato sulla riga che c'e' gia'.
#
# Tutti i controlli stanno qui e non nelle pagine: la finestra temporale, il
# limite di gare e la proprieta' dell'iscrizione si rileggono dal database
# prima di ogni scrittura. Un bottone disabilitato a video non e' una
# garanzia di niente.

# Quanti giorni prima dell'apertura ufficiale la squadra raccoglie le
# adesioni. Vale sia per il bottone in Agenda sia per la scrittura: la
# regola e' una sola, e sta anche nelle query (vedi queries.FINESTRA_APERTA).
GIORNI_ANTICIPO = 30

# Quanti giorni prima della chiusura ufficiale l'atleta smette di poter
# scrivere. L'ultimo giorno resta alla squadra per portare le adesioni sul
# portale federale: dal giorno di close_registration_date in poi non si
# iscrive e non si modifica piu' niente, si guarda. Vale per Iscriviti, per
# Modifica e per il bottone in Agenda, e la stessa condizione sta in SQL.
GIORNI_CODA = 1


def ultimo_giorno_utile(chiusura) -> _dt.date | None:
    """L'ultimo giorno in cui l'atleta puo' ancora scrivere."""
    quando = _data_pura(chiusura)
    return None if quando is None else quando - _dt.timedelta(days=GIORNI_CODA)


def primo_giorno_utile(apertura) -> _dt.date | None:
    """Il primo giorno in cui si raccolgono le adesioni."""
    quando = _data_pura(apertura)
    return None if quando is None else quando - _dt.timedelta(days=GIORNI_ANTICIPO)


def stato_finestra(apertura, chiusura,
                   oggi: _dt.date | None = None) -> tuple[bool, str]:
    """
    (si puo' scrivere, perche' no), decisa sulle due date della
    manifestazione.

    La usa l'interfaccia per disegnare bottoni e messaggi: Agenda, le due
    pagine di iscrizione e la lista. Il controllo vero lo rifa' comunque
    `salva_iscrizioni`, che rilegge la finestra a database prima di scrivere.
    Sta qui una volta sola perche' prima ogni pagina se la riscriveva, e una
    riscrittura che resta indietro e' un bottone che promette quello che poi
    il server rifiuta.
    """
    oggi = oggi or _dt.date.today()
    da, a = primo_giorno_utile(apertura), ultimo_giorno_utile(chiusura)
    if da is None or a is None:
        return False, "Date di iscrizione non ancora registrate"
    if a < da:
        return False, "Le date di iscrizione non sono coerenti"
    if oggi < da:
        return False, f"Si parte il {da.strftime('%d/%m/%Y')}"
    if oggi > a:
        return False, f"Chiuse il {a.strftime('%d/%m/%Y')}"
    return True, ""


@st.cache_data(ttl=60, show_spinner=False)
def conteggi_gestione() -> dict:
    """I numeri dell'indice Gestione in una query sola.

    Con quattro letture separate i riquadri comparivano a scaglioni, uno per
    ogni risposta del database: la pagina sembrava rotta.
    """
    df = query_df(GESTIONE_CONTEGGI_SQL)
    if df.empty:
        return {}
    return {k: int(v or 0) for k, v in df.iloc[0].to_dict().items()}


@st.cache_data(ttl=60, show_spinner=False)
def manifestazioni_iscrivibili() -> pd.DataFrame:
    """Manifestazioni con le iscrizioni aperte oggi, estremi compresi."""
    df = query_df(SIGNUP_MEETS_SQL)
    for c in ("comp_id", "max_gare", "n_gare"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def finestra_iscrizioni(comp_id: int) -> dict:
    """Stato della finestra, riletto a database. Niente cache: e' il
    controllo che decide se una scrittura puo' partire."""
    df = query_df(SIGNUP_WINDOW_SQL, (int(comp_id),))
    if df.empty:
        return {"esiste": False, "aperta": False}
    r = df.iloc[0].to_dict()
    r["esiste"] = True
    r["aperta"] = bool(r.get("aperta"))
    massimo = r.get("max_gare")
    # Limite non valorizzato (o zero) vuol dire nessun limite dichiarato.
    r["max_gare"] = (None if massimo is None or pd.isna(massimo)
                     or int(massimo) <= 0 else int(massimo))
    return r


def motivo_chiusura(finestra: dict) -> str:
    """Frase da mostrare quando non si puo' scrivere."""
    if not finestra.get("esiste"):
        return "Manifestazione non trovata o non piu' attiva."
    apertura, chiusura = finestra.get("apertura"), finestra.get("chiusura")
    if apertura is None or chiusura is None:
        return ("Per questa manifestazione non sono state registrate le date "
                "di apertura e chiusura iscrizioni: chiedi all'amministratore.")
    oggi = _dt.date.today()
    anticipo = (_data_pura(finestra.get("anticipo"))
                or primo_giorno_utile(apertura))
    ultimo = (_data_pura(finestra.get("ultimo_giorno"))
              or ultimo_giorno_utile(chiusura))
    if anticipo is not None and oggi < anticipo:
        return (f"Si raccolgono le iscrizioni dal {anticipo.strftime('%d/%m/%Y')}, "
                f"{GIORNI_ANTICIPO} giorni prima dell'apertura ufficiale del "
                f"{apertura.strftime('%d/%m/%Y')}.")
    if ultimo is not None and oggi > ultimo:
        return (f"Il termine era il {ultimo.strftime('%d/%m/%Y')}, il giorno "
                f"prima della chiusura ufficiale del "
                f"{chiusura.strftime('%d/%m/%Y')}: l'ultimo giorno serve alla "
                "squadra per portare le adesioni sul portale federale. Per "
                "una correzione adesso serve l'amministratore.")
    return "Iscrizioni non disponibili."


@st.cache_data(ttl=60, show_spinner=False)
def gare_iscrizione(comp_id: int, athlete_id: int) -> pd.DataFrame:
    """Gare della manifestazione con la mia iscrizione e il mio personale.

    Il personale arriva dalla query: stessa specialita' e stessa vasca, solo
    gare individuali gia' nuotate.
    """
    df = query_df(SIGNUP_RACES_SQL, (int(athlete_id), int(athlete_id),
                                     int(comp_id)))
    for c in ("race_id", "pool_length", "dist_num", "entry_id", "entry_sec",
              "time_sec", "pb_sec", "session", "race_order"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "race_date" in df.columns:
        df["race_date"] = pd.to_datetime(df["race_date"], errors="coerce")
    return df


@st.cache_data(ttl=60, show_spinner=False)
def iscrizioni_manifestazione(comp_id: int) -> pd.DataFrame:
    """Tutte le iscrizioni di una manifestazione, per allenatori e admin."""
    df = query_df(COMP_ENTRIES_ADMIN_SQL, (int(comp_id),))
    for c in ("entry_id", "athlete_id", "fin_code", "birth_year", "race_id",
              "pool_length", "dist_num", "entry_sec", "time_sec",
              "session", "race_order"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "race_date" in df.columns:
        df["race_date"] = pd.to_datetime(df["race_date"], errors="coerce")
    return df


@st.cache_data(ttl=60, show_spinner=False)
def mie_iscrizioni(athlete_id: int) -> pd.DataFrame:
    """Le mie iscrizioni alle manifestazioni non ancora concluse."""
    df = query_df(MY_SIGNUPS_SQL, (int(athlete_id),))
    for c in ("entry_id", "comp_id", "pool_length", "entry_sec", "time_sec",
              "session", "race_order"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "race_date" in df.columns:
        df["race_date"] = pd.to_datetime(df["race_date"], errors="coerce")
    return df


def mie_manifestazioni(athlete_id: int) -> pd.DataFrame:
    """
    Una riga per manifestazione in cui l'atleta ha almeno un'iscrizione.

    L'ordine arriva dalla query: prima quelle da nuotare, dalla piu' vicina,
    poi lo storico dalla piu' recente. Serve a tre posti (l'indice delle
    iscrizioni, la pagina Modifica e la lista), quindi sta qui e non in
    pagina: contate in tre modi diversi, i numeri non tornavano.
    """
    mie = mie_iscrizioni(int(athlete_id))
    if mie.empty:
        return mie
    mie = mie.copy()
    mie["start_date"] = pd.to_datetime(mie["start_date"], errors="coerce")
    quante = mie.groupby("comp_id", sort=False).size()
    teste = mie.drop_duplicates(subset="comp_id").copy()
    colonne = [c for c in ("comp_id", "manifestazione", "start_date",
                           "chiusura", "ultimo_giorno", "aperta", "futura")
               if c in teste.columns]
    teste = teste[colonne]
    teste["gare"] = teste["comp_id"].map(quante).astype(int)
    return teste


def conta_individuali(athlete_id: int, comp_id: int) -> int:
    df = query_df(SIGNUP_COUNT_SQL, (int(athlete_id), int(comp_id)))
    return 0 if df.empty else int(df.iloc[0]["individuali"] or 0)


def _iscrizione_di(entry_id: int) -> dict | None:
    """Una riga di iscrizione per id, con il suo proprietario.

    Non la usa piu' il salvataggio, che adesso rilegge tutta la
    manifestazione con _stato_a_database: resta per chi deve controllare una
    riga sola, per esempio prima di toccarla da una pagina di servizio.
    """
    df = query_df(ENTRY_OWNER_SQL, (int(entry_id),))
    return None if df.empty else df.iloc[0].to_dict()


def _stato_a_database(athlete_id: int, comp_id: int) -> dict[int, dict]:
    """
    Le righe che l'atleta ha davvero in quella manifestazione, adesso.

    Niente cache: `gare_iscrizione` ne ha uno da 60 secondi, giusto per la
    pagina ma pessimo per decidere se inserire o aggiornare. Fra il momento
    in cui la pagina ha letto le gare e il momento in cui si salva puo'
    essere entrata una riga da un'altra scheda del browser, da un altro
    dispositivo o da Inserisci tempi, e allora l'inserimento sbatterebbe
    contro l'indice unico.

    Restituisce race_id -> riga, con la riga attiva che ha la precedenza su
    quella cancellata (l'ORDER BY mette le attive per prime).
    """
    df = query_df(ENTRY_STATE_SQL, (int(athlete_id), int(comp_id)))
    stato: dict[int, dict] = {}
    if df.empty:
        return stato
    for r in df.to_dict("records"):
        stato.setdefault(int(r["race_id"]), r)
    return stato


def salva_iscrizioni(athlete_id: int, comp_id: int,
                     scelte: list[dict]) -> tuple[dict, list[str]]:
    """Allinea le iscrizioni dell'atleta a quello che ha scelto in pagina.

    scelte: una voce per gara con race_id, iscritto (bool), tempo (testo) e
    l'entry_id se l'iscrizione c'e' gia'.

    Controlla tutto prima di scrivere: finestra aperta, gare che appartengono
    davvero a questa manifestazione, limite delle individuali, formato dei
    tempi, e che ogni riga toccata sia dell'atleta e non porti gia' un
    risultato. Se qualcosa non torna non parte nessuna query.
    """
    errori: list[str] = []
    finestra = finestra_iscrizioni(int(comp_id))
    if not finestra.get("aperta"):
        return {}, [motivo_chiusura(finestra)]

    # Le gare vere di questa manifestazione, rilette a database: cosi' un
    # race_id arrivato da un widget manomesso non passa.
    vere = gare_iscrizione(int(comp_id), int(athlete_id))
    if vere.empty:
        return {}, ["Questa manifestazione non ha gare."]
    mappa = {int(r["race_id"]): r for r in vere.to_dict("records")}

    volute: list[dict] = []
    for s in scelte:
        rid = s.get("race_id")
        if rid is None or int(rid) not in mappa:
            errori.append("Gara non valida per questa manifestazione.")
            continue
        gara = mappa[int(rid)]
        if not s.get("iscritto"):
            continue
        relay = bool(gara.get("is_relay"))
        # Nelle staffette l'atleta da' la disponibilita': la squadra e il
        # tempo li decide l'allenatore, qui non si scrive nessun tempo.
        tempo, err = (None, None) if relay else tempo_da_testo(s.get("tempo"))
        if err:
            errori.append(f"{gara['etichetta']}: {err}")
        # Campo lasciato vuoto: vale il personale, che e' il tempo che la
        # segreteria metterebbe comunque sul modulo.
        if not relay and tempo is None and not err:
            pb = gara.get("pb_sec")
            if pb is not None and not pd.isna(pb):
                tempo, _ = tempo_da_testo(tempo_in_testo(pb))
        volute.append({"race_id": int(rid), "relay": relay, "tempo": tempo,
                       "entry_id": s.get("entry_id")})

    massimo = finestra.get("max_gare")
    individuali = sum(1 for v in volute if not v["relay"])
    if massimo is not None and individuali > massimo:
        errori.append(f"Puoi iscriverti al massimo a {massimo} gare "
                      f"individuali: ne hai scelte {individuali}. Le "
                      "staffette non contano.")

    # Lo stato vero, riletto adesso e senza cache: e' questo che decide fra
    # inserire, aggiornare e riattivare, non l'entry_id che arriva dalla
    # pagina. La pagina puo' avere in mano una fotografia vecchia di un
    # minuto, e intanto la riga puo' essere nata altrove.
    stato = _stato_a_database(int(athlete_id), int(comp_id))
    presenti = {rid: r for rid, r in stato.items() if not r["is_deleted"]}
    tenute = {v["race_id"] for v in volute}

    for rid, r in presenti.items():
        if rid in tenute:
            continue
        if r.get("final_time") is not None:
            nome = mappa.get(rid, {}).get("etichetta", f"gara {rid}")
            errori.append(f"{nome}: c'e' gia' il tempo di gara, "
                          "l'iscrizione non si puo' togliere. Chiedi "
                          "all'amministratore.")

    if errori:
        return {}, errori

    conteggi = {"inserite": 0, "aggiornate": 0, "tolte": 0}

    try:
        for v in volute:
            riga = stato.get(v["race_id"])

            if riga is None:
                # Nessuna traccia: si inserisce. L'ON CONFLICT dentro la
                # query fa da rete se la riga nasce proprio adesso da
                # un'altra parte: aggiorna il tempo invece di fallire.
                execute(SIGNUP_INSERT_SQL, (v["race_id"], int(athlete_id),
                                            v["tempo"], _user_id()))
                conteggi["inserite"] += 1
                continue

            if riga["is_deleted"]:
                # Si era tolto e ci ripensa: si rimette in piedi la riga
                # vecchia invece di crearne un'altra sulla stessa gara.
                execute(ENTRY_REACTIVATE_SQL, (v["tempo"], _user_id(),
                                               int(riga["entry_id"])))
                conteggi["inserite"] += 1
                continue

            if riga.get("final_time") is not None:
                continue                  # c'e' gia' il risultato
            if riga.get("entry_time") == v["tempo"]:
                continue                  # niente da cambiare
            execute(SIGNUP_UPDATE_SQL, (v["tempo"], _user_id(),
                                        int(riga["entry_id"])))
            conteggi["aggiornate"] += 1

        for rid, r in presenti.items():
            if rid in tenute or r.get("final_time") is not None:
                continue
            execute(ENTRY_DEACTIVATE_SQL, (_user_id(), int(r["entry_id"])))
            conteggi["tolte"] += 1
    except Exception:
        # Qualunque cosa vada storta a database, l'atleta non deve vedere un
        # traceback: le scritture vanno una per volta e in autocommit,
        # quindi quelle gia' passate restano e basta rifare il salvataggio.
        _svuota_cache()
        return {}, ["Non sono riuscito a salvare tutto: riapri la pagina e "
                    "controlla le tue iscrizioni prima di riprovare."]

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


# ══════════════════════════════════════════════════════════════════
# Preferiti
# ══════════════════════════════════════════════════════════════════
# La stella accanto a un atleta, legata a chi l'ha messa. Prima stava solo
# in `st.session_state` e quindi durava quanto la sessione: su Community
# Cloud l'app va in pausa da sola e al risveglio i preferiti erano spariti.
# Adesso la riga sta su `athlete_favorites` e segue l'atleta su qualunque
# dispositivo.

PREFERITI_VUOTI = ["athlete_id", "full_name", "inattivo", "da_quando"]


def _tabella_assente(err: Exception) -> bool:
    """
    True se l'errore e' "questa tabella non esiste" (SQLSTATE 42P01).

    Serve a non far cadere mezza app quando il codice arriva a destinazione
    prima della sua tabella: il deploy su Community Cloud parte da un push,
    la migrazione la si lancia a mano, e fra i due c'e' una finestra. In
    quella finestra i preferiti devono spegnersi, non buttare giu' il
    Profilo e la Scheda atleta, che la stella la disegnano tutte e due.
    """
    return (getattr(err, "sqlstate", None) == "42P01"
            or type(err).__name__ == "UndefinedTable")


@st.cache_data(ttl=300, show_spinner=False)
def preferiti_di(athlete_id: int) -> pd.DataFrame:
    """
    I preferiti di un atleta, in ordine alfabetico e gia' con i nomi.

    Cachata perche' la stella si disegna in piu' punti della stessa pagina
    (il selettore, l'elenco, la testata della scheda) e sarebbe una lettura
    per ognuno. Ogni scrittura svuota il cache, quindi la stella cambia
    colore subito.

    Senza la tabella torna vuota: l'app resta in piedi e la stella non fa
    niente. Qualunque altro errore passa, perche' nasconderlo vorrebbe dire
    mostrare "nessun preferito" a chi invece ne ha.
    """
    try:
        df = query_df(FAVORITES_SQL, (int(athlete_id),))
    except Exception as err:
        if _tabella_assente(err):
            return pd.DataFrame(columns=PREFERITI_VUOTI)
        raise
    if not df.empty:
        df["athlete_id"] = pd.to_numeric(df["athlete_id"], errors="coerce")
    return df


def aggiungi_preferito(athlete_id: int, preferito_id: int) -> bool:
    """Mette la stella. Ripetere l'operazione non e' un errore.

    Torna False se la tabella non c'e' ancora, cosi' la pagina puo' dirlo
    invece di far finta che sia andata."""
    try:
        execute(FAVORITE_INSERT_SQL, (int(athlete_id), int(preferito_id),
                                      _user_id()))
    except Exception as err:
        if _tabella_assente(err):
            return False
        raise
    preferiti_di.clear()
    return True


def togli_preferito(athlete_id: int, preferito_id: int) -> bool:
    """Toglie la stella. Se non c'era, non succede niente."""
    try:
        execute(FAVORITE_DELETE_SQL, (int(athlete_id), int(preferito_id)))
    except Exception as err:
        if _tabella_assente(err):
            return False
        raise
    preferiti_di.clear()
    return True


# ══════════════════════════════════════════════════════════════════
# Il sollecito della pre-iscrizione
# ══════════════════════════════════════════════════════════════════
# Due date diverse, e non è una svista.
#
# Il **limite tecnico** è il giorno prima della chiusura ufficiale: oltre
# quello `salva_iscrizioni` non scrive più, ed è la regola di
# `queries.FINESTRA_APERTA`.
#
# Il **sollecito** è il giorno prima dell'apertura ufficiale, ed è una
# scadenza della squadra, non del portale: il giorno in cui si apre il
# portale federale gli allenatori devono già avere le adesioni in mano per
# portarcele. Chi si pre-iscrive dopo può ancora farlo dall'app, ma rischia
# di arrivare quando l'iscrizione vera è già stata mandata.
#
# Il sollecito avvisa e basta: non blocca niente e non entra in nessun
# controllo di scrittura.

GIORNI_SOLLECITO_ROSSO = 3   # da qui in giù la fascia diventa rossa


def prossimo_sollecito(athlete_id: int | None,
                       oggi: _dt.date | None = None) -> dict | None:
    """
    La pre-iscrizione più urgente da fare, o None se non ce n'è nessuna.

    Si prende la manifestazione più vicina fra quelle su cui oggi si può
    ancora scrivere: l'elenco arriva già filtrato e ordinato per data da
    `manifestazioni_iscrivibili()`, quindi è la prima.

    Torna anche quante gare l'atleta ha già scelto lì dentro, perché a chi
    si è già pre-iscritto non si fa la predica: gli si dice solo fino a
    quando può cambiare idea.
    """
    aperte = manifestazioni_iscrivibili()
    if aperte.empty:
        return None

    r = aperte.iloc[0].to_dict()
    apertura = _data_pura(r.get("apertura"))
    if apertura is None:
        return None

    oggi = oggi or _dt.date.today()
    sollecito = apertura - _dt.timedelta(days=GIORNI_CODA)
    ultimo = _data_pura(r.get("ultimo_giorno")) or ultimo_giorno_utile(
        r.get("chiusura"))

    mie = 0
    if athlete_id is not None:
        righe = mie_iscrizioni(int(athlete_id))
        if not righe.empty:
            mie = int((righe["comp_id"] == int(r["comp_id"])).sum())

    return {
        "comp_id": int(r["comp_id"]),
        "nome": str(r.get("nome") or "Manifestazione"),
        "start_date": _data_pura(r.get("start_date")),
        "apertura": apertura,
        "sollecito": sollecito,
        "ultimo_giorno": ultimo,
        "giorni": (sollecito - oggi).days,
        "scaduto": oggi > sollecito,
        "mie_gare": mie,
    }
