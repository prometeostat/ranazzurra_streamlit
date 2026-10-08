"""
views/manifestazioni.py — Anagrafica manifestazioni, riservata all'admin.

Stesso schema dell'anagrafica atleti: elenco con filtro di stato, form di
inserimento e modifica, disattivazione morbida. "Elimina" non cancella la
riga, mette is_deleted = TRUE: alle manifestazioni sono appese le gare e i
risultati di tutti.

Serve soprattutto per il futuro: lo scraper porta a database solo le
manifestazioni gia' nuotate, quindi le prossime si inseriscono qui e da qui
finiscono in Agenda.
"""
from __future__ import annotations

import datetime as _dt

import pandas as pd
import streamlit as st

import auth
import crud
from views._common import page_header

STATI = ["Attive", "Disattivate", "Tutte"]
QUANDO = ["Tutte", "In programma", "Concluse"]
OGGI = _dt.date.today()

page_header("Anagrafica manifestazioni", "Calendario e dati di gara")

if not auth.is_admin():
    st.info("L'anagrafica e' riservata all'amministratore.")
    st.stop()

st.session_state.setdefault("man_mode", "lista")     # lista | nuovo | modifica
st.session_state.setdefault("man_id", None)
st.session_state.setdefault("man_conferma", None)
st.session_state.setdefault("gara_mode", None)       # None | nuova | id gara
st.session_state.setdefault("gara_conferma", None)


def _torna() -> None:
    st.session_state["man_mode"] = "lista"
    st.session_state["man_id"] = None
    st.session_state["man_conferma"] = None
    st.session_state["gara_mode"] = None
    st.session_state["gara_conferma"] = None


def _data(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, pd.Timestamp):
        return None if pd.isna(v) else v.date()
    return v


# ══════════════════════════════════════════════════════════════════
# Form
# ══════════════════════════════════════════════════════════════════

def _form(gara: dict | None) -> None:
    nuovo = gara is None
    titolo = "Nuova manifestazione" if nuovo else f"Modifica · {gara['nome']}"
    st.markdown(f'<div class="section-title">{titolo}</div>', unsafe_allow_html=True)
    if not nuovo:
        st.caption(f"ID {int(gara['comp_id'])} · assegnato dal database. "
                   f"{int(gara.get('n_gare') or 0)} gare collegate.")

    cronometraggi = crud.elenco_cronometraggi()

    with st.form("form_manifestazione"):
        nome = st.text_input("Nome *", value="" if nuovo else (gara["nome"] or ""),
                             max_chars=crud.MAX_NOME_GARA,
                             placeholder="es. 1ª Giornata Circuito Aquasport")

        c1, c2 = st.columns(2)
        inizio = c1.date_input("Data inizio *",
                               value=OGGI if nuovo else _data(gara.get("start_date")),
                               format="DD/MM/YYYY")
        fine = c2.date_input("Data fine",
                             value=OGGI if nuovo else _data(gara.get("end_date")),
                             format="DD/MM/YYYY")

        c3, c4 = st.columns(2)
        apertura = c3.date_input("Apertura iscrizioni",
                                 value=None if nuovo else _data(gara.get("open_registration_date")),
                                 format="DD/MM/YYYY")
        chiusura = c4.date_input("Chiusura iscrizioni",
                                 value=None if nuovo else _data(gara.get("close_registration_date")),
                                 format="DD/MM/YYYY")

        c5, c6 = st.columns(2)
        attuale = "" if nuovo else (gara.get("timing") or "")
        opzioni = [""] + sorted(set(cronometraggi) | ({attuale} if attuale else set()))
        timing = c5.selectbox("Cronometraggio", opzioni,
                              index=opzioni.index(attuale) if attuale in opzioni else 0,
                              format_func=lambda v: v or "—")
        massimo = gara.get("max_races_per_athlete") if not nuovo else None
        max_gare = c6.number_input("Max gare per atleta", min_value=0, max_value=20,
                                   value=int(massimo) if pd.notna(massimo) else 0,
                                   help="0 = non specificato.")

        sito = st.text_input("Link al sito", value="" if nuovo else (gara.get("website_link") or ""),
                             max_chars=crud.MAX_LINK,
                             placeholder="https://…")
        pdf = st.text_input("Link al programma PDF",
                            value="" if nuovo else (gara.get("pdf_link") or ""),
                            max_chars=crud.MAX_LINK, placeholder="https://…")

        ufficiale = st.checkbox(
            "Manifestazione ufficiale FIN",
            value=True if nuovo else bool(gara.get("is_fin", True)),
            help="Gara del calendario federale. Toglila per il circuito "
                 "Aquasport, le traversate in acque libere e le gare "
                 "sociali: i loro tempi restano a database ma si possono "
                 "escludere dai filtri di schede, classifiche e confronti.")

        b1, b2 = st.columns(2)
        salva = b1.form_submit_button("Salva", type="primary", use_container_width=True)
        annulla = b2.form_submit_button("Annulla", use_container_width=True)

    if annulla:
        _torna()
        st.rerun()
    if not salva:
        return

    dati = {
        "nome": nome, "start_date": inizio, "end_date": fine,
        "open_reg": apertura, "close_reg": chiusura, "timing": timing,
        "website_link": sito, "pdf_link": pdf,
        "max_races": int(max_gare) or None,
        "is_fin": bool(ufficiale),
    }
    errori = crud.valida_manifestazione(dati)
    if errori:
        for e in errori:
            st.error(e)
        return

    if nuovo:
        nuovo_id = crud.crea_manifestazione(dati)
        st.session_state["man_msg"] = f"Manifestazione creata con ID {nuovo_id}: {nome}."
    else:
        crud.aggiorna_manifestazione(int(gara["comp_id"]), dati)
        st.session_state["man_msg"] = f"Manifestazione aggiornata: {nome}."
    _torna()
    st.rerun()


