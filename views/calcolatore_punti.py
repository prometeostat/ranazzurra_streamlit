"""
views/calcolatore_punti.py — dal tempo al punteggio.

Si scelgono gara, vasca, sesso e categoria, si scrive il tempo nelle tre
caselle e si premo Calcola. Il conto sta in punteggi.py: qui si raccolgono i
campi e si mostra il risultato.
"""
from __future__ import annotations

import html

import streamlit as st

import punteggi
from theme import section
from views._calcolatore_comune import (campo_tempo, carica_tabella,
                                       nota_in_fondo, riga_scarto,
                                       riquadro_tempo_base, scelte)
from views._common import page_header

page_header("Calcolatore Punti", "Dal tempo al punteggio")

tb = carica_tabella()
if tb is None:
    st.stop()

s = scelte(tb, "calcp")
riquadro_tempo_base(s)

cent, err_tempo, premuto = campo_tempo("calcp")

if err_tempo:
    st.warning(err_tempo, icon="⚠️")
    st.stop()

if not premuto:
    st.caption("Compila il tempo e premi Calcola.")
    nota_in_fondo()
    st.stop()

if cent is None:
    st.warning("Il tempo è a zero: scrivi minuti, secondi e centesimi.",
               icon="⚠️")
    st.stop()

esito = punteggi.esito_punti(tb, s["gara"], s["vasca"], s["sesso"],
                             s["categoria"], cent)

if esito["errore"]:
    st.warning(esito["errore"], icon="⚠️")
else:
    p = esito["punti"]
    # Verde sopra il tempo base, oro sotto: sono le stesse tinte che l'app
    # usa per i personali e per i tempi in avvicinamento.
    tono = "green" if p >= 1000 else "gold"
    section("Punteggio")
    st.markdown(
        f'<div class="kpi-wrap">'
        f'<div class="kpi-val {tono}">{punteggi.testo_da_punti(p)}</div>'
        f'<div class="kpi-lbl">Punti FIN</div>'
        f'<div class="kpi-sub">{html.escape(punteggi.testo_da_cent(esito["cent_reale"]))}'
        f' su un tempo base di '
        f'{html.escape(punteggi.testo_da_cent(esito["cent_base"]))}</div>'
        f'<div class="kpi-sub">{html.escape(riga_scarto(esito["scarto"]))}</div>'
        f'</div>', unsafe_allow_html=True)

    if p >= punteggi.PUNTI_SOSPETTI:
        st.warning(
            f"Oltre {punteggi.PUNTI_SOSPETTI} punti: possibile, ma e' il "
            "livello dei record. Controlla che gara, vasca e categoria "
            "siano quelle giuste, e che i minuti non siano finiti nella "
            "casella dei secondi.", icon="🔎")

    # Nei referti dell'app i punti sono numeri interi (fin_score e' uno
    # smallint): dirlo qui evita di cercare i decimali nella scheda atleta.
    st.caption(f"Nelle schede e nelle classifiche i punti sono interi: "
               f"questo tempo vale **{int(p)}**.")

nota_in_fondo()
