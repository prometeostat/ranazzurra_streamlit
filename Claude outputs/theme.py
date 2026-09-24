"""
theme.py — palette chiara/scura, CSS globale e helper di formattazione.

Il tema si sceglie a runtime dalla barra laterale: la scelta sta in
st.session_state["ui_theme"] ("dark" o "light") e viene letta all'inizio di
ogni rerun, prima di disegnare qualsiasi cosa.

Due livelli di colore:
  - l'HTML usa le variabili CSS (--teal, --muted, ...), che cambiano da sole;
  - i grafici Plotly prendono i colori da palette(), perche' Plotly vuole
    valori espliciti e non capisce var().
"""
from __future__ import annotations

import math
import streamlit as st

# ── Colori dei tracciati, uno per tema ────────────────────────────
_MARKS = {
    "dark": {
        "teal": "#00c2c7", "teal2": "#00e5ea", "gold": "#f0b429",
        "green": "#00e676", "red": "#ff4d6d", "purple": "#9b59b6",
        "muted": "#a4b6d2", "text": "#f5f8ff",
        "grid": "rgba(255,255,255,0.06)", "zero": "rgba(255,255,255,0.10)",
        "marker_edge": "#0a1628", "ghost": "rgba(255,255,255,0.07)",
        "silver": "#c0c0c0", "bronze": "#cd7f32",
    },
    "light": {
        "teal": "#00838a", "teal2": "#006a70", "gold": "#b8780a",
        "green": "#0a8f4d", "red": "#d02b4c", "purple": "#7b45b0",
        "muted": "#5b6b85", "text": "#0a1628",
        "grid": "rgba(10,22,40,0.08)", "zero": "rgba(10,22,40,0.14)",
        "marker_edge": "#ffffff", "ghost": "rgba(10,22,40,0.07)",
        "silver": "#9aa2ad", "bronze": "#b5722c",
    },
}

# Costanti storiche, tema scuro. Il codice nuovo usa palette().
TEAL, TEAL2 = "#00c2c7", "#00e5ea"
GOLD, GREEN, RED, MUTED, WHITE = "#f0b429", "#00e676", "#ff4d6d", "#7a8fb5", "#f0f4ff"
NAVY, NAVY2 = "#0a1628", "#111f3a"

RESP_H, RESP_H_TALL, RESP_H_SMALL = 340, 400, 280


def mode() -> str:
    """Tema attivo in questo rerun."""
    return "light" if st.session_state.get("ui_theme") == "light" else "dark"


def is_light() -> bool:
    return mode() == "light"


def palette() -> dict:
    """Colori per i grafici, coerenti col tema attivo."""
    return _MARKS[mode()]


def series_colors() -> list[str]:
    p = palette()
    return [p["teal"], p["gold"], p["green"], p["purple"], p["red"],
            "#5dade2", "#f39c12"]


# Compatibilita' con il codice che importava SERIES_COLORS
SERIES_COLORS = [TEAL, GOLD, GREEN, "#9b59b6", RED, "#5dade2", "#f39c12"]

STROKE_COLORS = {
    "Stile Libero": TEAL, "Dorso": GOLD, "Rana": GREEN,
    "Farfalla": "#9b59b6", "Misti": RED,
}


# ══════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════

_FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&'
          'family=Barlow+Condensed:wght@300;400;600;700&'
          'family=Barlow:wght@300;400;500&display=swap" rel="stylesheet">')

_ROOT_DARK = """
:root {
    --teal:   #00c2c7;
    --teal2:  #00e5ea;
    --gold:   #f0b429;
    --green:  #00e676;
    --red:    #ff4d6d;
    --white:  #f5f8ff;
    --muted:  #a4b6d2;
    --sky:    #b9d2f0;
    --border: rgba(0,194,199,0.20);
    --glass:  rgba(255,255,255,0.04);
    --glass2: rgba(255,255,255,0.08);
    --bg1: #0a1628; --bg2: #111f3a; --bg3: #0d1f3c;
    --sidebar: rgba(10,22,40,0.95);
    --shadow: rgba(0,194,199,0.40);
    --hairline: rgba(255,255,255,0.12);
}
"""

