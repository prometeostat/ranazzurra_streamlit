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
import data
import season as season_mod
from views._common import inline_filters, page_header, season_year

OGGI = _dt.date.today()

page_header("Agenda", "Calendario manifestazioni")
inline_filters("agenda", pool=False)

sy = season_year()
manif = data.load_agenda(sy).copy()

cerca = st.text_input("Cerca manifestazione", placeholder="Nome, citta', organizzatore…",
                      label_visibility="collapsed", key="agenda_cerca")
if cerca.strip() and not manif.empty:
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


futuri = manif[manif["start_date"].dt.date >= OGGI].sort_values("start_date")
passati = manif[manif["start_date"].dt.date < OGGI].sort_values("start_date",
                                                                ascending=False)

st.markdown('<div class="section-title">In programma</div>', unsafe_allow_html=True)
if futuri.empty:
    st.info("Nessuna manifestazione futura in calendario. A database arrivano "
            "solo quelle gia' nuotate: le prossime si inseriscono a mano "
            "dall'Anagrafica manifestazioni."
            if auth.is_admin() else
            "Nessuna manifestazione futura in calendario: le prossime le "
            "carica la segreteria.")
else:
    st.markdown("".join(_scheda(r, True) for r in futuri.to_dict("records")),
                unsafe_allow_html=True)

st.markdown(f'<div class="section-title">Concluse · {len(passati)}</div>',
            unsafe_allow_html=True)
if passati.empty:
    st.info("Nessuna manifestazione conclusa nel periodo.")
else:
    MOSTRA = 25
    st.markdown("".join(_scheda(r, False)
                        for r in passati.head(MOSTRA).to_dict("records")),
                unsafe_allow_html=True)
    if len(passati) > MOSTRA:
        st.caption(f"Mostrate le ultime {MOSTRA} di {len(passati)}. "
                   f"Restringi il periodo o usa la ricerca per trovare le altre.")

st.caption(f"Periodo: {season_mod.label(sy).lower()}.")
