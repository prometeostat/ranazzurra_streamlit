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

def _form_clona(elenco: pd.DataFrame) -> None:
    """
    Copia di un'edizione passata: intestazione piu' programma gare.

    La manifestazione da cui partire si sceglie qui dentro, non dall'elenco:
    quasi sempre e' quella dell'anno scorso, che con i filtri attivi
    potrebbe non essere nemmeno a video.
    """
    st.markdown('<div class="section-title">Clona manifestazione</div>',
                unsafe_allow_html=True)

    sorgenti = elenco.copy()
    sorgenti["start_date"] = pd.to_datetime(sorgenti["start_date"], errors="coerce")
    sorgenti = sorgenti.sort_values("start_date", ascending=False)
    ids = sorgenti["comp_id"].astype(int).tolist()
    etichette = {int(r["comp_id"]): _etichetta(r) for _, r in sorgenti.iterrows()}

    src = st.selectbox("Manifestazione da clonare", options=ids, key="man_src",
                       format_func=lambda i: etichette.get(i, str(i)),
                       help="Si copiano nome, date, cronometraggio e programma "
                            "gare. I risultati no: restano all'edizione vecchia.")
    base = elenco[elenco["comp_id"] == src].iloc[0].to_dict()
    gare_src = crud.gare_manifestazione(int(src))
    specialita = crud.elenco_specialita()
    if specialita.empty:
        st.warning("Nessuna specialità a database: non si possono creare gare.")
        return

    tipi = specialita["etichetta"].astype(str).tolist()
    per_etichetta = {str(r["etichetta"]): int(r["race_event_id"])
                     for _, r in specialita.iterrows()}

    st.caption(f"ID {int(src)} · {len(gare_src)} gare nel programma. Le date "
               "arrivano gia' spostate di un anno, i link no: quelli puntano "
               "all'edizione vecchia. Fascia oraria e ordine delle gare si "
               "copiano, la giornata no: si rimette dopo, dal Programma.")

    if gare_src.empty:
        righe_gare = pd.DataFrame({"Copia": pd.Series(dtype=bool),
                                   "Gara": pd.Series(dtype=str),
                                   "Vasca": pd.Series(dtype="Int64"),
                                   "Specialità": pd.Series(dtype=str),
                                   "_fascia": pd.Series(dtype="Int64"),
                                   "_ordine": pd.Series(dtype="Int64")})
    else:
        righe_gare = pd.DataFrame({
            "Copia": True,
            "Gara": gare_src["name"].fillna(gare_src["etichetta"]).astype(str),
            "Vasca": gare_src["pool_length"].astype("Int64"),
            "Specialità": gare_src["etichetta"].astype(str),
            # Non si editano qui, viaggiano con la riga: fascia e ordine sono
            # relativi e restano buoni, la giornata no perche' le date
            # cambiano e si rimette dalla griglia del programma.
            "_fascia": gare_src["session"],
            "_ordine": gare_src["race_order"],
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

        ufficiale = st.checkbox(
            "Manifestazione ufficiale FIN",
            value=bool(base.get("is_fin", True)),
            help="Arriva dall'edizione di partenza: si cambia solo se la "
                 "nuova edizione cambia calendario.")

        st.markdown("**Programma gare**")
        modificate = st.data_editor(
            righe_gare, key=f"man_clona_gare_{int(src)}", hide_index=True,
            use_container_width=True, num_rows="fixed",
            column_config={
                "Copia": st.column_config.CheckboxColumn(
                    "Copia", help="Togli la spunta alle gare che non si fanno."),
                "Gara": st.column_config.TextColumn(
                    "Gara", width="large", max_chars=crud.MAX_NOME_PROVA),
                "Vasca": st.column_config.SelectboxColumn(
                    "Vasca", options=crud.VASCHE, width="small"),
                "Specialità": st.column_config.SelectboxColumn(
                    "Specialità", options=tipi, width="medium"),
                "_fascia": None,
                "_ordine": None,
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
        "is_fin": bool(ufficiale),
        "organizer_company_id": organizzatore or None,
    }
    errori = crud.valida_manifestazione(dati)
    if errori:
        for e in errori:
            st.error(e)
        return

    scelte, scartate = [], 0
    for r in modificate.to_dict("records"):
        if not _vero(r.get("Copia")):
            continue
        riga = {
            "nome": _pulito(r.get("Gara")).strip(),
            "pool_length": _numero(r.get("Vasca")),
            "race_event_id": per_etichetta.get(_pulito(r.get("Specialità"))),
            "session": _numero(r.get("_fascia")),
            "race_order": _numero(r.get("_ordine")),
        }
        if (not riga["nome"] or not riga["race_event_id"]
                or riga["pool_length"] not in crud.VASCHE):
            scartate += 1
            continue
        scelte.append(riga)

    if scartate:
        st.error(f"{scartate} righe non hanno nome, specialità o vasca valida: "
                 "sistemale o togli la spunta a Copia.")
        return

    nuovo_id, fatte = crud.clona_manifestazione(dati, scelte)
    if nuovo_id < 0:
        st.error("La manifestazione non e' stata creata: riprova.")
        return
    st.session_state["man_msg"] = (
        f"Copiata da «{base.get('nome')}»: nuova manifestazione ID {nuovo_id} "
        f"({nome}) con {fatte} gar{'a' if fatte == 1 else 'e'}. "
        "Nessun risultato e' stato duplicato.")
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
    # Il programma (giornata, fascia, ordine) si tocca dalla griglia qui
    # sotto, non da questo form: qui va ricopiato com'e', se no salvando il
    # nome di una gara si azzererebbe il suo posto nel programma.
    if not nuova:
        dati.update({"race_date": _data(gara.get("race_date")),
                     "session": gara.get("session"),
                     "race_order": gara.get("race_order")})
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


SENZA_FASCIA = "—"


def _griglia_programma(comp_id: int, gare: pd.DataFrame) -> None:
    """
    Il programma di tutta la manifestazione in una griglia sola.

    Giornata, fascia e numero d'ordine si sistemano riga per riga e si
    salvano insieme: con trenta gare aprire trenta form non ha senso. Il
    salvataggio tocca solo queste tre colonne, nome, vasca e specialita'
    restano quelle del form della singola gara.
    """
    with st.expander("Programma: giornate, fasce e ordine"):
        st.caption("Le gare si susseguono per giornata e per fascia oraria: "
                   "mattino, pomeriggio, sera. Il numero e' l'ordine dentro "
                   "la fascia. Si puo' lasciare vuoto: le gare senza "
                   "programma finiscono in fondo agli elenchi, ordinate come "
                   "sempre per stile e distanza.")

        tabella = pd.DataFrame({
            "race_id": gare["race_id"].astype(int),
            "Gara": gare["name"].fillna(gare["etichetta"]).astype(str),
            "Giornata": pd.to_datetime(gare["race_date"], errors="coerce"),
            "Fascia": gare["session"].map(
                lambda v: crud.SESSIONI.get(int(v), SENZA_FASCIA)
                if pd.notna(v) else SENZA_FASCIA),
            "N.": pd.to_numeric(gare["race_order"],
                                errors="coerce").astype("Int64"),
        })

        modificate = st.data_editor(
            tabella, key=f"prog_{comp_id}", hide_index=True,
            use_container_width=True, num_rows="fixed",
            column_config={
                "race_id": None,     # nascosta: serve solo per il salvataggio
                "Gara": st.column_config.TextColumn("Gara", disabled=True,
                                                    width="large"),
                "Giornata": st.column_config.DateColumn(
                    "Giornata", format="DD/MM/YYYY",
                    help="Il giorno in cui si nuota, dentro le date della "
                         "manifestazione."),
                "Fascia": st.column_config.SelectboxColumn(
                    "Fascia", width="medium",
                    options=[SENZA_FASCIA] + list(crud.SESSIONI.values())),
                "N.": st.column_config.NumberColumn(
                    "N.", min_value=1, max_value=999, step=1, format="%d",
                    help="Ordine dentro la fascia. Vuoto = non indicato."),
            },
        )

        if st.button("Salva il programma", type="primary",
                     use_container_width=True, key=f"prog_salva_{comp_id}"):
            righe = []
            for r in modificate.to_dict("records"):
                fascia = _pulito(r.get("Fascia"), SENZA_FASCIA)
                righe.append({
                    "race_id": _numero(r.get("race_id")),
                    "race_date": r.get("Giornata"),
                    "session": None if fascia == SENZA_FASCIA else fascia,
                    "race_order": _numero(r.get("N.")),
                })
            fatte, errori = crud.salva_programma(int(comp_id), righe)
            if errori:
                for e in errori:
                    st.error(e)
                return
            st.session_state["gara_msg"] = (
                f"Programma salvato: {fatte} gar{'a' if fatte == 1 else 'e'} "
                "aggiornate.")
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
            # Testo e non colonne tipizzate: una data vuota in una DateColumn
            # si legge "None", e qui le celle vuote sono la norma.
            "Giornata": pd.to_datetime(gare["race_date"], errors="coerce").map(
                lambda v: v.strftime("%d/%m/%Y") if pd.notna(v) else "—"),
            "Fascia": gare["session"].map(
                lambda v: crud.SESSIONI.get(int(v), "—")
                if pd.notna(v) else "—"),
            "N.": gare["race_order"].map(
                lambda v: str(int(v)) if pd.notna(v) else "—"),
            "Iscritti": gare["iscritti"].astype("Int64"),
            "Con tempo": gare["con_tempo"].astype("Int64"),
        }),
        use_container_width=True, hide_index=True,
        column_config={
            "N.": st.column_config.TextColumn(
                "N.", help="Numero di programma dentro la fascia oraria."),
        },
    )

    _griglia_programma(int(comp_id), gare)

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
if modo == "clona":
    _form_clona(manif)
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
etichette = {int(r["comp_id"]): _etichetta(r) for _, r in vista.iterrows()}
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