# ══════════════════════════════════════════════════════════════════
# Gare della manifestazione
# ══════════════════════════════════════════════════════════════════
# Sta sotto al form di modifica, fuori dal form: dentro un st.form i
# bottoni non fanno rerun finche' non si invia, e qui invece ogni azione
# deve rispondere subito.

def _form_gara(comp_id: int, gara: dict | None, specialita: pd.DataFrame) -> None:
    nuova = gara is None
    st.markdown(f'<div class="section-title">'
                f'{"Nuova gara" if nuova else "Modifica gara"}</div>',
                unsafe_allow_html=True)

    ids = specialita["race_event_id"].astype(int).tolist()
    nomi = {int(r["race_event_id"]): str(r["etichetta"])
            for _, r in specialita.iterrows()}
    corrente = None if nuova else int(gara.get("race_event_id") or 0)

    with st.form("form_gara"):
        evento = st.selectbox(
            "Specialità *", options=ids,
            index=ids.index(corrente) if corrente in ids else 0,
            format_func=lambda i: nomi.get(i, str(i)),
            help="Sono le combinazioni di stile, distanza e staffetta già a "
                 "database: l'app non ne crea di nuove.")
        vasca = st.radio("Vasca *", crud.VASCHE, horizontal=True,
                         index=(crud.VASCHE.index(int(gara["pool_length"]))
                                if (not nuova and int(gara.get("pool_length") or 0)
                                    in crud.VASCHE) else 0),
                         format_func=lambda v: f"{v}m")
        nome = st.text_input(
            "Nome gara", value="" if nuova else (gara.get("name") or ""),
            max_chars=crud.MAX_NOME_PROVA,
            placeholder=nomi.get(evento, ""),
            help="Come sta sui risultati, per esempio \"50 Dorso - Assoluti "
                 "Maschi\". Lasciandolo vuoto prende il nome della specialità.")
        b1, b2 = st.columns(2)
        salva = b1.form_submit_button("Salva", type="primary",
                                      use_container_width=True)
        annulla = b2.form_submit_button("Annulla", use_container_width=True)

    if annulla:
        st.session_state["gara_mode"] = None
        st.rerun()
    if not salva:
        return

    dati = {"race_event_id": int(evento), "pool_length": int(vasca),
            "nome": (nome or "").strip() or nomi.get(int(evento), "")}
    errori = crud.valida_gara(dati)
    if errori:
        for e in errori:
            st.error(e)
        return

    if nuova:
        crud.crea_gara(int(comp_id), dati)
        st.session_state["gara_msg"] = f"Gara creata: {dati['nome']}."
    else:
        crud.aggiorna_gara(int(gara["race_id"]), dati)
        st.session_state["gara_msg"] = f"Gara aggiornata: {dati['nome']}."
    st.session_state["gara_mode"] = None
    st.rerun()


