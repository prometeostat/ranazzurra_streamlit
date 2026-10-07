"""
views/manifestazioni.py — Anagrafica manifestazioni, riservata all'admin.

Stesso schema dell'anagrafica atleti: elenco con filtro di stato, form di
inserimento e modifica, disattivazione morbida. "Elimina" non cancella la
riga, mette is_deleted = TRUE: alle manifestazioni sono appese le gare e i
risultati di tutti.

Serve soprattutto per il futuro: lo scraper porta a database solo le
manifestazioni gia' nuotate, quindi le prossime si inseriscono qui e da qui
finiscono in Agenda.

"Clona" ricopia un'edizione passata con il suo programma gare: si sceglie la
manifestazione da cui partire, le date arrivano gia' spostate di un anno e
l'elenco delle gare si corregge riga per riga prima di salvare. Si copia solo
la struttura, mai i risultati: i tempi restano attaccati all'edizione in cui
sono stati nuotati.
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

# lista | nuovo | modifica | clona
st.session_state.setdefault("man_mode", "lista")
st.session_state.setdefault("man_id", None)
st.session_state.setdefault("man_conferma", None)


def _torna() -> None:
    st.session_state["man_mode"] = "lista"
    st.session_state["man_id"] = None
    st.session_state["man_conferma"] = None


def _data(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, pd.Timestamp):
        return None if pd.isna(v) else v.date()
    return v


def _anno_dopo(v):
    """La stessa data dell'anno prossimo. Il 29 febbraio diventa il 28."""
    d = _data(v)
    if d is None:
        return None
    try:
        return d.replace(year=d.year + 1)
    except ValueError:
        return d.replace(year=d.year + 1, day=28)


def _vero(v) -> bool:
    """
    True solo se il valore e' davvero acceso. I valori che tornano da un
    data_editor possono essere pd.NA, che non si puo' valutare come
    booleano: va intercettato prima del bool().
    """
    try:
        if v is None or pd.isna(v):
            return False
    except (TypeError, ValueError):
        return False
    return bool(v)


def _pulito(v, vuoto: str = "") -> str:
    """Stringa utilizzabile, con la stessa prudenza su pd.NA."""
    try:
        if v is None or pd.isna(v):
            return vuoto
    except (TypeError, ValueError):
        return vuoto
    return str(v)


def _numero(v) -> int | None:
    """Intero oppure None, pd.NA compreso."""
    try:
        if v is None or pd.isna(v):
            return None
    except (TypeError, ValueError):
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


SENZA_SOCIETA = 0


def _tendina_societa(dove, corrente, nome_corrente: str = "", chiave=None):
    """
    Tendina dell'organizzatore, con lo zero che fa da "non indicato":
    organizer_company_id accetta NULL e buona parte delle manifestazioni
    storiche ce l'ha davvero vuoto, quindi obbligare a scegliere qualcuno
    sarebbe peggio del campo vuoto.

    Se la societa' agganciata non e' piu' nell'elenco, perche' disattivata o
    senza nome, resta comunque in tendina marcata come fuori elenco: salvando
    la manifestazione non si perde un riferimento buono.
    """
    societa = crud.elenco_societa()
    nomi: dict[int, str] = {}
    if not societa.empty:
        nomi = {int(r["company_id"]): str(r["name"]).strip()
                for _, r in societa.iterrows()}

    cid = _numero(corrente) or SENZA_SOCIETA
    if cid and cid not in nomi:
        etichetta = _pulito(nome_corrente).strip() or f"societa' {cid}"
        nomi[cid] = f"{etichetta}  ·  fuori elenco"

    opzioni = [SENZA_SOCIETA] + sorted(nomi, key=lambda i: nomi[i].lower())
    argomenti = {"key": chiave} if chiave else {}
    return dove.selectbox(
        "Organizzatore", opzioni,
        index=opzioni.index(cid) if cid in opzioni else 0,
        format_func=lambda i: "—" if i == SENZA_SOCIETA else nomi.get(i, str(i)),
        help="La societa' che organizza. Finisce in Agenda sotto il nome "
             "della manifestazione.",
        **argomenti)


