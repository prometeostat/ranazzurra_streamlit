"""
version.py — numero di versione dell'app e lettura del changelog.

Il numero sta qui e non in un file di configurazione: e' codice, viaggia con
il commit, e cosi' la versione che si vede a video e' sempre quella che gira
davvero. Le novita' stanno in CHANGELOG.md accanto a questo file, scritte a
mano a ogni rilascio.

Tre numeri, con il significato di sempre: il primo cambia quando cambia il
modo di usare l'app, il secondo quando arriva una funzione nuova, il terzo
per le correzioni.
"""
from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path

VERSIONE = "1.1.0"
DATA_RILASCIO = _dt.date(2026, 10, 26)

_FILE = Path(__file__).with_name("CHANGELOG.md")


def etichetta() -> str:
    """'v1.1.0 · 26/10/2026', per le righe di piede."""
    return f"v{VERSIONE} · {DATA_RILASCIO.strftime('%d/%m/%Y')}"


def changelog() -> str:
    """Tutto il file delle novita'. Stringa vuota se non c'e'."""
    try:
        return _FILE.read_text(encoding="utf-8")
    except OSError:
        return ""


def novita(versione: str | None = None) -> str:
    """
    Il pezzo di changelog di una sola versione, senza la sua intestazione.

    Serve all'avviso che compare dopo un rilascio: li' si mostrano le novita'
    dell'ultima versione, non tutta la storia. Se il blocco non si trova
    torna una stringa vuota e chi chiama decide cosa farne.
    """
    testo = changelog()
    if not testo:
        return ""
    cercata = re.escape(versione or VERSIONE)
    # Dal titolo di quella versione fino al titolo successivo, o alla fine.
    trovato = re.search(rf"^##\s+{cercata}\b.*?$(.*?)(?=^##\s|\Z)",
                        testo, re.M | re.S)
    return trovato.group(1).strip() if trovato else ""
