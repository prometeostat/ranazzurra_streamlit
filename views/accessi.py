"""
views/accessi.py — registro accessi, riservato all'amministratore.

Una riga per evento nella tabella access_log: chi e' entrato, come, chi e'
uscito e quali tentativi sono falliti. Si scarica in txt e si puo' svuotare,
con conferma, perche' un registro che non si puo' azzerare diventa presto
inutile.
"""
from __future__ import annotations

import datetime as _dt

import pandas as pd
import streamlit as st

import auth
import crud
import data
from views._common import page_header

RIGHE = 500

page_header("Registro accessi", "Chi entra e quando")

if not auth.is_admin():
    st.info("Il registro e' riservato all'amministratore.")
    st.stop()

_msg = st.session_state.pop("log_msg", None)
if _msg:
    st.success(_msg)

stat = data.access_log_stats()
righe_totali = int(stat.get("righe") or 0)

if not righe_totali:
    st.info("Registro vuoto: nessun accesso ancora registrato. Le righe "
            "compaiono qui dal prossimo ingresso.")
    st.stop()


def _quando(v) -> str:
    q = pd.to_datetime(v, errors="coerce")
    return "—" if pd.isna(q) else q.strftime("%d/%m/%Y %H:%M:%S")


k = st.columns(3)
k[0].metric("Righe", righe_totali)
k[1].metric("Accessi", int(stat.get("accessi") or 0))
k[2].metric("Tentativi falliti", int(stat.get("falliti") or 0))
st.caption(f"Dal {_quando(stat.get('dal'))} al {_quando(stat.get('al'))}, "
           "ora italiana.")

log = data.load_access_log(RIGHE)

# ── Filtri ────────────────────────────────────────────────────────
tipi = ["Tutti"] + sorted(log["event_type"].dropna().unique().tolist())
c1, c2 = st.columns([2, 3])
tipo = c1.selectbox("Evento", tipi, key="log_tipo")
cerca = c2.text_input("Cerca", placeholder="Nome, codice FIN…", key="log_cerca")

vista = log if tipo == "Tutti" else log[log["event_type"] == tipo]
if cerca.strip():
    chiave = cerca.strip().lower()
    testo = (vista["full_name"].fillna("").astype(str) + " "
             + vista["fin_code"].fillna("").astype(str) + " "
             + vista["note"].fillna("").astype(str))
    vista = vista[testo.str.lower().str.contains(chiave, na=False)]

st.caption(f"{len(vista)} righe mostrate, ultime {RIGHE} in ordine dalla piu' "
           "recente.")

def _intero(col) -> pd.Series:
    """Colonne numeriche con i buchi: niente None a video, niente migliaia."""
    n = pd.to_numeric(col, errors="coerce")
    return n.map(lambda v: "—" if pd.isna(v) else f"{int(v)}")


tabella = pd.DataFrame({
    "Quando": pd.to_datetime(vista["quando"]),
    "Evento": vista["event_type"],
    "Atleta": vista["full_name"].fillna("—"),
    "ID": _intero(vista["athlete_id"]),
    "Cod. FIN": _intero(vista["fin_code"]),
    "Ruolo": vista["user_role"].fillna("—"),
    "Via": vista["via"].fillna("—"),
    "Note": vista["note"].fillna(""),
})
st.dataframe(
    tabella, use_container_width=True, hide_index=True,
    column_config={"Quando": st.column_config.DatetimeColumn(
        "Quando", format="DD/MM/YYYY HH:mm:ss")},
)

# ── Scarica e svuota ──────────────────────────────────────────────
righe_txt = "\n".join(
    " | ".join([
        _quando(r["quando"]),
        str(r["event_type"]),
        f"id={int(r['athlete_id'])}" if pd.notna(r["athlete_id"]) else "",
        f"nome={r['full_name']}" if pd.notna(r["full_name"]) else "",
        f"fin={int(r['fin_code'])}" if pd.notna(r["fin_code"]) else "",
        f"ruolo={r['user_role']}" if pd.notna(r["user_role"]) else "",
        f"via={r['via']}" if pd.notna(r["via"]) else "",
        str(r["note"]) if pd.notna(r["note"]) else "",
    ]).replace(" |  | ", " | ").rstrip(" |")
    for r in log.to_dict("records")
)
intestazione = (f"Registro accessi Master Conegliano\n"
                f"Esportato il {_dt.datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                f"{len(log)} righe su {righe_totali} a database\n"
                f"{'-' * 60}\n")

b1, b2 = st.columns(2)
b1.download_button("⬇  Scarica LOG", intestazione + righe_txt,
                   file_name=f"accessi_{_dt.date.today():%Y%m%d}.txt",
                   mime="text/plain", use_container_width=True, type="primary")
if b2.button("🗑  Cancella", use_container_width=True):
    st.session_state["log_conferma"] = True

if st.session_state.get("log_conferma"):
    st.warning(f"Confermi la cancellazione di tutte le {righe_totali} righe "
               "del registro? Qui la cancellazione e' definitiva, non e' una "
               "disattivazione: scarica prima il LOG se ti serve.")
    c_ok, c_no = st.columns(2)
    if c_ok.button("Sì, cancella tutto", type="primary", use_container_width=True):
        tolte = crud.svuota_registro()
        utente = auth.current_user() or {}
        auth.registra_accesso("SVUOTATO", id=utente.get("athlete_id"),
                              nome=utente.get("full_name"),
                              ruolo=utente.get("role"),
                              nota=f"{tolte} righe cancellate")
        st.session_state["log_conferma"] = False
        st.session_state["log_msg"] = (f"Registro svuotato: {tolte} righe "
                                       "cancellate. Resta solo questa riga, "
                                       "che tiene traccia dello svuotamento.")
        st.rerun()
    if c_no.button("Annulla", use_container_width=True):
        st.session_state["log_conferma"] = False
        st.rerun()
