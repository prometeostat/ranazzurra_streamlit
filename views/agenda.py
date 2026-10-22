"""
views/agenda.py — calendario delle manifestazioni.

A database ci sono solo le manifestazioni dove abbiamo gareggiato, perche'
arrivano dallo scraper dei risultati: il passato e' pieno, il futuro si
popola a mano dall'Anagrafica manifestazioni.
"""
from __future__ import annotations

import datetime as _dt
import html

import pandas as pd
import streamlit as st

import auth
import crud
import data
import season as season_mod
from views._common import (apply_fin, inline_filters, page_header,
                           season_year)

OGGI = _dt.date.today()

# Quanto lontano guarda "In programma". Oltre questa soglia le manifestazioni
# restano a database e si trovano con la ricerca, ma non affollano la lista:
# a sei mesi di distanza non c'e' niente da decidere. 75 giorni coprono con
# margine l'apertura delle iscrizioni, che sulle gare a calendario parte fra
# i 50 e i 65 giorni prima della gara.
ORIZZONTE = 75

page_header("Agenda", "Calendario manifestazioni")


def fascia_pre_iscrizione() -> None:
    """
    La scadenza della prossima pre-iscrizione, in cima a tutto.

    Non e' il limite tecnico delle iscrizioni, che e' il giorno prima della
    chiusura ufficiale: e' il giorno prima dell'**apertura**, quando gli
    allenatori devono avere le adesioni in mano per portarle sul portale
    federale. Chi arriva dopo puo' ancora pre-iscriversi dall'app, ma
    rischia che l'iscrizione vera sia gia' partita, ed e' per questo che la
    fascia dice tutte e due le date invece di una sola.

    Sta prima dei filtri e prima di qualunque `st.stop()` della pagina:
    deve vedersi sempre, anche quando il periodo scelto non ha niente
    dentro.
    """
    io = auth.current_user() or {}
    if io.get("athlete_id") is None:
        return
    s = crud.prossimo_sollecito(int(io["athlete_id"]))
    if not s:
        return

    quando = (s["sollecito"].strftime("%d/%m/%Y") if s["sollecito"] else "—")
    ultimo = (s["ultimo_giorno"].strftime("%d/%m/%Y")
              if s["ultimo_giorno"] else None)
    gara = (f'{s["nome"]}, {s["start_date"].strftime("%d/%m")}'
            if s["start_date"] else s["nome"])

    if s["mie_gare"]:
        # Etichetta corta: con una lunga la data va a capo e la fascia
        # perde il colpo d'occhio.
        stile, etichetta = "fatta", "Puoi cambiare fino al"
        coda = (f'{s["mie_gare"]} gar{"a" if s["mie_gare"] == 1 else "e"} '
                "gia' scelte" if s["mie_gare"] != 1 else "1 gara gia' scelta")
        quando = ultimo or quando
        sotto = (f'{gara}. Hai gia\' dato le tue gare: fino al {ultimo} puoi '
                 'aggiungerne, toglierne o cambiare i tempi da Modifica.'
                 if ultimo else gara)
    else:
        giorni = s["giorni"]
        urgente = s["scaduto"] or giorni <= crud.GIORNI_SOLLECITO_ROSSO
        stile = "urgente" if urgente else ""
        etichetta = "Pre-iscrizione entro il"
        if s["scaduto"]:
            coda = "scaduta"
        elif giorni == 0:
            coda = "oggi e' l'ultimo giorno"
        elif giorni == 1:
            coda = "manca 1 giorno"
        else:
            coda = f"mancano {giorni} giorni"
        if s["scaduto"]:
            sotto = (f'{gara}. Il termine per la squadra e\' passato: il '
                     f'modulo resta aperto fino al {ultimo}, ma l\'iscrizione '
                     'vera potrebbe essere gia\' partita. Avvisa i coach.'
                     if ultimo else f'{gara}. Il termine e\' passato: avvisa i coach.')
        else:
            sotto = (f'{gara}. Il {s["apertura"].strftime("%d/%m")} la squadra '
                     'porta le adesioni sul portale federale, quindi servono '
                     f'prima. Dopo puoi ancora cambiare qui fino al {ultimo}.'
                     if ultimo else gara)

    st.html(
        f'<div class="isc-scadenza {stile}">'
        f'<span class="isc-scadenza-lbl">{html.escape(etichetta)}</span>'
        f'<span class="isc-scadenza-data">{quando}</span>'
        f'<span class="isc-scadenza-coda">{html.escape(coda)}</span></div>')
    st.caption(sotto)

    if not auth.sola_lettura():
        if st.button("📝  Vai alla pre-iscrizione", type="primary",
                     use_container_width=True, key="sollecito_vai"):
            st.session_state["isc_comp"] = s["comp_id"]
            st.switch_page("views/iscrizioni_nuove.py")


