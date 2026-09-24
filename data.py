"""
data.py — caricamento dati e piccole elaborazioni.

Regole che valgono per tutte le funzioni qui dentro:
  - il cast dei tipi si fa DENTRO la funzione cachata (psycopg restituisce
    Decimal, e mutare un DataFrame dopo il cache manda in segfault pyarrow);
  - chi consuma questi DataFrame lavora sempre su .copy().
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

import season as season_mod
from db import query_df
from queries import (
    AGENDA_SQL, ALLTIME_PB_SQL, ALL_ATHLETES_SQL, ATHLETES_SQL, CLUB_RANKING_SQL, COMPARE_PB_SQL,
    FIN_LEADERBOARD_SQL, FREQUENCY_SQL, PB_SQL, RACES_SQL, RANKING_SQL,
    SEASONS_SQL, SEASON_META_SQL, SPLITS_BY_EVENT_SQL, SPLITS_SQL, TREND_SQL,
)

TTL = 3600


def _num(df: pd.DataFrame, cols) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


# ══════════════════════════════════════════════════════════════════
# Anagrafica e stagioni
# ══════════════════════════════════════════════════════════════════

@st.cache_data(ttl=TTL, show_spinner=False)
def load_seasons() -> list[int]:
    df = query_df(SEASONS_SQL)
    if df.empty:
        return [season_mod.current_season_year()]
    return [int(v) for v in df["season_start_year"].tolist()]


@st.cache_data(ttl=TTL, show_spinner=False)
def load_athletes(season_year: int) -> pd.DataFrame:
    start, end = season_mod.bounds(season_year)
    df = query_df(ATHLETES_SQL, (season_mod.category_year(season_year), start, end))
    return _num(df, ("age", "birth_year", "master_cat", "fin_code", "athlete_id"))


@st.cache_data(ttl=TTL, show_spinner=False)
def load_all_athletes(season_year: int) -> pd.DataFrame:
    df = query_df(ALL_ATHLETES_SQL, (season_mod.category_year(season_year),))
    return _num(df, ("age", "birth_year", "master_cat", "fin_code", "athlete_id"))


# ══════════════════════════════════════════════════════════════════
# Scheda atleta
# ══════════════════════════════════════════════════════════════════

@st.cache_data(ttl=TTL, show_spinner=False)
def load_report(athlete_id: int, season_year: int) -> dict:
    curr_start, curr_end = season_mod.bounds(season_year)
    # In modalita' "tutte le stagioni" non esiste una stagione precedente:
    # previous_bounds restituisce un intervallo vuoto e i PB di confronto
    # risultano nulli, che e' esattamente quello che vogliamo mostrare.
    prev_start, prev_end = season_mod.previous_bounds(season_year)

    meta = query_df(SEASON_META_SQL, (athlete_id, curr_start, curr_end))
    meta = _num(meta, ("total_races", "total_competitions", "distinct_events",
                       "avg_fin_score", "best_fin_score"))

    pb = query_df(PB_SQL, (
        curr_start, curr_end,
        prev_start, prev_end,
        curr_start, curr_end,
        athlete_id,
        curr_start, curr_end,
    ))
    pb = _num(pb, ("pb_curr_sec", "pb_prev_sec", "pb_alltime_sec",
                   "pool_length", "swims_curr", "swims_total"))

    ranking = query_df(RANKING_SQL, (curr_start, curr_end, athlete_id))
    ranking = _num(ranking, ("pb_sec", "rank_club", "n_club", "pool_length"))

    freq = query_df(FREQUENCY_SQL, (athlete_id, curr_start, curr_end))
    freq = _num(freq, ("races", "events"))

    trend = query_df(TREND_SQL, (athlete_id,))
    trend = _num(trend, ("time_sec", "pool_length", "fin_score", "season_start_year"))
    if not trend.empty:
        trend["season_label"] = trend["season_start_year"].apply(
            lambda y: season_mod.short_label(int(y)) if pd.notna(y) else "—")

    return dict(meta=meta, pb=pb, ranking=ranking, freq=freq, trend=trend)


# ══════════════════════════════════════════════════════════════════
# Gare e passaggi
# ══════════════════════════════════════════════════════════════════

@st.cache_data(ttl=TTL, show_spinner=False)
def load_races(athlete_id: int, season_year: int) -> pd.DataFrame:
    start, end = season_mod.bounds(season_year)
    df = query_df(RACES_SQL, (athlete_id, start, end))
    return _num(df, ("time_sec", "pool_length", "fin_score", "n_split",
                     "athlete_race_id", "comp_id"))


@st.cache_data(ttl=TTL, show_spinner=False)
def load_alltime_pb(athlete_id: int) -> pd.DataFrame:
    """Personale di sempre per specialita' e vasca, per il badge PB."""
    df = query_df(ALLTIME_PB_SQL, (athlete_id,))
    return _num(df, ("pb_alltime_sec", "pool_length"))


@st.cache_data(ttl=TTL, show_spinner=False)
def load_splits(athlete_race_id: int) -> pd.DataFrame:
    df = query_df(SPLITS_SQL, (athlete_race_id,))
    return _num(df, ("seg_sec",))