_ROOT_LIGHT = """
:root {
    --teal:   #00838a;
    --teal2:  #006a70;
    --gold:   #b8780a;
    --green:  #0a8f4d;
    --red:    #d02b4c;
    --white:  #0e1b30;
    --muted:  #55657f;
    --sky:    #1e4f7c;
    --border: rgba(0,131,138,0.22);
    --glass:  rgba(255,255,255,0.75);
    --glass2: rgba(10,22,40,0.05);
    --bg1: #eef3fb; --bg2: #f7fafe; --bg3: #e9f1f8;
    --sidebar: rgba(255,255,255,0.94);
    --shadow: rgba(0,131,138,0.22);
    --hairline: rgba(10,22,40,0.08);
}
"""

# Ritocchi che servono solo sul chiaro: i widget di Streamlit nascono scuri
# perche' il tema di config.toml e' dark.
_LIGHT_FIXES = """
.stApp, .stApp p, .stApp span, .stApp label, .stApp li,
section[data-testid="stSidebar"] * { color: var(--white); }
section[data-testid="stSidebar"] { box-shadow: 0 0 24px rgba(10,22,40,0.06); }
.glass-card, .glass-card-accent, .kpi-wrap {
    box-shadow: 0 2px 10px rgba(10,22,40,0.06);
}
input, textarea, .stTextInput input, .stDateInput input {
    background: #ffffff !important; color: var(--white) !important;
}
div[data-baseweb="select"] > div, div[data-baseweb="popover"] div {
    background: #ffffff !important; color: var(--white) !important;
}
div[data-baseweb="calendar"] { background: #ffffff !important; }
/* Bottoni, bottoni di form e link-bottoni: sul chiaro nascono scuri perche'
   il tema di config.toml e' dark. Attenzione: mai scrivere parentesi angolari
   nei commenti di questo CSS, il sanitizer di st.html le legge come tag e
   scarta l'intero blocco di stile. */
.stButton button, .stFormSubmitButton button, .stDownloadButton button,
a[data-testid^="stBaseLinkButton"] {
    background: #ffffff !important;
    color: var(--white) !important;
    border: 1px solid var(--border) !important;
}
.stButton button:hover, .stFormSubmitButton button:hover,
.stDownloadButton button:hover, a[data-testid^="stBaseLinkButton"]:hover {
    border-color: var(--teal) !important; color: var(--teal) !important;
}
a[data-testid^="stBaseLinkButton"] p { color: inherit !important; }
/* I primari restano pieni di teal, altrimenti sparisce la gerarchia */
button[data-testid*="primary"], a[data-testid*="stBaseLinkButton-primary"] {
    background: var(--teal) !important;
    color: #ffffff !important;
    border-color: var(--teal) !important;
}
button[data-testid*="primary"] p { color: #ffffff !important; }

/* Pallini dei radio: il cerchio precede l'input nel DOM, quindi lo stato
   selezionato si prende con :has() e non con un selettore fratello. */
label[data-baseweb="radio"] > div:first-child {
    background-color: #ffffff !important;
    border: 1px solid var(--muted) !important;
    box-shadow: none !important;
}
label[data-baseweb="radio"] > div:first-child > div {
    background-color: #ffffff !important;
}
label[data-baseweb="radio"]:has(input:checked) > div:first-child {
    background-color: var(--teal) !important;
    border-color: var(--teal) !important;
}
label[data-baseweb="radio"]:has(input:checked) > div:first-child > div {
    background-color: #ffffff !important;
}

/* Barra in alto dell'app: resta navy se non la si schiarisce */
header[data-testid="stHeader"] { background: transparent !important; }
/* st.dataframe disegna su canvas col tema del server, che resta scuro:
   l'inversione lo riallinea al fondo chiaro. Togli questa regola se preferisci
   impostare base = "light" in .streamlit/config.toml. */
div[data-testid="stDataFrame"], div[data-testid="stTable"] {
    filter: invert(0.92) hue-rotate(180deg);
    border-radius: 10px; overflow: hidden;
}
"""

