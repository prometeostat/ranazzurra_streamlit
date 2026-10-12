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

    La finestra parte GIORNI_ANTICIPO giorni prima dell'apertura ufficiale e
    finisce alla chiusura, estremi compresi: le adesioni si raccolgono prima
    di portarle sul portale federale. Senza le due date non si clicca.
    La verifica vera la rifa' comunque crud prima di scrivere: qui si decide
    solo come disegnare il bottone.
    """
    apertura = pd.to_datetime(r.get("open_registration_date"), errors="coerce")
    chiusura = pd.to_datetime(r.get("close_registration_date"), errors="coerce")
    if pd.isna(apertura) or pd.isna(chiusura):
        return False, "Date di iscrizione non ancora registrate"
    da = apertura.date() - _dt.timedelta(days=crud.GIORNI_ANTICIPO)
    if OGGI < da:
        return False, f"Si parte il {da.strftime('%d/%m/%Y')}"
    if OGGI > chiusura.date():
        return False, f"Chiuse il {chiusura.strftime('%d/%m/%Y')}"
    return True, ""


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