@st.cache_data(ttl=TTL, show_spinner=False)
def load_splits_by_event(athlete_id: int, stroke: str, distance: str,
                         pool_length: int) -> pd.DataFrame:
    df = query_df(SPLITS_BY_EVENT_SQL, (athlete_id, stroke, distance, int(pool_length)))
    return _num(df, ("time_sec", "seg_sec", "athlete_race_id"))


def split_table(seg_secs: list[float], distance: str | int,
                pool_length: int | None) -> tuple[pd.DataFrame, str | None]:
    """
    Trasforma i tempi di frazione in una tabella leggibile.

    A DB i parziali sono tempi di FRAZIONE (la somma fa il tempo finale) e la
    granularita' e' quasi sempre ogni 50 m, anche in vasca da 25. Qui deduco i
    metri per frazione e restituisco anche un avviso quando i parziali sono
    irregolari o incompleti, invece di etichettare distanze inventate.

    Ritorna (DataFrame, avviso|None).
    """
    seg = [float(s) for s in seg_secs if s is not None]
    if not seg:
        return pd.DataFrame(), None

    n = len(seg)
    try:
        dist_m = int(distance)
    except (TypeError, ValueError):
        dist_m = None

    warn = None
    seg_m = None
    if dist_m and dist_m % n == 0:
        seg_m = dist_m // n
        # un passaggio piu' corto della vasca non ha senso
        if pool_length and seg_m < int(pool_length):
            seg_m, warn = None, "Parziali non allineati alla lunghezza della vasca."
    elif dist_m:
        warn = "Parziali irregolari: le frazioni non dividono la distanza di gara."

    # Frazioni molto sbilanciate = passaggi mancanti (capita nei dati FIN)
    if seg_m and n > 1 and max(seg) > 2.2 * min(seg):
        seg_m, warn = None, ("Parziali incompleti: alcune frazioni sembrano "
                             "accorpate, le distanze non sono affidabili.")

    cum, tot = [], 0.0
    for s in seg:
        tot += s
        cum.append(tot)

    df = pd.DataFrame({
        "frazione": range(1, n + 1),
        "seg_sec": seg,
        "cum_sec": cum,
    })
    df["metri"] = [(i + 1) * seg_m for i in range(n)] if seg_m else [None] * n
    df["etichetta"] = (df["metri"].apply(lambda m: f"{int(m)} m")
                       if seg_m else df["frazione"].apply(lambda i: f"Fraz. {i}"))
    df["delta"] = df["seg_sec"].diff()
    if seg_m:
        df["pace_50"] = df["seg_sec"] * 50.0 / seg_m
    else:
        df["pace_50"] = None
    return df, warn


# ══════════════════════════════════════════════════════════════════
# Confronti e classifiche
# ══════════════════════════════════════════════════════════════════

@st.cache_data(ttl=TTL, show_spinner=False)
def load_compare(athlete_ids: tuple[int, ...], season_year: int) -> pd.DataFrame:
    if not athlete_ids:
        return pd.DataFrame()
    start, end = season_mod.bounds(season_year)
    df = query_df(COMPARE_PB_SQL, (list(athlete_ids), start, end))
    return _num(df, ("pb_sec", "fin_score", "pool_length", "athlete_id"))


@st.cache_data(ttl=TTL, show_spinner=False)
def load_club_ranking(season_year: int) -> pd.DataFrame:
    """
    Miglior tempo di ogni atleta per specialita', vasca e stagione, con la
    categoria master di QUELLA stagione: un 50 stile del 2019 vale nella
    categoria di allora. La banda (20, 25, 30...) serve al filtro, che deve
    valere per maschi e femmine insieme; 0 e' il giovanile.
    """
    start, end = season_mod.bounds(season_year)
    df = query_df(CLUB_RANKING_SQL, (start, end))
    df = _num(df, ("pb_sec", "pool_length", "athlete_id", "birth_year",
                   "stagione"))
    if df.empty:
        return df
    bande, categorie = [], []
    for anno, stagione, sesso in zip(df["birth_year"], df["stagione"], df["sex"]):
        if pd.isna(anno) or pd.isna(stagione):
            bande.append(pd.NA)
            categorie.append("—")
            continue
        banda = season_mod.master_band(int(anno), int(stagione))
        bande.append(banda if banda >= 20 else 0)
        categorie.append(season_mod.master_category(int(anno), int(stagione), sesso))
    df["banda"] = pd.array(bande, dtype="Int64")
    df["categoria"] = categorie
    return df


@st.cache_data(ttl=TTL, show_spinner=False)
def load_fin_leaderboard(season_year: int) -> pd.DataFrame:
    start, end = season_mod.bounds(season_year)
    df = query_df(FIN_LEADERBOARD_SQL, (start, end))
    return _num(df, ("fin_score", "pool_length", "time_sec", "athlete_id"))


# ══════════════════════════════════════════════════════════════════
# Agenda manifestazioni
# ══════════════════════════════════════════════════════════════════

@st.cache_data(ttl=TTL, show_spinner=False)
def load_agenda(season_year: int) -> pd.DataFrame:
    """Manifestazioni del periodo, con quante gare e atleti nostri c'erano."""
    start, end = season_mod.bounds(season_year)
    df = query_df(AGENDA_SQL, (start, end))
    return _num(df, ("comp_id", "nostre_gare", "nostri_atleti"))
