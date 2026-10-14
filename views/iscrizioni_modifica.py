"""
views/iscrizioni_modifica.py — Modifica: si cambia quello che si era scelto.

Guscio come la pagina Iscriviti: il modulo e' lo stesso,
`views/_iscrizioni_form.py`, chiamato in modo "modifica". La differenza sta
nell'elenco, che propone solo le manifestazioni ancora da nuotare in cui
l'atleta ha davvero delle gare, e nel fatto che quelle col termine scaduto
restano in elenco per mostrarle in sola lettura invece di farle sparire.

Il termine e' il giorno prima della chiusura ufficiale, come per la prima
iscrizione: dal giorno di `close_registration_date` in poi non si tocca piu'
niente, e il controllo lo rifa' `crud.salva_iscrizioni` rileggendo il
database.
"""
from __future__ import annotations

from views import _iscrizioni_form

_iscrizioni_form.disegna("modifica")
