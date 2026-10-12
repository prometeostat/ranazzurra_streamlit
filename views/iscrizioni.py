"""
views/iscrizioni.py — indice delle iscrizioni dell'atleta.

Due porte: una per iscriversi a una manifestazione aperta, l'altra per
guardare quello che si e' gia' fatto.
"""
from __future__ import annotations

import streamlit as st

import auth
import crud
from views._common import page_header

page_header("Iscrizioni", "Le tue gare")

utente = auth.current_user() or {}
if utente.get("athlete_id") is None:
    st.info("Le iscrizioni sono per i tesserati: il tuo account non e' "
            "collegato a una scheda atleta.")
    st.stop()


def _voce(icona: str, titolo: str, sottotitolo: str, pagina: str, chiave: str) -> None:
    """Come in Cerca: tutta la scheda e' cliccabile."""
    if st.button(f"{icona}\n\n{titolo}\n\n{sottotitolo}",
                 key=f"hub_{chiave}", use_container_width=True):
        st.switch_page(pagina)


aperte = len(crud.manifestazioni_iscrivibili())
mie = len(crud.mie_iscrizioni(int(utente["athlete_id"])))

_voce("📝", "Nuove iscrizioni",
      ("Nessuna manifestazione aperta in questo momento" if not aperte
       else f"{aperte} manifestazioni aperte alle iscrizioni"),
      "views/iscrizioni_nuove.py", "isc_nuove")
_voce("📒", "Lista iscrizioni",
      ("Non sei iscritto a niente" if not mie
       else f"{mie} gare fra quelle a cui ti sei iscritto"),
      "views/iscrizioni_mie.py", "isc_mie")

st.caption("Le adesioni si raccolgono dai 30 giorni prima della data di "
           "apertura ufficiale fino alla chiusura delle iscrizioni: dopo "
           "si possono solo guardare.")
