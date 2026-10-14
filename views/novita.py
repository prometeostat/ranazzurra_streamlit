"""
views/novita.py — cosa e' cambiato nell'app, versione per versione.

Legge CHANGELOG.md e lo mostra com'e'. La pagina e' aperta a tutti: le
novita' riguardano chi usa l'app, non chi la scrive.
"""
from __future__ import annotations

import streamlit as st

import version
from views._common import page_header

page_header("Novità", "Cosa è cambiato nell'app")

testo = version.changelog()
if not testo.strip():
    st.info("Il file delle novità non è disponibile.")
    st.stop()

# Il titolo del file lo fa gia' l'intestazione della pagina: si parte dalla
# prima riga utile dopo l'H1, se c'e'.
righe = testo.splitlines()
if righe and righe[0].startswith("# "):
    righe = righe[1:]
st.markdown("\n".join(righe).strip())

st.markdown("---")
st.caption(f"Stai usando la versione {version.etichetta()}. "
           "L'app si aggiorna da sola: se vedi qualcosa di strano dopo un "
           "rilascio, ricarica la pagina.")