def _etichetta(r: dict | pd.Series) -> str:
    quando = pd.to_datetime(r.get("start_date"), errors="coerce")
    giorno = "—" if pd.isna(quando) else quando.strftime("%d/%m/%Y")
    coda = "  ·  disattivata" if _vero(r.get("is_deleted")) else ""
    return f'{giorno} · {_pulito(r.get("nome"), "Manifestazione")}{coda}'


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

        organizzatore = _tendina_societa(
            st, None if nuovo else gara.get("organizer_company_id"),
            "" if nuovo else _pulito(gara.get("organizzatore")))

        sito = st.text_input("Link al sito", value="" if nuovo else (gara.get("website_link") or ""),
                             max_chars=crud.MAX_LINK,
                             placeholder="https://…")
        pdf = st.text_input("Link al programma PDF",
                            value="" if nuovo else (gara.get("pdf_link") or ""),
                            max_chars=crud.MAX_LINK, placeholder="https://…")

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
        "organizer_company_id": organizzatore or None,
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
# Clonazione
# ══════════════════════════════════════════════════════════════════
SENZA_TIPO = "—"


def _form_clona() -> None:
    """
    Copia di un'edizione passata: intestazione piu' programma gare.

    La manifestazione da cui partire si sceglie qui dentro, non dall'elenco:
    quasi sempre e' quella dell'anno scorso, che con i filtri attivi
    potrebbe non essere nemmeno a video.
    """
    st.markdown('<div class="section-title">Clona manifestazione</div>',
                unsafe_allow_html=True)

    sorgenti = manif.copy()
    sorgenti["start_date"] = pd.to_datetime(sorgenti["start_date"], errors="coerce")
    sorgenti = sorgenti.sort_values("start_date", ascending=False)
    ids = sorgenti["comp_id"].astype(int).tolist()
    etichette = {int(r["comp_id"]): _etichetta(r) for _, r in sorgenti.iterrows()}

    src = st.selectbox("Manifestazione da clonare", options=ids, key="man_src",
                       format_func=lambda i: etichette.get(i, str(i)),
                       help="Si copiano nome, date, cronometraggio e programma "
                            "gare. I risultati no: restano all'edizione vecchia.")
    base = manif[manif["comp_id"] == src].iloc[0].to_dict()
    gare_src = crud.gare_di_manifestazione(int(src))
    eventi = crud.elenco_eventi_gara()

    tipi = [SENZA_TIPO] + ([] if eventi.empty else eventi["evento"].tolist())
    per_id = {} if eventi.empty else dict(zip(eventi["evento"], eventi["id"]))

    st.caption(f"ID {int(src)} · {len(gare_src)} gare nel programma. Le date "
               "arrivano gia' spostate di un anno, i link no: quelli puntano "
               "all'edizione vecchia.")

    if gare_src.empty:
        righe_gare = pd.DataFrame({"Copia": pd.Series(dtype=bool),
                                   "Gara": pd.Series(dtype=str),
                                   "Vasca": pd.Series(dtype="Int64"),
                                   "Tipo": pd.Series(dtype=str)})
    else:
        righe_gare = pd.DataFrame({
            "Copia": True,
            "Gara": gare_src["nome"].fillna("").astype(str),
            "Vasca": gare_src["pool_length"].astype("Int64"),
            "Tipo": gare_src["evento"].fillna(SENZA_TIPO).astype(str),
        })

    cronometraggi = crud.elenco_cronometraggi()

    with st.form("form_clona_manifestazione"):
        nome = st.text_input("Nome *", value=str(base.get("nome") or ""),
                             max_chars=crud.MAX_NOME_GARA,
                             help="Di solito cambia solo il numero di edizione.")

        c1, c2 = st.columns(2)
        inizio = c1.date_input("Data inizio *", value=_anno_dopo(base.get("start_date")),
                               format="DD/MM/YYYY")
        fine = c2.date_input("Data fine", value=_anno_dopo(base.get("end_date")),
                             format="DD/MM/YYYY")

        c3, c4 = st.columns(2)
        apertura = c3.date_input("Apertura iscrizioni",
                                 value=_anno_dopo(base.get("open_registration_date")),
                                 format="DD/MM/YYYY")
        chiusura = c4.date_input("Chiusura iscrizioni",
                                 value=_anno_dopo(base.get("close_registration_date")),
                                 format="DD/MM/YYYY")

        c5, c6 = st.columns(2)
        attuale = base.get("timing") or ""
        opzioni = [""] + sorted(set(cronometraggi) | ({attuale} if attuale else set()))
        timing = c5.selectbox("Cronometraggio", opzioni,
                              index=opzioni.index(attuale) if attuale in opzioni else 0,
                              format_func=lambda v: v or "—")
        massimo = base.get("max_races_per_athlete")
        max_gare = c6.number_input("Max gare per atleta", min_value=0, max_value=20,
                                   value=int(massimo) if pd.notna(massimo) else 0,
                                   help="0 = non specificato.")

        organizzatore = _tendina_societa(
            st, base.get("organizer_company_id"),
            _pulito(base.get("organizzatore")), chiave=f"man_clona_org_{int(src)}")

        sito = st.text_input("Link al sito", value="", max_chars=crud.MAX_LINK,
                             placeholder="https://…")
        pdf = st.text_input("Link al programma PDF", value="",
                            max_chars=crud.MAX_LINK, placeholder="https://…")

        st.markdown("**Programma gare**")
        modificate = st.data_editor(
            righe_gare, key=f"man_clona_gare_{int(src)}", hide_index=True,
            use_container_width=True, num_rows="fixed",
            column_config={
                "Copia": st.column_config.CheckboxColumn(
                    "Copia", help="Togli la spunta alle gare che non si fanno."),
                "Gara": st.column_config.TextColumn("Gara", width="large"),
                "Vasca": st.column_config.NumberColumn("Vasca", min_value=0,
                                                       max_value=5000, step=25,
                                                       format="%d m"),
                "Tipo": st.column_config.SelectboxColumn("Tipo", options=tipi,
                                                         width="medium"),
            },
        )

        b1, b2 = st.columns(2)
        salva = b1.form_submit_button("Crea la copia", type="primary",
                                      use_container_width=True)
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
        "organizer_company_id": organizzatore or None,
    }
    errori = crud.valida_manifestazione(dati)
    if errori:
        for e in errori:
            st.error(e)
        return

    scelte = []
    for r in modificate.to_dict("records"):
        if not _vero(r.get("Copia")):
            continue
        tipo = r.get("Tipo")
        scelte.append({
            "nome": r.get("Gara"),
            "pool_length": r.get("Vasca"),
            "race_event_id": per_id.get(_pulito(tipo, SENZA_TIPO)),
        })

    nuovo_id, fatte = crud.clona_manifestazione(dati, scelte)
    if nuovo_id < 0:
        st.error("La manifestazione non e' stata creata: nessuna gara copiata.")
        return
    st.session_state["man_msg"] = (
        f"Copiata da «{base.get('nome')}»: nuova manifestazione ID {nuovo_id} "
        f"({nome}) con {fatte} gar{'a' if fatte == 1 else 'e'}. "
        "Nessun risultato e' stato duplicato.")
    _torna()
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
    _form(riga.iloc[0].to_dict())
    st.stop()
if modo == "clona":
    _form_clona()
    st.stop()

c_new, c_clona, c_stato = st.columns([1.3, 1.3, 3], vertical_alignment="bottom")
if c_new.button("＋  Nuova", type="primary", use_container_width=True):
    st.session_state["man_mode"] = "nuovo"
    st.rerun()
if c_clona.button("⧉  Clona", use_container_width=True,
                  help="Parti da un'edizione passata e portati dietro il "
                       "programma gare."):
    st.session_state["man_mode"] = "clona"
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
    "Organizzatore": vista["organizzatore"].fillna("—"),
    "Cronometraggio": vista["timing"],
    "Gare": vista["n_gare"].astype("Int64"),
    "Attiva": ~vista["is_deleted"].astype(bool),
})
st.dataframe(
    tabella, use_container_width=True, hide_index=True,
    column_config={
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