fascia_pre_iscrizione()
inline_filters("agenda", pool=False)

sy = season_year()
manif = apply_fin(data.load_agenda(sy)).copy()

cerca = st.text_input("Cerca manifestazione", placeholder="Nome, citta', organizzatore…",
                      label_visibility="collapsed", key="agenda_cerca")
sta_cercando = bool(cerca.strip())
if sta_cercando and not manif.empty:
    k = cerca.strip().lower()
    testo = (manif["nome"].fillna("") + " " + manif["organizzatore"].fillna(""))
    manif = manif[testo.str.lower().str.contains(k, na=False)]

if manif.empty:
    st.info("Nessuna manifestazione nel periodo selezionato.")
    st.stop()

manif["start_date"] = pd.to_datetime(manif["start_date"])
manif["end_date"] = pd.to_datetime(manif["end_date"])


def _intervallo(r: dict) -> str:
    inizio = r["start_date"]
    fine = r["end_date"]
    if pd.isna(fine) or fine.date() == inizio.date():
        return inizio.strftime("%d/%m/%Y")
    if fine.month == inizio.month and fine.year == inizio.year:
        return f"{inizio.strftime('%d')}–{fine.strftime('%d/%m/%Y')}"
    return f"{inizio.strftime('%d/%m')} – {fine.strftime('%d/%m/%Y')}"


def _vasche(v) -> str:
    """Le gare di fondo hanno pool_length uguale alla distanza."""
    if not v or (isinstance(v, float) and pd.isna(v)):
        return ""
    piscina = [x for x in str(v).split("/") if x in ("25", "50")]
    fondo = [x for x in str(v).split("/") if x not in ("25", "50")]
    pezzi = [f"vasca {x}m" for x in piscina]
    if fondo:
        pezzi.append("acque libere")
    return " · ".join(pezzi)


def _scheda(r: dict, futura: bool) -> str:
    nome = html.escape(str(r.get("nome") or "Manifestazione"))
    url = str(r.get("website_link") or "").strip()
    titolo = (f'<a href="{html.escape(url, quote=True)}" target="_blank" '
              f'rel="noopener">{nome}</a>') if url.lower().startswith("http") else nome

    righe = []
    if r.get("organizzatore"):
        righe.append(html.escape(str(r["organizzatore"])))
    vasche = _vasche(r.get("vasche"))
    if vasche:
        righe.append(vasche)
    if r.get("timing"):
        righe.append(f"cronometraggio {str(r['timing']).lower()}")

    nostre = int(r.get("nostre_gare") or 0)
    atleti = int(r.get("nostri_atleti") or 0)
    if nostre:
        righe.append(f"{nostre} nostre gare, {atleti} atleti")
    elif futura:
        chiusura = r.get("close_registration_date")
        if chiusura is not None and not pd.isna(chiusura):
            righe.append(f"iscrizioni entro il "
                         f"{pd.to_datetime(chiusura).strftime('%d/%m/%Y')}")

    pdf = str(r.get("pdf_link") or "").strip()
    if pdf.lower().startswith("http"):
        righe.append(f'<a href="{html.escape(pdf, quote=True)}" target="_blank" '
                     f'rel="noopener">programma PDF ↗</a>')

    return (f'<div class="ag-card{" ag-futura" if futura else ""}">'
            f'<div class="ag-data">{_intervallo(r)}</div>'
            f'<div class="ag-nome">{titolo}</div>'
            f'<div class="ag-meta">{" · ".join(righe)}</div>'
            f'</div>')


def _stato_iscrizioni(r: dict) -> tuple[bool, str]:
    """(si puo' cliccare, perche' no).

    La finestra la decide `crud.stato_finestra`, che e' la stessa regola usata
    dalle pagine di iscrizione e dal controllo lato server: dai 30 giorni
    prima dell'apertura ufficiale al giorno prima della chiusura. Qui si
    sceglie solo come disegnare il bottone; la verifica vera la rifa' comunque
    crud rileggendo il database prima di scrivere.
    """
    if auth.sola_lettura():
        return False, "Stai guardando come un altro atleta: sola lettura"
    return crud.stato_finestra(r.get("open_registration_date"),
                               r.get("close_registration_date"), OGGI)


