"""
views/anagrafica.py — Anagrafica atleti: elenco, nuovo, modifica, disattiva.

"Elimina" non cancella niente: mette is_deleted = TRUE, che nell'interfaccia
si legge come Attivo = No. Cosi' restano gare, risultati e storico attaccati
all'atleta. Chi e' gia' inattivo non si puo' eliminare di nuovo: gli si
propone Riattiva.
"""
from __future__ import annotations

import datetime as _dt

import pandas as pd
import streamlit as st

import auth
import crud
from views._common import page_header

STATI = ["Attivi", "Inattivi", "Tutti"]
ORDINAMENTI = {
    "Cognome": "last_name",
    "Nome": "first_name",
    "Codice FIN": "fin_code",
    "E-Mail": "email",
}

page_header("Anagrafica atleti", "Gestione tesserati")

if not auth.is_admin():
    st.info("L'anagrafica e' riservata all'amministratore. "
            "I tempi restano visibili a tutti dalle altre pagine.")
    st.stop()

st.session_state.setdefault("anag_mode", "lista")   # lista | nuovo | modifica
st.session_state.setdefault("anag_id", None)
st.session_state.setdefault("anag_conferma", None)


def _torna_alla_lista() -> None:
    st.session_state["anag_mode"] = "lista"
    st.session_state["anag_id"] = None
    st.session_state["anag_conferma"] = None