_BASE = """
.stApp {
    background: linear-gradient(135deg, var(--bg1) 0%, var(--bg2) 60%, var(--bg3) 100%);
    background-attachment: fixed;
}
section[data-testid="stSidebar"] {
    background: var(--sidebar) !important;
    border-right: 1px solid var(--border);
}
html, body, [class*="css"] { font-family: 'Barlow', sans-serif !important; color: var(--white); }
h1, h2, h3 { font-family: 'Bebas Neue', sans-serif !important; letter-spacing: 3px; }

.sidebar-logo { font-family:'Bebas Neue',sans-serif; font-size:28px; letter-spacing:4px;
                color:var(--teal); text-align:center; padding:12px 0 4px; }
.sidebar-sub  { font-family:'Barlow Condensed',sans-serif; font-size:11px; letter-spacing:2px;
                color:var(--muted); text-align:center; text-transform:uppercase; margin-bottom:20px; }
.season-pill {
    display:inline-block; background:rgba(240,180,41,0.12);
    border:1px solid rgba(240,180,41,0.35); border-radius:20px; padding:4px 16px;
    font-family:'Barlow Condensed',sans-serif; font-size:12px; font-weight:700;
    letter-spacing:2px; color:var(--gold); text-transform:uppercase;
}

/* Scheda identita' nella sidebar */
.id-card {
    background: var(--glass); border:1px solid var(--border); border-radius:12px;
    padding:12px 14px; margin-bottom:12px; text-align:center;
}
.id-name { font-family:'Bebas Neue',sans-serif; font-size:20px; letter-spacing:2px;
           color:var(--white); line-height:1.1; }
.id-cat  { display:inline-block; margin-top:6px; padding:2px 12px; border-radius:20px;
           background:rgba(0,194,199,0.14); border:1px solid var(--border);
           font-family:'Bebas Neue',sans-serif; font-size:18px; letter-spacing:2px;
           color:var(--teal); }
.id-meta { font-family:'Barlow Condensed',sans-serif; font-size:11px; letter-spacing:1px;
           color:var(--muted); margin-top:6px; line-height:1.6; }

.glass-card {
    background: var(--glass); border:1px solid var(--border); border-radius:14px;
    padding:24px 28px; backdrop-filter: blur(10px); margin-bottom:20px;
}
.glass-card-accent {
    background: var(--glass); border:1px solid var(--border); border-left:4px solid var(--teal);
    border-radius:14px; padding:20px 24px; backdrop-filter: blur(10px); margin-bottom:16px;
}

.hero-name { font-family:'Bebas Neue',sans-serif; font-size:52px; letter-spacing:5px;
             color:var(--white); line-height:1; margin:0; }
.hero-sub  { font-family:'Barlow Condensed',sans-serif; font-size:14px; letter-spacing:2px;
             color:var(--sky); text-transform:uppercase; margin-top:4px; }
.hero-meta { font-family:'Barlow Condensed',sans-serif; font-size:13px; color:var(--muted);
             letter-spacing:1px; margin-top:2px; }
.hero-meta span { color:var(--white); font-weight:600; }

.kpi-wrap { text-align:center; padding:18px 12px; background:var(--glass);
            border:1px solid var(--border); border-radius:12px; }
.kpi-val  { font-family:'Bebas Neue',sans-serif; font-size:46px; line-height:1; color:var(--teal); }
.kpi-val.gold  { color:var(--gold); }
.kpi-val.green { color:var(--green); }
.kpi-val.small { font-size:34px; }
.kpi-lbl  { font-family:'Barlow Condensed',sans-serif; font-size:11px; letter-spacing:2px;
            color:var(--muted); text-transform:uppercase; margin-top:2px; }

.section-title { font-family:'Bebas Neue',sans-serif; font-size:22px; letter-spacing:4px;
                 color:var(--sky); border-bottom:1px solid var(--border);
                 padding-bottom:8px; margin:28px 0 16px; }

.rank-1 { background:#f0b429; color:#0a1628; padding:2px 10px; border-radius:4px;
          font-weight:800; font-family:'Bebas Neue',sans-serif; font-size:18px; }
.rank-2 { background:#c0c0c0; color:#0a1628; padding:2px 10px; border-radius:4px;
          font-weight:800; font-family:'Bebas Neue',sans-serif; font-size:18px; }
.rank-3 { background:#cd7f32; color:#fff; padding:2px 10px; border-radius:4px;
          font-weight:800; font-family:'Bebas Neue',sans-serif; font-size:18px; }
.rank-n { background:var(--glass2); color:var(--muted); padding:2px 10px; border-radius:4px;
          font-weight:600; font-family:'Barlow Condensed',sans-serif; }

.delta-pos { color:var(--green); font-weight:700; }
.delta-neg { color:var(--red);   font-weight:700; }
.delta-neu { color:var(--muted); }

.event-pill { display:inline-block; background:rgba(0,194,199,0.12);
              border:1px solid var(--border); border-radius:4px; padding:2px 10px;
              font-family:'Barlow Condensed',sans-serif; font-size:13px; font-weight:600;
              color:var(--teal2); }
.badge-cat  { display:inline-block; background:rgba(240,180,41,0.12);
              border:1px solid rgba(240,180,41,0.30); border-radius:4px; padding:1px 8px;
              font-family:'Barlow Condensed',sans-serif; font-size:12px; font-weight:700;
              color:var(--gold); }

.race-row { display:flex; align-items:center; justify-content:space-between; gap:12px;
            padding:10px 14px; margin-bottom:8px; background:var(--glass);
            border:1px solid var(--border); border-left:3px solid var(--teal);
            border-radius:10px; font-family:'Barlow Condensed',sans-serif; }

/* ── Elenco gare raggruppato per specialita' ── */
.combo-box { margin-bottom:14px; }
.combo-head {
    display:flex; align-items:baseline; justify-content:space-between; gap:10px;
    padding:0 4px 6px; border-bottom:1px solid var(--hairline); margin-bottom:6px;
}
.combo-name { font-family:'Barlow Condensed',sans-serif; font-size:17px;
              font-weight:700; letter-spacing:1px; color:var(--white); }
.combo-pb   { font-family:'Barlow Condensed',sans-serif; font-size:12px;
              letter-spacing:1px; color:var(--muted); white-space:nowrap; }
.evt-season { font-family:'Bebas Neue',sans-serif; font-size:20px;
              letter-spacing:2px; color:var(--teal); line-height:1.1; }
.evt-gap    { font-family:'Barlow Condensed',sans-serif; font-size:13px;
              color:var(--muted); margin-left:6px; }
.evt-meet   { font-family:'Barlow Condensed',sans-serif; font-size:13px;
              letter-spacing:0.5px; margin-top:1px; }
.evt-meet a { color:var(--teal); text-decoration:none; }
.evt-meet a:hover { text-decoration:underline; }
.meet-city a { color:inherit; text-decoration:none; }
.meet-city a:hover { color:var(--teal); }

/* ── Barra di navigazione in basso (stile app) ── */
.st-key-bottombar {
    position: fixed; left: 0; right: 0; bottom: 0; z-index: 9990;
    background: var(--sidebar);
    border-top: 1px solid var(--border);
    backdrop-filter: blur(14px);
    padding: 6px 6px calc(6px + env(safe-area-inset-bottom, 0px));
    box-shadow: 0 -6px 20px rgba(0,0,0,0.18);
}
/* Le colonne di Streamlit si impilano sotto i 640px: qui no, devono restare
   affiancate come in una tab bar. */
.st-key-bottombar [data-testid="stHorizontalBlock"] {
    gap: 2px !important; flex-wrap: nowrap !important; align-items: stretch;
}
.st-key-bottombar [data-testid="stColumn"] {
    flex: 1 1 0 !important; width: auto !important;
    min-width: 0 !important; padding: 0 !important;
}
.st-key-bottombar .stButton button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: var(--muted) !important;
    flex-direction: column !important;
    gap: 2px !important;
    padding: 6px 2px !important;
    min-height: 54px;
    border-radius: 14px !important;
}
.st-key-bottombar .stButton button p {
    font-family: 'Barlow Condensed', sans-serif !important;
    letter-spacing: 0.5px; margin: 0 !important; color: inherit !important;
}
/* l'etichetta e' due paragrafi: icona sopra, testo sotto */
.st-key-bottombar .stButton button p:first-child {
    font-size: 21px !important; line-height: 1.15 !important;
}
.st-key-bottombar .stButton button p:last-child { font-size: 11px !important; }
.st-key-bottombar .stButton button:hover { color: var(--teal) !important; }
.st-key-bottombar .nav-attiva .stButton button,
.st-key-bottombar .stButton button[kind="primary"] {
    background: var(--glass2) !important;
    color: var(--teal) !important;
}
/* spazio sotto al contenuto, se no la barra copre l'ultima riga */
.block-container { padding-bottom: 92px !important; }

/* La barra laterale sparisce: la navigazione sta in basso */
section[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"] { display: none !important; }

/* ── Voci hub (Cerca, Gestione): la scheda e' il bottone ──
   L'etichetta del bottone e' icona, titolo e sottotitolo separati da righe
   vuote: Streamlit li rende come tre paragrafi, che la griglia qui sotto
   dispone come una card. La chiave del bottone inizia per hub_ e Streamlit
   la mette come classe st-key-hub_... sul contenitore. */
div[class*="st-key-hub_"] .stButton button {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    box-shadow: none !important;
    padding: 14px 18px !important;
    margin-bottom: 2px;
    text-align: left !important;
    justify-content: flex-start !important;
}
div[class*="st-key-hub_"] .stButton button:hover {
    background: var(--glass2) !important;
    border-color: var(--teal) !important;
}
div[class*="st-key-hub_"] .stButton button div[data-testid="stMarkdownContainer"] {
    display: grid !important;
    grid-template-columns: 46px 1fr;
    column-gap: 14px; row-gap: 0;
    align-items: center; width: 100%;
}
div[class*="st-key-hub_"] .stButton button p {
    font-family: 'Barlow Condensed', sans-serif !important;
    margin: 0 !important; text-align: left !important;
}
div[class*="st-key-hub_"] .stButton button p:first-child {
    grid-column: 1; grid-row: 1 / span 2;
    width: 46px; height: 46px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px !important; line-height: 1 !important;
    background: rgba(0,194,199,0.14);
    border: 1px solid var(--border);
}
div[class*="st-key-hub_"] .stButton button p:nth-child(2) {
    grid-column: 2; grid-row: 1; align-self: end;
    font-size: 20px !important; font-weight: 700 !important;
    letter-spacing: 0.5px; line-height: 1.15 !important;
    color: var(--white) !important;
}
div[class*="st-key-hub_"] .stButton button p:last-child {
    grid-column: 2; grid-row: 2; align-self: start;
    font-size: 13px !important; font-weight: 400 !important;
    line-height: 1.3 !important; color: var(--muted) !important;
}
div[class*="st-key-hub_"] .stButton button:hover p:nth-child(2) {
    color: var(--teal) !important;
}

/* ── Agenda ── */
.ag-card {
    background: var(--glass); border: 1px solid var(--border);
    border-left: 3px solid var(--teal); border-radius: 14px;
    padding: 12px 16px; margin-bottom: 8px;
}
.ag-data { font-family:'Bebas Neue',sans-serif; font-size:19px; letter-spacing:2px;
           color:var(--teal); }
.ag-nome { font-family:'Barlow Condensed',sans-serif; font-size:17px; font-weight:600;
           color:var(--white); line-height:1.25; }
.ag-meta { font-family:'Barlow Condensed',sans-serif; font-size:12px; color:var(--muted);
           letter-spacing:0.5px; margin-top:2px; }
.ag-meta a { color:var(--teal); text-decoration:none; }
.ag-meta a:hover { text-decoration:underline; }
.ag-futura { border-left-color: var(--gold); }
.ag-futura .ag-data { color: var(--gold); }

/* ── Righe del selettore atleta ── */
.ath-row {
    background: var(--glass); border:1px solid var(--border); border-radius:12px;
    padding:10px 14px;
}
.ath-name { font-family:'Barlow Condensed',sans-serif; font-size:19px; font-weight:600;
            color:var(--white); letter-spacing:0.5px; line-height:1.2; }
.ath-meta { font-family:'Barlow Condensed',sans-serif; font-size:13px; color:var(--muted); }
.ath-team { font-family:'Barlow Condensed',sans-serif; font-size:13px; color:var(--teal); }

/* ── Blocchi manifestazione (ultime gare) ── */
.meet-card {
    background: var(--glass); border:1px solid var(--border); border-radius:14px;
    padding:14px 16px; margin-bottom:6px; min-height:150px;
}
.meet-card:hover { border-color: var(--teal); }
/* Il blocchetto e' tutto un link ai risultati ufficiali: niente bottone
   Dettaglio sotto. */
a.meet-link { display:block; text-decoration:none; color:inherit; }
a.meet-link .meet-card { transition: border-color .15s, background .15s; }
a.meet-link:hover .meet-card {
    border-color: var(--teal); background: var(--glass2);
}
.meet-go { font-size:15px; letter-spacing:0; color:var(--teal); margin-left:6px; }
.meet-city { font-family:'Bebas Neue',sans-serif; font-size:22px; letter-spacing:2px;
             color:var(--white); line-height:1.1; }
.meet-meta { font-family:'Barlow Condensed',sans-serif; font-size:12px; letter-spacing:1px;
             color:var(--muted); margin-bottom:8px; }
.meet-line { display:flex; justify-content:space-between; gap:10px;
             font-family:'Barlow Condensed',sans-serif; font-size:13px;
             padding:3px 0; border-bottom:1px solid var(--hairline); }
.meet-line:last-child { border-bottom:none; }
.meet-ev { color:var(--muted); }
.meet-t  { color:var(--white); font-weight:600; white-space:nowrap; }

/* ── Confronto testa a testa ──
   Tre colonne: tempo di uno, distacco, tempo dell'altro. Sotto a ogni tempo
   data, punteggio FIN e manifestazione. Il piu' veloce sta dentro una
   pastiglia accesa, cosi' si vede da lontano chi ha vinto. */
.vs-head {
    display:grid; grid-template-columns:1fr auto 1fr; align-items:end; gap:8px;
    padding:2px 12px 8px; margin-bottom:10px;
    border-bottom:1px solid var(--border);
}
.vs-nome { font-family:'Bebas Neue',sans-serif; font-size:19px; letter-spacing:1.5px;
           color:var(--white); line-height:1.15; }
.vs-vs   { font-family:'Barlow Condensed',sans-serif; font-size:11px; letter-spacing:2px;
           text-transform:uppercase; color:var(--muted); }
.vs-row {
    display:grid; grid-template-columns:1fr auto 1fr; align-items:start; gap:6px;
    padding:10px 12px; margin-bottom:8px; background:var(--glass);
    border:1px solid var(--border); border-radius:12px;
}
.vs-ev { grid-column:1 / -1; font-family:'Barlow Condensed',sans-serif; font-size:12px;
         letter-spacing:1.5px; text-transform:uppercase; color:var(--muted);
         margin-bottom:4px; }
.vs-side { min-width:0; padding:6px 8px; border-radius:10px;
           border:1px solid transparent; }
.vs-side.vincente { background:rgba(0,194,199,0.12); border-color:var(--border); }
.vs-t  { font-family:'Bebas Neue',sans-serif; font-size:24px; letter-spacing:1px;
         color:var(--muted); line-height:1.1; }
.vs-side.vincente .vs-t { color:var(--teal2); }
.vs-meta { font-family:'Barlow Condensed',sans-serif; font-size:11px; letter-spacing:0.5px;
           color:var(--muted); margin-top:2px; }
.vs-meet { font-family:'Barlow Condensed',sans-serif; font-size:12px; margin-top:1px;
           color:var(--muted); overflow:hidden; text-overflow:ellipsis;
           white-space:nowrap; }
.vs-meet a { color:var(--sky); text-decoration:none; }
.vs-meet a:hover { text-decoration:underline; }
.vs-gap { font-family:'Barlow Condensed',sans-serif; font-size:12px; color:var(--muted);
          white-space:nowrap; text-align:center; padding-top:12px; }
.vs-dx { text-align:right; }

/* ── Elenco per stile ── */
.stroke-head {
    font-family:'Bebas Neue',sans-serif; font-size:24px; letter-spacing:3px;
    color:var(--sky); margin:22px 0 8px; padding-bottom:4px;
    border-bottom:1px solid var(--border);
}
.evt-row {
    display:flex; align-items:center; justify-content:space-between; gap:12px;
    padding:12px 16px; margin-bottom:8px; background:var(--glass);
    border:1px solid var(--border); border-radius:12px;
}
.evt-name { font-family:'Barlow Condensed',sans-serif; font-size:17px; font-weight:600;
            color:var(--white); letter-spacing:0.5px; }
.evt-meta { font-family:'Barlow Condensed',sans-serif; font-size:12px; color:var(--muted);
            letter-spacing:1px; margin-top:2px; }
.evt-time { font-family:'Bebas Neue',sans-serif; font-size:30px; letter-spacing:1px;
            color:var(--white); line-height:1; white-space:nowrap; }
.evt-time.pb { color:var(--gold); }
.pb-badge { display:inline-block; margin-left:6px; padding:1px 7px; border-radius:4px;
            background:rgba(240,180,41,0.14); border:1px solid rgba(240,180,41,0.35);
            font-family:'Barlow Condensed',sans-serif; font-size:11px; font-weight:700;
            letter-spacing:1px; color:var(--gold); vertical-align:middle; }
@media (max-width: 768px) {
    .evt-time { font-size:24px; }
    .meet-card { min-height:0; }
}

.stSelectbox > div > div, .stMultiSelect > div > div {
    background: var(--glass2) !important; border:1px solid var(--border) !important;
    border-radius:8px !important;
}
div[data-testid="stMetricValue"] { font-family:'Bebas Neue',sans-serif !important;
                                   font-size:36px !important; color:var(--teal) !important; }
.stTabs [data-baseweb="tab-list"] { background:transparent; border-bottom:1px solid var(--border);
                                    gap:4px; }
.stTabs [data-baseweb="tab"] { font-family:'Barlow Condensed',sans-serif !important;
    font-size:14px !important; font-weight:600 !important; letter-spacing:1.5px !important;
    text-transform:uppercase !important; color:var(--muted) !important;
    background:transparent !important; border:none !important; }
.stTabs [aria-selected="true"] { color:var(--teal) !important;
                                 border-bottom:2px solid var(--teal) !important; }
.stDataFrame { background:transparent !important; }
footer { display:none !important; }
#MainMenu { display:none !important; }

@media (max-width: 768px) {
    .hero-name { font-size:30px !important; letter-spacing:2px !important; }
    .hero-sub, .hero-meta { font-size:12px !important; }
    .kpi-val { font-size:30px !important; }
    .kpi-val.small { font-size:24px !important; }
    .kpi-lbl { font-size:10px !important; }
    .kpi-wrap { padding:12px 6px !important; }
    .section-title { font-size:18px !important; letter-spacing:2px !important; }
    .glass-card { padding:16px !important; }
    .block-container { padding-left:12px !important; padding-right:12px !important;
                       padding-top:12px !important; }
    table { min-width:560px; }
    .js-plotly-plot, .plotly, .main-svg { width:100% !important; }
    .race-row { flex-wrap:wrap; }
}
@media (display-mode: standalone) { .block-container { padding-top:28px !important; } }
.js-plotly-plot .plotly .main-svg { max-width:100% !important; height:auto !important; }
"""