futuri = manif[manif["start_date"].dt.date >= OGGI].sort_values("start_date")
passati = manif[manif["start_date"].dt.date < OGGI].sort_values("start_date",
                                                                ascending=False)

# La finestra di ORIZZONTE giorni, con due eccezioni.
# La prima: una ricerca per nome la scavalca, perche' chi scrive "Belluno"
# vuole trovare quella gara, non sentirsi dire che non c'e'.
# La seconda: una manifestazione gia' aperta alle iscrizioni resta a video
# anche se e' piu' in la'. Oggi non succede, perche' 75 giorni coprono tutte
# le aperture a calendario, ma e' la rete che impedisce al bottone Iscriviti
# di sparire se un domani una gara aprisse le adesioni con piu' anticipo.
LIMITE = OGGI + _dt.timedelta(days=ORIZZONTE)
if not sta_cercando and not futuri.empty:
    vicina = futuri["start_date"].dt.date <= LIMITE
    aperta = futuri.apply(lambda r: _stato_iscrizioni(r)[0], axis=1)
    lontane = futuri[~(vicina | aperta)]
    futuri = futuri[vicina | aperta]
else:
    lontane = futuri.iloc[0:0]

st.markdown('<div class="section-title">In programma</div>', unsafe_allow_html=True)
if futuri.empty and not lontane.empty:
    prima = lontane["start_date"].min()
    st.info(f"Niente in calendario nei prossimi {ORIZZONTE} giorni. La "
            f"prossima e' il {prima.strftime('%d/%m/%Y')}: cercala per nome "
            "per vederla.")
elif futuri.empty:
    st.info("Nessuna manifestazione futura in calendario. A database arrivano "
            "solo quelle gia' nuotate: le prossime si inseriscono a mano "
            "dall'Anagrafica manifestazioni."
            if auth.is_admin() else
            "Nessuna manifestazione futura in calendario: le prossime le "
            "carica l'amministratore.")
else:
    # Una card per volta, con il bottone accanto: la card a sinistra e
    # Iscriviti a destra, che e' dove lo si cerca. I bottoni non stanno
    # dentro una stringa HTML, quindi niente blocco unico.
    _sono_atleta = (auth.current_user() or {}).get("athlete_id") is not None
    for r in futuri.to_dict("records"):
        if not _sono_atleta:
            st.markdown(_scheda(r, True), unsafe_allow_html=True)
            continue
        # Le due colonne stanno dentro un contenitore con chiave perche' il
        # CSS possa tenerle affiancate anche sul telefono: sotto i 640px
        # Streamlit impila le colonne, e il bottone finiva sotto la scheda.
        with st.container(key=f"riga_{int(r['comp_id'])}"):
            c_card, c_btn = st.columns([5, 2], vertical_alignment="center")
        c_card.markdown(_scheda(r, True), unsafe_allow_html=True)
        si_puo, perche = _stato_iscrizioni(r)
        # Il bottone c'e' sempre, anche spento: dice che quella gara una
        # iscrizione ce l'ha, e il perche' sta nel tooltip. Quadrato: lo
        # stile sta in theme.py, agganciato alla chiave isc_.
        with c_btn.container(key=f"isc_{int(r['comp_id'])}"):
            if st.button("📝\n\nIscriviti", key=f"iscb_{int(r['comp_id'])}",
                         type="primary" if si_puo else "secondary",
                         disabled=not si_puo,
                         help=perche or "Vai alla pagina di iscrizione"):
                st.session_state["isc_comp"] = int(r["comp_id"])
                st.switch_page("views/iscrizioni_nuove.py")

st.markdown(f'<div class="section-title">Concluse · {len(passati)}</div>',
            unsafe_allow_html=True)
if passati.empty:
    st.info("Nessuna manifestazione conclusa nel periodo.")
else:
    MOSTRA = 5
    st.markdown("".join(_scheda(r, False)
                        for r in passati.head(MOSTRA).to_dict("records")),
                unsafe_allow_html=True)
    if len(passati) > MOSTRA:
        st.caption(f"Mostrate le ultime {MOSTRA} di {len(passati)}. "
                   f"Restringi il periodo o usa la ricerca per vedere le altre.")

st.caption(f"Periodo: {season_mod.label(sy).lower()}.")
