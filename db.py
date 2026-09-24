"""
db.py — Connessione PostgreSQL (Aiven) per Streamlit.

Usa psycopg3 (psycopg[binary]) con SSL.

Ordine di lettura della configurazione:
  1. st.secrets["postgres"]           -> Streamlit Cloud e locale (.streamlit/secrets.toml)
  2. variabili d'ambiente PG*/DATABASE_URL -> comodo per run locali senza secrets
Se non trova nulla mostra un messaggio che dice esattamente cosa creare.

Il CA cert è opzionale: se presente e valido si usa verify-ca,
altrimenti fallback a sslmode=require (SSL cifrato, no CA verify).
"""
from __future__ import annotations

import os
import tempfile
from urllib.parse import urlparse, unquote

import streamlit as st
import psycopg
from psycopg.rows import dict_row
import pandas as pd


# --------------------------------------------------------------------------- #
# Configurazione
# --------------------------------------------------------------------------- #
def _cfg_from_secrets() -> dict | None:
    """
    Legge [postgres] dai secrets.
    Va catturata Exception generica: se secrets.toml non esiste Streamlit
    solleva StreamlitSecretNotFoundError, non KeyError.
    """
    try:
        return dict(st.secrets["postgres"])
    except Exception:
        return None


def _cfg_from_env() -> dict | None:
    """Fallback su variabili d'ambiente (DATABASE_URL oppure PGHOST/PGPORT/...)."""
    url = os.getenv("DATABASE_URL") or os.getenv("PG_URL")
    if url:
        p = urlparse(url)
        if p.hostname:
            return {
                "host":        p.hostname,
                "port":        p.port or 5432,
                "dbname":      (p.path or "/defaultdb").lstrip("/") or "defaultdb",
                "user":        unquote(p.username or "avnadmin"),
                "password":    unquote(p.password or ""),
                "sslrootcert": os.getenv("PG_CA_CERT", ""),
            }

    host = os.getenv("PGHOST") or os.getenv("PG_HOST")
    if not host:
        return None
    return {
        "host":        host,
        "port":        os.getenv("PGPORT") or os.getenv("PG_PORT") or 5432,
        "dbname":      os.getenv("PGDATABASE") or os.getenv("PG_DBNAME") or "defaultdb",
        "user":        os.getenv("PGUSER") or os.getenv("PG_USER") or "avnadmin",
        "password":    os.getenv("PGPASSWORD") or os.getenv("PG_PASSWORD") or "",
        "sslrootcert": os.getenv("PG_CA_CERT", ""),
    }


def _load_cfg() -> dict:
    cfg = _cfg_from_secrets() or _cfg_from_env()
    if cfg:
        return cfg

    st.error(
        "⚠️ Configurazione DB mancante.\n\n"
        "**In locale**: crea il file `.streamlit/secrets.toml` accanto ad `app.py` "
        "partendo da `.streamlit/secrets.toml.example` e compila la sezione `[postgres]`.\n\n"
        "**Su Streamlit Cloud**: incolla la stessa sezione in *App settings → Secrets*.\n\n"
        "In alternativa esporta le variabili d'ambiente `PGHOST`, `PGPORT`, "
        "`PGDATABASE`, `PGUSER`, `PGPASSWORD` (oppure `DATABASE_URL`)."
    )
    st.stop()


def _write_ca_cert(cert_content: str) -> str | None:
    """
    Scrive il CA cert in un file temporaneo.
    Ritorna None se il cert è vuoto o palesemente malformato.
    """
    if not cert_content or not str(cert_content).strip():
        return None
    content = str(cert_content).strip()
    if "-----BEGIN CERTIFICATE-----" not in content:
        return None
    if "-----END CERTIFICATE-----" not in content:
        return None
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pem", mode="w")
        tmp.write(content)
        tmp.flush()
        tmp.close()
        return tmp.name
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Connessione
# --------------------------------------------------------------------------- #
def _connect(cfg: dict, **ssl_kwargs):
    conn = psycopg.connect(
        host            = cfg["host"],
        port            = int(cfg["port"]),
        dbname          = cfg["dbname"],
        user            = cfg["user"],
        password        = cfg["password"],
        row_factory     = dict_row,
        connect_timeout = 15,
        **ssl_kwargs,
    )
    conn.autocommit = True
    return conn


@st.cache_resource(show_spinner=False)
def _get_connection():
    """Connessione persistente al DB Aiven."""
    cfg = _load_cfg()

    if not cfg.get("password"):
        st.error(
            "⚠️ Password del DB non impostata: hai lasciato il segnaposto in "
            "`.streamlit/secrets.toml`. Incolla la password reale dell'utente "
            f"`{cfg.get('user', 'avnadmin')}` (console Aiven → servizio → "
            "Connection information)."
        )
        st.stop()

    ssl_kwargs: dict = {"sslmode": "require"}
    ca_path = _write_ca_cert(cfg.get("sslrootcert", ""))
    if ca_path:
        ssl_kwargs["sslrootcert"] = ca_path
        ssl_kwargs["sslmode"] = "verify-ca"

    try:
        return _connect(cfg, **ssl_kwargs)
    except psycopg.OperationalError as e:
        msg = str(e).lower()
        # Retry senza CA verification se il problema è il certificato
        if ca_path and ("root certificate" in msg or "bad base64" in msg or "ssl" in msg):
            try:
                return _connect(cfg, sslmode="require")
            except Exception as e2:
                st.error(f"❌ Impossibile connettersi al DB: {e2}")
                st.stop()
        st.error(f"❌ Impossibile connettersi al DB: {e}")
        st.stop()


# --------------------------------------------------------------------------- #
# Query
# --------------------------------------------------------------------------- #
def query_df(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Esegue una query e restituisce un DataFrame pandas."""
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return pd.DataFrame(rows)
    except psycopg.OperationalError:
        # Riconnette se la connessione è caduta (idle timeout Aiven, rete, ecc.)
        st.cache_resource.clear()
        conn = _get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return pd.DataFrame(rows)


# ------------------------------------------------------------------------- #
# Scritture
# ------------------------------------------------------------------------- #

def execute(sql: str, params: tuple = (), returning: bool = False):
    """
    Esegue una scrittura. Con returning=True restituisce la prima riga
    (dict, perche' la connessione usa dict_row), altrimenti il numero di
    righe toccate. La connessione e' in autocommit, come per le letture.
    """
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone() if returning else cur.rowcount
    except psycopg.OperationalError:
        # connessione caduta: riapre e riprova una volta sola
        st.cache_resource.clear()
        conn = _get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone() if returning else cur.rowcount
