"""
views/cerca.py — pagina indice della sezione Cerca.

Cinque porte d'ingresso: le proprie iscrizioni, la scheda di un atleta, le
classifiche di squadra, i risultati di una manifestazione gara per gara e il
calcolatore dei punteggi FIN.

Le iscrizioni stanno per prime perche' sono l'unica voce con una scadenza:
le altre si consultano quando capita, quella no. Il calcolatore sta per
ultimo perche' e' l'unico che non guarda il database: non racconta niente di
quello che e' stato fatto, serve a fare un conto.
"""
from __future__ import annotations

import streamlit as st

from views._common import page_header

page_header("Cerca", "Iscrizioni, atleti, classifiche e manifestazioni")


def _voce(icona: str, titolo: str, sottotitolo: str, pagina: str, chiave: str) -> None:
    """La scheda e' il bottone: icona, titolo e sottotitolo sono tre paragrafi
    dell'etichetta, impaginati dal CSS legato alla chiave hub_*."""
    if st.button(f"{icona}\n\n{titolo}\n\n{sottotitolo}",
                 key=f"hub_{chiave}", use_container_width=True):
        st.switch_page(pagina)


_voce("📝", "Iscrizioni",
      "Iscriviti, modifica e controlla le tue gare",
      "views/iscrizioni.py", "iscrizioni")
_voce("🏊", "Atleta", "Tempi, personali e storico gara per gara",
      "views/scheda.py", "scheda")
_voce("🏆", "Classifiche",
      "I migliori tempi di squadra, per specialita'",
      "views/classifiche.py", "classifiche")
_voce("📋", "Manifestazioni",
      "Gare, iscritti, tempi e punteggi",
      "views/risultati.py", "risultati")
_voce("🧮", "Calcolatore",
      "Punti FIN da un tempo, e il tempo da un punteggio",
      "views/calcolatore.py", "calcolatore")
