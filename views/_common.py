"""
views/_common.py — pezzi di interfaccia condivisi fra le pagine.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

import auth
import data
import season as season_mod
from theme import fmt_int


# ══════════════════════════════════════════════════════════════════
# Stato condiviso
# ══════════════════════════════════════════════════════════════════

def season_year() -> int:
    return int(st.session_state.get("season_year", season_mod.current_season_year()))


def pool_filter() -> str:
    return st.session_state.get("pool_filter", "Tutte")


# Etichetta mostrata -> nome dello stile a database. A DB la farfalla si
# chiama "Farfalla", in vasca la chiamano tutti delfino.
TUTTE_LE_GARE = "Tutte le gare"
STILI_UI = {
    "Stile Libero": "Stile Libero",
    "Dorso": "Dorso",
    "Rana": "Rana",
    "Delfino": "Farfalla",
    "Misti": "Misti",
}


def stroke_filter() -> str:
    return st.session_state.get("stroke_filter", TUTTE_LE_GARE)


def apply_stroke(df: pd.DataFrame, col: str = "stroke") -> pd.DataFrame:
    scelta = stroke_filter()
    if scelta == TUTTE_LE_GARE or df.empty or col not in df.columns:
        return df
    return df[df[col] == STILI_UI.get(scelta, scelta)].copy()


def apply_pool(df: pd.DataFrame, col: str = "pool_length") -> pd.DataFrame:
    pf = pool_filter()
    if pf == "Tutte" or df.empty or col not in df.columns:
        return df
    return df[df[col] == int(pf.replace("m", ""))].copy()


def anagrafica(sy: int | None = None) -> pd.DataFrame:
    """
    Anagrafica completa per la stagione scelta: chi ha gareggiato piu' chi e'
    solo a ruolino. Serve al selettore atleta, che deve mostrare tutti.
    """
    sy = season_year() if sy is None else sy
    tutti = data.load_all_athletes(sy)
    if tutti.empty:
        return tutti
    return tutti[tutti["is_deleted"] != True].copy()   # noqa: E712


def selected_athlete() -> pd.Series | None:
    """
    L'atleta aperto. Chiunque puo' vedere chiunque: se non e' stato scelto
    nessuno restituisce None e la pagina mostra l'invito a sceglierlo.
    """
    aid = st.session_state.get("athlete_id")
    if aid is None:
        return None
    sy = season_year()
    for df in (data.load_athletes(sy), anagrafica(sy)):
        if df.empty:
            continue
        riga = df[df["athlete_id"] == aid]
        if not riga.empty:
            return riga.iloc[0]
    return None


def apri_atleta(athlete_id: int) -> None:
    """Apre la scheda di un atleta da qualunque punto dell'app."""
    st.session_state["athlete_id"] = int(athlete_id)
    st.session_state["scheda_aperta"] = True


# ══════════════════════════════════════════════════════════════════
# Preferiti (per ora vivono nella sessione, vedi README)
# ══════════════════════════════════════════════════════════════════

def preferiti() -> list[int]:
    return [int(x) for x in st.session_state.get("preferiti", [])]


def e_preferito(athlete_id: int) -> bool:
    return int(athlete_id) in preferiti()


def toggle_preferito(athlete_id: int) -> None:
    pref = preferiti()
    aid = int(athlete_id)
    st.session_state["preferiti"] = [x for x in pref if x != aid] if aid in pref \
        else pref + [aid]


# ══════════════════════════════════════════════════════════════════
# Blocchi di interfaccia
# ══════════════════════════════════════════════════════════════════

def no_athlete_notice() -> None:
    st.info("Scegli un atleta dalla Scheda atleta per vedere questa pagina.")
    st.page_link("views/scheda.py", label="Vai alla scheda atleta →")


def hero(row: pd.Series) -> None:
    initials = (str(row["first_name"])[:1] + str(row["last_name"])[:1]).upper()
    sex_emoji = "♂️" if row["sex"] == "M" else "♀️"
    anno = row.get("birth_year")
    anno = int(anno) if pd.notna(anno) else None
    cat = season_mod.master_category(anno, season_year(), row.get('sex'))
    squadra = row.get("team") or "—"
    st.markdown(f"""
<div class="glass-card" style="border-left:4px solid var(--teal);
     background:linear-gradient(120deg,rgba(0,194,199,0.06),rgba(10,22,40,0.3));">
  <div style="display:flex; align-items:center; gap:20px;">
    <div style="width:70px;height:70px;border-radius:50%;
         background:linear-gradient(135deg,#1a3a6e,#00c2c7);
         display:flex;align-items:center;justify-content:center;
         font-family:'Bebas Neue',sans-serif;font-size:26px;color:#0a1628;
         box-shadow:0 0 30px rgba(0,194,199,0.4);flex-shrink:0;">{initials}</div>
    <div>
      <div class="hero-name">{str(row['full_name']).title()}</div>
      <div class="hero-sub">{squadra}</div>
      <div class="hero-meta">{sex_emoji} {cat}
           &nbsp;·&nbsp; anno <span>{anno if anno else '—'}</span>
           &nbsp;·&nbsp; cod. FIN <span>{fmt_int(row.get('fin_code'))}</span></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    sub = (f'<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:12px;'
           f'letter-spacing:2px;color:var(--muted);text-transform:uppercase">{subtitle}</div>'
           if subtitle else "")
    st.markdown(
        f"""<div style="margin-bottom:8px">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:30px;letter-spacing:4px;
             color:var(--white)">{title}</div>{sub}</div>""",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════
# Filtri in pagina, sincronizzati con la barra laterale
# ══════════════════════════════════════════════════════════════════

def _sync(src: str, dst: str) -> None:
    """Callback: copia il valore del widget di pagina nello stato condiviso."""
    st.session_state[dst] = st.session_state[src]


def inline_filters(prefix: str = "pg", pool: bool = True,
                   strokes: bool = False) -> None:
    """
    Periodo (All Time o singola stagione), vasca e, dove serve, tipo di gara.
    Usa chiavi proprie e ricopia la scelta in season_year / pool_filter /
    stroke_filter con on_change: il callback gira a inizio rerun, quindi la
    barra laterale si ridisegna gia' allineata.
    """
    cols = st.columns([3, 4] if pool else [1])
    seasons = data.load_seasons()
    options = [season_mod.ALL] + seasons
    cur = season_year()
    if cur not in options:
        options = [cur] + options

    k_season = f"{prefix}_season"
    st.session_state[k_season] = cur        # tiene allineato il widget
    cols[0].selectbox("Periodo", options=options, key=k_season,
                      format_func=season_mod.label,
                      on_change=_sync, args=(k_season, "season_year"))

    if pool:
        k_pool = f"{prefix}_pool"
        st.session_state[k_pool] = pool_filter()
        cols[1].radio("Vasca", ["25m", "50m", "Tutte"], horizontal=True, key=k_pool,
                      on_change=_sync, args=(k_pool, "pool_filter"),
                      help="Tutte include anche le gare di fondo, che non hanno "
                           "una lunghezza vasca.")

    if strokes:
        k_stile = f"{prefix}_stile"
        st.session_state[k_stile] = stroke_filter()
        st.radio("Gara", [TUTTE_LE_GARE] + list(STILI_UI), horizontal=True,
                 key=k_stile, on_change=_sync, args=(k_stile, "stroke_filter"))