def _sezione_gare(comp_id: int) -> None:
    st.markdown('<div class="section-title">Gare</div>', unsafe_allow_html=True)

    msg = st.session_state.pop("gara_msg", None)
    if msg:
        st.success(msg)

    specialita = crud.elenco_specialita()
    if specialita.empty:
        st.warning("Nessuna specialità a database: non si possono creare gare.")
        return

    modo = st.session_state.get("gara_mode")
    gare = crud.gare_manifestazione(int(comp_id))

    if modo == "nuova":
        _form_gara(int(comp_id), None, specialita)
        return
    if modo is not None:
        riga = gare[gare["race_id"] == int(modo)]
        if riga.empty:
            st.session_state["gara_mode"] = None
            st.rerun()
        _form_gara(int(comp_id), riga.iloc[0].to_dict(), specialita)
        return

    if st.button("＋  Nuova gara", use_container_width=True, key="gara_nuova"):
        st.session_state["gara_mode"] = "nuova"
        st.rerun()

    if gare.empty:
        st.info("Nessuna gara in questa manifestazione. Creala qui sopra e poi "
                "carica i tempi da Gestione, Inserisci tempi.")
        return

    st.dataframe(
        pd.DataFrame({
            "Gara": gare["name"].fillna(gare["etichetta"]),
            "Specialità": gare["etichetta"],
            "Vasca": gare["pool_length"].map(lambda v: f"{int(v)}m"
                                             if pd.notna(v) else "—"),
            "Iscritti": gare["iscritti"].astype("Int64"),
            "Con tempo": gare["con_tempo"].astype("Int64"),
        }),
        use_container_width=True, hide_index=True,
    )

    ids = gare["race_id"].astype(int).tolist()
    etich = {int(r["race_id"]): (f'{r["name"] or r["etichetta"]} · '
                                f'{int(r["pool_length"])}m · '
                                f'{int(r["iscritti"])} iscritti')
             for _, r in gare.iterrows()}
    c1, c2, c3 = st.columns([4, 1.2, 1.2], vertical_alignment="bottom")
    scelta = c1.selectbox("Gara", options=ids, key="gara_sel",
                          format_func=lambda i: etich.get(i, str(i)))
    if c2.button("Modifica", use_container_width=True, key="gara_mod"):
        st.session_state["gara_mode"] = int(scelta)
        st.rerun()
    if c3.button("Elimina", use_container_width=True, key="gara_del"):
        st.session_state["gara_conferma"] = int(scelta)
        st.rerun()

    if st.button("⏱  Inserisci i tempi di questa gara", use_container_width=True,
                 key="gara_tempi"):
        st.session_state["tempi_comp"] = int(comp_id)
        st.session_state["tempi_race"] = int(scelta)
        st.switch_page("views/tempi.py")

    if st.session_state.get("gara_conferma") is not None:
        rid = int(st.session_state["gara_conferma"])
        r = gare[gare["race_id"] == rid]
        if r.empty:
            st.session_state["gara_conferma"] = None
        else:
            r = r.iloc[0]
            n = int(r["iscritti"] or 0)
            if n:
                st.warning(f"**{r['name'] or r['etichetta']}** ha {n} iscritti. "
                           "Prima togli i tempi da Inserisci tempi, poi la gara "
                           "si elimina.")
                if st.button("Ho capito", use_container_width=True,
                             key="gara_ok_bloccata"):
                    st.session_state["gara_conferma"] = None
                    st.rerun()
            else:
                st.warning(f"Confermi l'eliminazione di "
                           f"**{r['name'] or r['etichetta']}**? La gara viene "
                           "messa a non attiva, non cancellata.")
                c_ok, c_no = st.columns(2)
                if c_ok.button("Sì, elimina", type="primary",
                               use_container_width=True, key="gara_ok"):
                    fatto, testo = crud.elimina_gara(rid)
                    st.session_state["gara_conferma"] = None
                    st.session_state["gara_msg"] = testo
                    st.rerun()
                if c_no.button("Annulla", use_container_width=True,
                               key="gara_no"):
                    st.session_state["gara_conferma"] = None
                    st.rerun()


# ══════════════════════════════════════════════════════════════════
# Elenco
# ══════════════════════════════════════════════════════════════════

manif = crud.elenco_manifestazioni()
if manif.empty:
    st.warning("Nessuna manifestazione a database.")
    st.stop()

_msg = st.session_state.pop("man_msg", None)
if _msg:
    st.success(_msg)

modo = st.session_state["man_mode"]
if modo == "nuovo":
    _form(None)
    st.stop()
if modo == "modifica":
    riga = manif[manif["comp_id"] == st.session_state["man_id"]]
    if riga.empty:
        _torna()
        st.rerun()
    dati_manif = riga.iloc[0].to_dict()
    _form(dati_manif)
    _sezione_gare(int(dati_manif["comp_id"]))
    st.stop()

c_new, c_stato = st.columns([1.4, 3], vertical_alignment="bottom")
if c_new.button("＋  Nuova", type="primary", use_container_width=True):
    st.session_state["man_mode"] = "nuovo"
    st.rerun()
stato = c_stato.radio("Stato", STATI, horizontal=True, key="man_stato")

