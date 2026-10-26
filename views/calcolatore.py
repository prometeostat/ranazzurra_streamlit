"""
views/calcolatore.py — indice del calcolatore FIN.

Due porte, una per verso: dal tempo ai punti e dai punti al tempo. E' la
stessa formula letta nei due sensi, ma la domanda che si fa chi apre la
pagina e' diversa, e tenerle separate evita un modulo con due campi di cui
uno va lasciato vuoto.
"""
from __future__ import annotations

import streamlit as st

import punteggi
from views._common import page_header

page_header("Calcolatore", f"Punteggi FIN master {punteggi.STAGIONE_TABELLA}")


def _voce(icona: str, titolo: str, sottotitolo: str, pagina: str, chiave: str) -> None:
    """Come in Cerca: tutta la scheda e' cliccabile."""
    if st.button(f"{icona}\n\n{titolo}\n\n{sottotitolo}",
                 key=f"hub_{chiave}", use_container_width=True):
        st.switch_page(pagina)


_voce("🧮", "Calcolatore Punti",
      "Hai un tempo, vuoi sapere quanto vale",
      "views/calcolatore_punti.py", "calc_punti")
_voce("⏱️", "Calcolatore Tempo",
      "Hai un punteggio, vuoi sapere che tempo serve",
      "views/calcolatore_tempo.py", "calc_tempo")

st.caption("I tempi base sono quelli della tabella individuale FIN "
           f"{punteggi.STAGIONE_TABELLA}, una per vasca. Il conto non "
           "guarda il database: va bene anche per un tempo di un altro, o "
           "per uno che non hai ancora nuotato.")
