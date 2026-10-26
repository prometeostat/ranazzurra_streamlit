"""
views/calcolatore_tempo.py — dal punteggio al tempo.

La formula letta all'indietro: TR = (tempo base x 1000) / punti. Serve per
allenarsi con un obiettivo, che e' il motivo per cui qualcuno la cerca.

Un'avvertenza che vale la pena di scrivere a video: il tempo che esce e' il
piu' **lento** che vale ancora quel punteggio. Siccome i punti si troncano,
un centesimo in piu' fa scendere sotto l'obiettivo, e un centesimo in meno
vale un filo di piu'. Per questo la pagina mostra anche il punteggio vero di
quel tempo, che quasi mai e' il numero tondo chiesto.
"""
from __future__ import annotations

import html

import streamlit as st

import punteggi
from theme import section
from views._calcolatore_comune import (campo_punteggio, carica_tabella,
                                       nota_in_fondo, riga_scarto,
                                       riquadro_tempo_base, scelte)
from views._common import page_header

page_header("Calcolatore Tempo", "Dal punteggio al tempo")

tb = carica_tabella()
if tb is None:
    st.stop()

s = scelte(tb, "calct")
riquadro_tempo_base(s)

obiettivo, err_punti, premuto = campo_punteggio("calct")

if err_punti:
    st.warning(err_punti, icon="⚠️")
    st.stop()

if not premuto:
    st.caption("Scrivi il punteggio e premi Calcola.")
    nota_in_fondo()
    st.stop()

if obiettivo is None:
    st.warning("Il punteggio è a zero: scrivi quanti punti vuoi fare.",
               icon="⚠️")
    st.stop()

esito = punteggi.esito_tempo(tb, s["gara"], s["vasca"], s["sesso"],
                             s["categoria"], obiettivo)

if esito["errore"]:
    st.warning(esito["errore"], icon="⚠️")
else:
    tono = "green" if obiettivo >= 1000 else "gold"
    section("Tempo da nuotare")
    st.markdown(
        f'<div class="kpi-wrap">'
        f'<div class="kpi-val {tono}">'
        f'{html.escape(punteggi.testo_da_cent(esito["cent_reale"]))}</div>'
        f'<div class="kpi-lbl">Per {punteggi.testo_da_punti(obiettivo)} punti</div>'
        f'<div class="kpi-sub">Tempo base '
        f'{html.escape(punteggi.testo_da_cent(esito["cent_base"]))}</div>'
        f'<div class="kpi-sub">{html.escape(riga_scarto(esito["scarto"]))}</div>'
        f'</div>', unsafe_allow_html=True)

    st.caption(
        f"È il tempo più lento che vale ancora "
        f"{punteggi.testo_da_punti(obiettivo)} punti: nuotandolo esatto fanno "
        f"**{punteggi.testo_da_punti(esito['punti_resi'])}**, un centesimo "
        "più piano e si scende sotto l'obiettivo.")

    if obiettivo >= punteggi.PUNTI_SOSPETTI:
        st.warning(
            f"Oltre {punteggi.PUNTI_SOSPETTI} punti: il tempo che esce e' da "
            "record. Controlla il punteggio.", icon="🔎")

nota_in_fondo()