c_quando, c_cerca = st.columns([3, 3], vertical_alignment="bottom")
quando = c_quando.radio("Quando", QUANDO, horizontal=True, key="man_quando")
cerca = c_cerca.text_input("Cerca", placeholder="Nome manifestazione…", key="man_cerca")

vista = manif.copy()
vista["start_date"] = pd.to_datetime(vista["start_date"])
if stato == "Attive":
    vista = vista[vista["is_deleted"] == False]      # noqa: E712
elif stato == "Disattivate":
    vista = vista[vista["is_deleted"] == True]       # noqa: E712
if quando == "In programma":
    vista = vista[vista["start_date"].dt.date >= OGGI]
elif quando == "Concluse":
    vista = vista[vista["start_date"].dt.date < OGGI]
if cerca.strip():
    vista = vista[vista["nome"].fillna("").str.lower()
                  .str.contains(cerca.strip().lower(), na=False)]

st.caption(f"{len(vista)} manifestazioni su {len(manif)} a database.")
if vista.empty:
    st.info("Nessuna manifestazione con questi filtri.")
    st.stop()

tabella = pd.DataFrame({
    "ID": vista["comp_id"].astype(int),
    "Nome": vista["nome"],
    "Inizio": vista["start_date"],
    "Fine": pd.to_datetime(vista["end_date"]),
    "Chiusura iscr.": pd.to_datetime(vista["close_registration_date"]),
    "Cronometraggio": vista["timing"],
    "Gare": vista["n_gare"].astype("Int64"),
    "FIN": vista["is_fin"].astype(bool),
    "Attiva": ~vista["is_deleted"].astype(bool),
})
st.dataframe(
    tabella, use_container_width=True, hide_index=True,
    column_config={
        "FIN": st.column_config.CheckboxColumn(
            "FIN", disabled=True,
            help="Manifestazione ufficiale del calendario federale."),
        "Attiva": st.column_config.CheckboxColumn("Attiva", disabled=True),
        "Inizio": st.column_config.DateColumn("Inizio", format="DD/MM/YYYY"),
        "Fine": st.column_config.DateColumn("Fine", format="DD/MM/YYYY"),
        "Chiusura iscr.": st.column_config.DateColumn("Chiusura iscr.",
                                                      format="DD/MM/YYYY"),
    },
)

st.markdown('<div class="section-title">Azioni</div>', unsafe_allow_html=True)
ids = vista["comp_id"].astype(int).tolist()
etichette = {
    int(r["comp_id"]): (f'{pd.to_datetime(r["start_date"]).strftime("%d/%m/%Y")} · '
                        f'{r["nome"]}{"" if not r["is_deleted"] else "  ·  disattivata"}')
    for _, r in vista.iterrows()
}
c_sel, c_mod, c_del = st.columns([4, 1.2, 1.4], vertical_alignment="bottom")
scelta = c_sel.selectbox("Manifestazione", options=ids, key="man_sel",
                         format_func=lambda i: etichette.get(i, str(i)))
riga = manif[manif["comp_id"] == scelta].iloc[0]
disattivata = bool(riga["is_deleted"])

if c_mod.button("Modifica", use_container_width=True):
    st.session_state["man_mode"] = "modifica"
    st.session_state["man_id"] = int(scelta)
    st.rerun()

if disattivata:
    if c_del.button("Riattiva", type="primary", use_container_width=True):
        crud.riattiva_manifestazione(int(scelta))
        st.session_state["man_msg"] = f"{riga['nome']} e' di nuovo attiva."
        st.rerun()
else:
    if c_del.button("Elimina", use_container_width=True):
        st.session_state["man_conferma"] = int(scelta)
        st.rerun()

if st.session_state.get("man_conferma") is not None:
    cid = int(st.session_state["man_conferma"])
    r = manif[manif["comp_id"] == cid]
    if r.empty:
        st.session_state["man_conferma"] = None
    else:
        r = r.iloc[0]
        gare = int(r["n_gare"]) if pd.notna(r["n_gare"]) else 0
        st.warning(
            f"Confermi l'eliminazione di **{r['nome']}**?  \n"
            f"Viene messa a non attiva, non cancellata: le {gare} gare collegate "
            "restano a database, ma spariscono da agenda, schede e classifiche "
            "finche' non la riattivi."
        )
        c_ok, c_no = st.columns(2)
        if c_ok.button("Sì, elimina", type="primary", use_container_width=True):
            crud.disattiva_manifestazione(cid)
            st.session_state["man_conferma"] = None
            st.session_state["man_msg"] = f"{r['nome']} e' ora disattivata."
            st.rerun()
        if c_no.button("Annulla", use_container_width=True):
            st.session_state["man_conferma"] = None
            st.rerun()
