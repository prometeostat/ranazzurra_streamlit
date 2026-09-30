"""
views/gestione.py — indice delle anagrafiche, riservato all'amministratore.
"""
from __future__ import annotations

import streamlit as st

import auth
import crud
import data
from views._common import page_header

page_header("Gestione", "Anagrafiche")

if not auth.is_admin():
    st.info("Sezione riservata all'amministratore.")
    st.stop()

atleti = crud.elenco_atleti()
manif = crud.elenco_manifestazioni()
n_accessi = int(data.access_log_stats().get("righe") or 0)
n_atleti = int((atleti["is_deleted"] == False).sum()) if not atleti.empty else 0  # noqa: E712
n_manif = int((manif["is_deleted"] == False).sum()) if not manif.empty else 0     # noqa: E712


def _voce(icona: str, titolo: str, sottotitolo: str, pagina: str, chiave: str) -> None:
    """Come in Cerca: tutta la scheda e' cliccabile, niente bottone "Apri"."""
    if st.button(f"{icona}\n\n{titolo}\n\n{sottotitolo}",
                 key=f"hub_{chiave}", use_container_width=True):
        st.switch_page(pagina)


_voce("📇", "Anagrafica atleti", f"{n_atleti} tesserati attivi",
      "views/anagrafica.py", "atleti")
_voce("📅", "Anagrafica manifestazioni", f"{n_manif} manifestazioni in calendario",
      "views/manifestazioni.py", "manifestazioni")
_voce("🔐", "Registro accessi", f"{n_accessi} righe a database",
      "views/accessi.py", "accessi")

st.caption("Le modifiche qui dentro si vedono subito in tutta l'app: dopo ogni "
           "salvataggio il cache dei dati viene svuotato.")
