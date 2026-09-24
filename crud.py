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
from queries import (ATHLETE_DEACTIVATE_SQL, ATHLETE_FIN_TAKEN_SQL,
                     ATHLETE_INSERT_SQL, ATHLETE_REACTIVATE_SQL,
                     ATHLETE_UPDATE_SQL, ATHLETES_ADMIN_SQL, COMPANIES_SQL,
                     COMPETITION_DEACTIVATE_SQL, COMPETITION_INSERT_SQL,
                     COMPETITION_REACTIVATE_SQL, COMPETITION_UPDATE_SQL,
                     COMPETITIONS_ADMIN_SQL, TIMINGS_SQL)

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
    """Inserisce un atleta attivo e restituisce il nuovo id."""
    fin, nome, cognome, sesso, nascita, email = _pulisci(dati)
    riga = execute(
        ATHLETE_INSERT_SQL,
        (fin, nome, cognome, sesso, nascita, email,
         dati.get("company_id"), _user_id()),
        returning=True,
    )
    _svuota_cache()
    return int(riga["id"]) if riga else -1


def aggiorna_atleta(athlete_id: int, dati: dict) -> int:
    fin, nome, cognome, sesso, nascita, email = _pulisci(dati)
    n = execute(ATHLETE_UPDATE_SQL,
                (fin, nome, cognome, sesso, nascita, email,
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
