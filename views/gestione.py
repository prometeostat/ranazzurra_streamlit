"""
views/gestione.py — indice dell'area riservata.

Gli allenatori arrivano fin qui ma vedono solo le iscrizioni ricevute: le
anagrafiche, i tempi e il registro accessi restano dell'amministratore.
"""
from __future__ import annotations

import streamlit as st

import auth
import crud
from views._common import page_header

page_header("Gestione", "Iscrizioni e anagrafiche")

if not auth.is_staff():
    st.info("Sezione riservata ad allenatori e amministratore.")
    st.stop()


def _voce(icona: str, titolo: str, sottotitolo: str, pagina: str, chiave: str) -> None:
    """Come in Cerca: tutta la scheda e' cliccabile, niente bottone "Apri"."""
    if st.button(f"{icona}\n\n{titolo}\n\n{sottotitolo}",
                 key=f"hub_{chiave}", use_container_width=True):
        st.switch_page(pagina)


# Tutti i numeri in un colpo solo, prima di disegnare: con una query per
# riquadro le schede comparivano a scaglioni, una per ogni risposta del
# database, e la pagina sembrava rotta.
n = crud.conteggi_gestione()
n_aperte = int(n.get("iscrivibili") or 0)

_voce("📝", "Iscrizioni gare",
      ("Nessuna manifestazione con iscrizioni aperte" if not n_aperte
       else f"{n_aperte} manifestazioni con le iscrizioni aperte"),
      "views/iscrizioni_admin.py", "iscrizioni_admin")

if not auth.is_admin():
    st.caption("Le anagrafiche, l'inserimento dei tempi e il registro "
               "accessi sono riservati all'amministratore.")
    st.stop()

n_atleti = int(n.get("atleti") or 0)
n_staff = int(n.get("staff") or 0)
n_manif = int(n.get("manifestazioni") or 0)
n_accessi = int(n.get("accessi") or 0)

_voce("📇", "Anagrafica atleti",
      f"{n_atleti} tesserati attivi"
      + (f", {n_staff} fra allenatori e staff" if n_staff else ""),
      "views/anagrafica.py", "atleti")
_voce("📅", "Anagrafica manifestazioni", f"{n_manif} manifestazioni in calendario",
      "views/manifestazioni.py", "manifestazioni")
_voce("⏱️", "Inserisci tempi", "Tempi e punti FIN, gara per gara",
      "views/tempi.py", "tempi")
_voce("🔐", "Registro accessi", f"{n_accessi} righe a database",
      "views/accessi.py", "accessi")

st.caption("Le modifiche qui dentro si vedono subito in tutta l'app: dopo ogni "
           "salvataggio il cache dei dati viene svuotato.")
