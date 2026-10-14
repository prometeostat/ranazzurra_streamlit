"""
views/iscrizioni_nuove.py — Iscriviti: l'atleta si iscrive alle gare.

La pagina e' un guscio: il modulo sta in `views/_iscrizioni_form.py`, lo
stesso che serve la pagina Modifica, perche' scegliere le gare e cambiarle
sono la stessa operazione con due parole diverse davanti. Qui si propongono
tutte le manifestazioni aperte, con le gare gia' scelte spuntate.
"""
from __future__ import annotations

from views import _iscrizioni_form

_iscrizioni_form.disegna("nuova")
