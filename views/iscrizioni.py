"""
views/iscrizioni.py — indice delle iscrizioni dell'atleta.

Tre porte: iscriversi a una manifestazione aperta, tornare a cambiare quello
che si era scelto, e guardare tutto lo storico delle proprie iscrizioni.
Iscriviti e Modifica scrivono dentro la stessa finestra, che si chiude il
giorno prima della chiusura ufficiale; la terza voce si legge sempre.
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
mio_id = int(utente["athlete_id"])


def _voce(icona: str, titolo: str, sottotitolo: str, pagina: str, chiave: str) -> None:
    """Come in Cerca: tutta la scheda e' cliccabile."""
    if st.button(f"{icona}\n\n{titolo}\n\n{sottotitolo}",
                 key=f"hub_{chiave}", use_container_width=True):
        st.switch_page(pagina)


# I numeri arrivano dalle stesse letture cachate che usano le pagine: niente
# query in piu' solo per i sottotitoli.
aperte = crud.manifestazioni_iscrivibili()
teste = crud.mie_manifestazioni(mio_id)

n_aperte = 0 if aperte.empty else len(aperte)
n_gare = 0 if teste.empty else int(teste["gare"].sum())
# Da cambiare ci sono le manifestazioni ancora da nuotare dove ho delle gare
# e il termine non e' passato: le stesse che la pagina Modifica propone come
# modificabili.
if teste.empty:
    n_mod = 0
else:
    _da_nuotare = teste[teste["futura"].fillna(False).astype(bool)]
    n_mod = int(_da_nuotare["aperta"].fillna(False).astype(bool).sum())

_voce("📝", "Iscriviti",
      ("Nessuna manifestazione aperta in questo momento" if not n_aperte
       else f"{n_aperte} manifestazioni aperte alle iscrizioni"),
      "views/iscrizioni_nuove.py", "isc_nuove")
_voce("✏️", "Modifica",
      ("Niente da cambiare in questo momento" if not n_mod
       else f"{n_mod} manifestazioni che puoi ancora cambiare"),
      "views/iscrizioni_modifica.py", "isc_modifica")
_voce("📒", "Vedi le mie iscrizioni",
      ("Non sei iscritto a niente" if not n_gare
       else f"{n_gare} gare fra passato e futuro"),
      "views/iscrizioni_mie.py", "isc_mie")

st.caption("Le adesioni si raccolgono dai 30 giorni prima della data di "
           "apertura ufficiale fino al giorno prima della chiusura: "
           "l'ultimo giorno serve alla squadra per portarle sul portale "
           "federale, e da quel momento si possono solo guardare.")