def _data(v):
    """Normalizza a datetime.date: psycopg da' date, pandas a volte Timestamp."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, pd.Timestamp):
        return None if pd.isna(v) else v.date()
    return v


def _societa_predefinita(df: pd.DataFrame):
    """La societa' piu' usata in anagrafica: il default per i nuovi atleti."""
    if df.empty or "company_id" not in df.columns:
        return None
    valori = df["company_id"].dropna()
    return int(valori.mode().iloc[0]) if not valori.empty else None


# ══════════════════════════════════════════════════════════════════
# Form di inserimento e modifica
# ══════════════════════════════════════════════════════════════════

def _form(atleta: dict | None) -> None:
    nuovo = atleta is None
    titolo = "Nuovo atleta" if nuovo else f"Modifica · {atleta['last_name']} {atleta['first_name']}"
    st.markdown(f'<div class="section-title">{titolo}</div>', unsafe_allow_html=True)

    if not nuovo:
        st.caption(f"ID {int(atleta['athlete_id'])} · assegnato dal database, "
                   "non modificabile.")

    with st.form("form_atleta", clear_on_submit=False):
        c1, c2 = st.columns(2)
        cognome = c1.text_input("Cognome *", value="" if nuovo else (atleta["last_name"] or ""),
                                max_chars=crud.MAX_NOME)
        nome = c2.text_input("Nome *", value="" if nuovo else (atleta["first_name"] or ""),
                             max_chars=crud.MAX_NOME)

        c3, c4 = st.columns(2)
        fin_attuale = "" if nuovo or pd.isna(atleta.get("fin_code")) \
            else str(int(atleta["fin_code"]))
        fin = c3.text_input("Codice FIN", value=fin_attuale, max_chars=10,
                            help="Solo cifre. Serve anche per il login dell'atleta.")
        sesso_attuale = "Maschile" if nuovo or atleta.get("sex") else "Femminile"
        sesso = c4.radio("Sesso *", ["Maschile", "Femminile"], horizontal=True,
                         index=0 if sesso_attuale == "Maschile" else 1)

        c5, c6 = st.columns(2)
        nascita = c5.date_input(
            "Data di nascita",
            value=None if nuovo else _data(atleta.get("birth_date")),
            format="DD/MM/YYYY",
            min_value=_dt.date(1920, 1, 1), max_value=_dt.date.today(),
            help="Serve per la categoria master e per il login.",
        )
        email = c6.text_input("E-Mail", value="" if nuovo else (atleta.get("email") or ""),
                              max_chars=crud.MAX_NOME)

        st.checkbox("Attivo", value=True if nuovo else (not atleta["is_deleted"]),
                    disabled=True,
                    help="Si cambia con i pulsanti Disattiva e Riattiva nell'elenco.")

        b1, b2 = st.columns([1, 1])
        salva = b1.form_submit_button("Salva", type="primary", use_container_width=True)
        annulla = b2.form_submit_button("Annulla", use_container_width=True)

    if annulla:
        _torna_alla_lista()
        st.rerun()

    if not salva:
        return

    if fin.strip() and not fin.strip().isdigit():
        st.error("Il codice FIN deve contenere solo cifre.")
        return

    dati = {
        "first_name": nome,
        "last_name": cognome,
        "fin_code": int(fin.strip()) if fin.strip() else None,
        "sex": sesso == "Maschile",
        "birth_date": nascita,
        "email": email,
    }
    errori = crud.valida(dati, -1 if nuovo else int(atleta["athlete_id"]))
    if errori:
        for e in errori:
            st.error(e)
        return

    if nuovo:
        dati["company_id"] = _societa_predefinita(crud.elenco_atleti())
        nuovo_id = crud.crea_atleta(dati)
        st.session_state["anag_msg"] = (
            f"Atleta creato con ID {nuovo_id}: {cognome} {nome}.")
    else:
        crud.aggiorna_atleta(int(atleta["athlete_id"]), dati)
        st.session_state["anag_msg"] = f"Anagrafica aggiornata: {cognome} {nome}."

    _torna_alla_lista()
    st.rerun()


# ══════════════════════════════════════════════════════════════════
# Elenco
# ══════════════════════════════════════════════════════════════════

atleti = crud.elenco_atleti()
if atleti.empty:
    st.warning("Nessun atleta in anagrafica.")
    st.stop()

_msg = st.session_state.pop("anag_msg", None)
if _msg:
    st.success(_msg)

modo = st.session_state["anag_mode"]
if modo == "nuovo":
    _form(None)
    st.stop()
if modo == "modifica":
    riga = atleti[atleti["athlete_id"] == st.session_state["anag_id"]]
    if riga.empty:
        _torna_alla_lista()
        st.rerun()
    _form(riga.iloc[0].to_dict())
    st.stop()

# ── Barra comandi ─────────────────────────────────────────────────
c_new, c_stato, c_cerca = st.columns([1.2, 2, 3], vertical_alignment="bottom")
if c_new.button("＋  Nuovo atleta", type="primary", use_container_width=True):
    st.session_state["anag_mode"] = "nuovo"
    st.rerun()
stato = c_stato.radio("Stato", STATI, horizontal=True, index=0, key="anag_stato")
cerca = c_cerca.text_input("Cerca", placeholder="Cognome, nome, codice FIN o e-mail…",
                           key="anag_cerca")

c_ord, c_verso = st.columns([2, 2])
ordina = c_ord.selectbox("Ordina per", list(ORDINAMENTI), key="anag_ordina")
verso = c_verso.radio("Verso", ["Crescente", "Decrescente"], horizontal=True,
                      key="anag_verso")

# ── Filtri ────────────────────────────────────────────────────────
vista = atleti.copy()
if stato == "Attivi":
    vista = vista[vista["is_deleted"] == False]      # noqa: E712
elif stato == "Inattivi":
    vista = vista[vista["is_deleted"] == True]       # noqa: E712

if cerca.strip():
    k = cerca.strip().lower()
    testo = (vista["last_name"].fillna("") + " " + vista["first_name"].fillna("")
             + " " + vista["email"].fillna("")
             + " " + vista["fin_code"].astype("Int64").astype(str)
                                      .replace("<NA>", "", regex=False))
    vista = vista[testo.str.lower().str.contains(k, na=False)]

vista = vista.sort_values(ORDINAMENTI[ordina], ascending=(verso == "Crescente"),
                          na_position="last")

st.caption(f"{len(vista)} atleti su {len(atleti)} in anagrafica "
           f"({int((atleti['is_deleted'] == False).sum())} attivi).")  # noqa: E712

if vista.empty:
    st.info("Nessun atleta con questi filtri.")
    st.stop()

tabella = pd.DataFrame({
    "ID": vista["athlete_id"].astype(int),
    "Codice FIN": vista["fin_code"].astype("Int64"),
    "Cognome": vista["last_name"],
    "Nome": vista["first_name"],
    "Sesso": vista["sex"].map({True: "M", False: "F"}),
    "Data di nascita": vista["birth_date"],
    "E-Mail": vista["email"],
    "Attivo": ~vista["is_deleted"].astype(bool),
    "Gare": vista["n_gare"].astype("Int64"),
})
st.dataframe(
    tabella, use_container_width=True, hide_index=True,
    column_config={
        "Attivo": st.column_config.CheckboxColumn("Attivo", disabled=True),
        "Data di nascita": st.column_config.DateColumn("Data di nascita",
                                                       format="DD/MM/YYYY"),
        "Codice FIN": st.column_config.NumberColumn("Codice FIN", format="%d"),
        "Gare": st.column_config.NumberColumn("Gare", help="Gare individuali a DB"),
    },
)

# ── Azioni sulla riga ─────────────────────────────────────────────
st.markdown('<div class="section-title">Azioni</div>', unsafe_allow_html=True)

ids = vista["athlete_id"].astype(int).tolist()
etichette = {
    int(r["athlete_id"]): (f'{r["last_name"]} {r["first_name"]}'
                           f'{"" if not r["is_deleted"] else "  ·  inattivo"}')
    for _, r in vista.iterrows()
}
c_sel, c_mod, c_del = st.columns([4, 1.2, 1.4], vertical_alignment="bottom")
scelto = c_sel.selectbox("Atleta", options=ids, key="anag_sel",
                         format_func=lambda i: etichette.get(i, str(i)))
riga = atleti[atleti["athlete_id"] == scelto].iloc[0]
inattivo = bool(riga["is_deleted"])

if c_mod.button("Modifica", use_container_width=True):
    st.session_state["anag_mode"] = "modifica"
    st.session_state["anag_id"] = int(scelto)
    st.rerun()

if inattivo:
    if c_del.button("Riattiva", use_container_width=True, type="primary"):
        crud.riattiva_atleta(int(scelto))
        st.session_state["anag_msg"] = (
            f"{riga['last_name']} {riga['first_name']} e' di nuovo attivo.")
        st.rerun()
else:
    if c_del.button("Elimina", use_container_width=True):
        st.session_state["anag_conferma"] = int(scelto)
        st.rerun()

# ── Conferma disattivazione ───────────────────────────────────────
if st.session_state.get("anag_conferma") is not None:
    aid = int(st.session_state["anag_conferma"])
    r = atleti[atleti["athlete_id"] == aid]
    if r.empty:
        st.session_state["anag_conferma"] = None
    else:
        r = r.iloc[0]
        gare = int(r["n_gare"]) if pd.notna(r["n_gare"]) else 0
        st.warning(
            f"Confermi l'eliminazione di **{r['last_name']} {r['first_name']}**?  \n"
            f"L'atleta viene messo a non attivo, non cancellato: le sue "
            f"{gare} gare a database restano al loro posto e lo puoi riattivare "
            "quando vuoi."
        )
        c_ok, c_no = st.columns([1, 1])
        if c_ok.button("Sì, elimina", type="primary", use_container_width=True):
            crud.disattiva_atleta(aid)
            st.session_state["anag_conferma"] = None
            st.session_state["anag_msg"] = (
                f"{r['last_name']} {r['first_name']} e' ora inattivo.")
            st.rerun()
        if c_no.button("Annulla", use_container_width=True):
            st.session_state["anag_conferma"] = None
            st.rerun()