def inject_css() -> None:
    """Da chiamare una volta per rerun, subito dopo set_page_config."""
    root = _ROOT_LIGHT if is_light() else _ROOT_DARK
    extra = _LIGHT_FIXES if is_light() else ""
    st.html(f"{_FONTS}<style>{root}{_BASE}{extra}</style>")


# ══════════════════════════════════════════════════════════════════
# Formattazione
# ══════════════════════════════════════════════════════════════════

def fmt_time(sec: float | None) -> str:
    """
    Secondi -> formato gara:
        28.14"        sotto il minuto
        1:05.43       sotto l'ora
        01:29:18.50   dall'ora in su (fondo, 1500, maratone)
    """
    if sec is None or (isinstance(sec, float) and math.isnan(sec)):
        return "—"
    sec = float(sec)
    segno = "-" if sec < 0 else ""
    sec = abs(sec)
    ore = int(sec // 3600)
    minuti = int((sec % 3600) // 60)
    resto = sec % 60
    if ore:
        return f"{segno}{ore:02d}:{minuti:02d}:{resto:05.2f}"
    if minuti:
        return f"{segno}{minuti}:{resto:05.2f}"
    return f"{segno}{resto:.2f}\""


def fmt_delta(sec: float | None) -> str:
    if sec is None or (isinstance(sec, float) and math.isnan(sec)):
        return "—"
    return f"{'+' if sec > 0 else ''}{sec:.2f}"


def delta_html(d: float | None, unit: str = "s") -> str:
    """Nel nuoto meno e' meglio: il segno negativo e' verde."""
    if d is None or (isinstance(d, float) and math.isnan(d)):
        return '<span class="delta-neu">—</span>'
    sign = "+" if d > 0 else ""
    cls = "delta-neg" if d > 0 else "delta-pos"
    return f'<span class="{cls}">{sign}{d:.2f}{unit}</span>'


def rank_html(r: int) -> str:
    if r == 1:
        return '<span class="rank-1">🥇 1°</span>'
    if r == 2:
        return '<span class="rank-2">🥈 2°</span>'
    if r == 3:
        return '<span class="rank-3">🥉 3°</span>'
    return f'<span class="rank-n">{r}°</span>'


def improvement_grade(pct: float | None) -> tuple[str, str]:
    if pct is None:
        return ("—", "Nessun confronto disponibile")
    if pct < -3.0:
        return ("A+", "Miglioramento eccellente")
    if pct < -1.5:
        return ("A", "Ottimo miglioramento")
    if pct < -0.5:
        return ("B", "Buon progresso")
    if pct < 0.0:
        return ("C+", "Leggero miglioramento")
    if pct < 1.0:
        return ("C", "Prestazione stabile")
    return ("D", "Tempo in calo")


def fmt_int(v) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "—"
    try:
        return str(int(v))
    except (ValueError, TypeError):
        return str(v)


def pool_label(v, breve: bool = False) -> str:
    """
    Etichetta della vasca. A DB le gare di fondo hanno pool_length uguale alla
    distanza (3000, 3300, 5000), quindi tutto cio' che non e' 25 o 50 e'
    acqua libera e non va scritto come "vasca 5000m".
    """
    try:
        n = int(v)
    except (TypeError, ValueError):
        return "—"
    if n in (25, 50):
        return f"{n}m" if breve else f"vasca {n}m"
    return "acque libere"


def section(title: str) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def kpi(value: str, label: str, tone: str = "") -> str:
    small = " small" if len(str(value)) > 6 else ""
    return (f'<div class="kpi-wrap"><div class="kpi-val {tone}{small}">{value}</div>'
            f'<div class="kpi-lbl">{label}</div></div>')


# ══════════════════════════════════════════════════════════════════
# Plotly
# ══════════════════════════════════════════════════════════════════

def plotly_layout(title: str = "") -> dict:
    p = palette()
    return dict(
        title=dict(text=title, font=dict(family="Bebas Neue", size=18, color=p["teal2"]), x=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Barlow Condensed", color=p["muted"]),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=p["muted"])),
        margin=dict(l=10, r=10, t=40, b=10),
        autosize=True,
    )


def apply_axes(fig):
    p = palette()
    fig.update_xaxes(gridcolor=p["grid"], zerolinecolor=p["zero"])
    fig.update_yaxes(gridcolor=p["grid"], zerolinecolor=p["zero"])
    return fig


def chart(fig, height: int = RESP_H) -> None:
    fig.update_layout(height=height)
    st.plotly_chart(fig, use_container_width=True,
                    config={"responsive": True, "displayModeBar": False})
