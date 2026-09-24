"""
season.py — stagioni agonistiche e categorie master.

Una stagione va dal 1 settembre al 31 agosto dell'anno successivo e si
identifica con l'anno di inizio: 2025 -> "2025/26".
Il valore speciale ALL (0) significa "tutte le stagioni".
"""
from __future__ import annotations

import datetime as _dt

ALL = 0
_ALL_START, _ALL_END = "1900-01-01", "2999-12-31"
# Intervallo vuoto: usato per la stagione precedente quando si guarda tutto
_NONE_START, _NONE_END = "1900-01-01", "1900-01-02"


def current_season_year(today: _dt.date | None = None) -> int:
    """Anno di inizio della stagione in corso."""
    today = today or _dt.date.today()
    return today.year if today.month >= 9 else today.year - 1


def is_all(season_year: int) -> bool:
    return int(season_year) == ALL


def bounds(season_year: int) -> tuple[str, str]:
    """Confini (start, end) della stagione, come stringhe ISO."""
    if is_all(season_year):
        return _ALL_START, _ALL_END
    if season_year < 0:          # stagione precedente di "tutte": non esiste
        return _NONE_START, _NONE_END
    return f"{season_year}-09-01", f"{season_year + 1}-08-31"


def previous_bounds(season_year: int) -> tuple[str, str]:
    """Confini della stagione precedente, vuoti in modalita' 'tutte'."""
    if is_all(season_year):
        return _NONE_START, _NONE_END
    return bounds(season_year - 1)


def label(season_year: int) -> str:
    """2025 -> '2025/2026'; ALL -> 'Tutte le stagioni'."""
    if is_all(season_year):
        return "Tutte le stagioni"
    return f"{season_year}/{season_year + 1}"


def short_label(season_year: int) -> str:
    """2025 -> '25/26'; ALL -> 'Tutte'."""
    if is_all(season_year):
        return "Tutte"
    return f"{str(season_year)[2:]}/{str(season_year + 1)[2:]}"


def previous_short_label(season_year: int) -> str:
    return "—" if is_all(season_year) else short_label(season_year - 1)


def category_year(season_year: int) -> int:
    """
    Anno di riferimento per la categoria master: la FIN guarda l'eta'
    compiuta entro il 31/12 dell'anno in cui la stagione si chiude.
    In modalita' 'tutte' si usa la stagione in corso.
    """
    if is_all(season_year):
        return current_season_year() + 1
    return season_year + 1


# ══════════════════════════════════════════════════════════════════
# Categorie master FIN
# ══════════════════════════════════════════════════════════════════

def master_band(birth_year: int, season_year: int) -> int:
    """
    Fascia quinquennale: anno di chiusura stagione meno anno di nascita,
    arrotondato per difetto a multipli di 5. Nel 2026 un nato nel 1980
    compie 46 anni e sta in M45.
    """
    return (category_year(season_year) - int(birth_year)) // 5 * 5


def master_category(birth_year: int | None, season_year: int,
                    sesso: str | bool | None = "M") -> str:
    """
    Etichetta della categoria per quella stagione, col prefisso di sesso:
    M45 per un maschio, F45 per una femmina. Le fasce partono da 20; sotto
    non esistono categorie e si parla di giovanili.

    sesso accetta 'M'/'F' oppure il booleano di athletes.sex (TRUE = maschio).
    """
    if birth_year is None:
        return "—"
    try:
        band = master_band(int(birth_year), season_year)
    except (TypeError, ValueError):
        return "—"
    if isinstance(sesso, bool):
        prefisso = "M" if sesso else "F"
    else:
        prefisso = "F" if str(sesso).upper().startswith("F") else "M"
    if band >= 20:
        return f"{prefisso}{band}"
    return "Giovanile"


def age_in_season(birth_year: int | None, season_year: int) -> int | None:
    """Eta' compiuta entro il 31/12 dell'anno di chiusura stagione."""
    if birth_year is None:
        return None
    try:
        return category_year(season_year) - int(birth_year)
    except (TypeError, ValueError):
        return None
