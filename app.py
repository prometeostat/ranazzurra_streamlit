"""
app.py — Master Conegliano · entrypoint.

Navigazione da app: niente barra laterale, una barra fissa in basso con
Agenda, Confronta, Cerca, Profilo e, per il solo amministratore, Gestione.
Cerca e Gestione sono due pagine-indice che portano alle sottopagine.

La navigazione di Streamlit e' in modalita' "hidden": le pagine restano
registrate (servono per st.switch_page e per gli URL) ma il menu lo
disegniamo noi in fondo alla pagina.
"""
from __future__ import annotations

import streamlit as st

import auth
import pwa
import season as season_mod
import theme

st.set_page_config(
    page_title="Master Conegliano",
    page_icon="🌊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Il tema si legge da session_state prima di disegnare: il widget che lo
# cambia sta nel Profilo, ma a inizio rerun il suo valore c'e' gia'.
theme.inject_css()
pwa.enable()

user = auth.require_login()


def _init_state() -> None:
    st.session_state.setdefault("ui_theme", "dark")
    st.session_state.setdefault("pool_filter", "Tutte")
    st.session_state.setdefault("athlete_id", user.get("athlete_id"))
    st.session_state.setdefault("preferiti", [])
    st.session_state.setdefault("scheda_aperta", False)
    # Periodo predefinito: tutte le stagioni, cosi' si parte dallo storico
    # completo e i personali sono quelli veri.
    st.session_state.setdefault("season_year", season_mod.ALL)
    st.session_state.setdefault("stroke_filter", "Tutte le gare")


_init_state()

# ══════════════════════════════════════════════════════════════════
# Pagine
# ══════════════════════════════════════════════════════════════════

PAGINE = {
    "agenda": st.Page("views/agenda.py", title="Agenda", url_path="agenda",
                      default=True),
    "confronta": st.Page("views/confronto.py", title="Confronta",
                         url_path="confronta"),
    "cerca": st.Page("views/cerca.py", title="Cerca", url_path="cerca"),
    "scheda": st.Page("views/scheda.py", title="Scheda atleta",
                      url_path="scheda-atleta"),
    "classifiche": st.Page("views/classifiche.py", title="Classifiche",
                           url_path="classifiche"),
    "profilo": st.Page("views/profilo.py", title="Profilo", url_path="profilo"),
}
if auth.is_admin():
    PAGINE["gestione"] = st.Page("views/gestione.py", title="Gestione",
                                 url_path="gestione")
    PAGINE["atleti"] = st.Page("views/anagrafica.py", title="Anagrafica atleti",
                               url_path="anagrafica-atleti")
    PAGINE["manifestazioni"] = st.Page("views/manifestazioni.py",
                                       title="Anagrafica manifestazioni",
                                       url_path="anagrafica-manifestazioni")

# Voci della barra: (chiave pagina, emoji, etichetta, pagine che la accendono)
VOCI = [
    ("agenda", "📅", "Agenda", {"agenda"}),
    ("confronta", "⚖️", "Confronta", {"confronta"}),
    ("cerca", "🔍", "Cerca", {"cerca", "scheda", "classifiche"}),
    ("profilo", "👤", "Profilo", {"profilo"}),
]
if auth.is_admin():
    VOCI.append(("gestione", "🛠️", "Gestione",
                 {"gestione", "atleti", "manifestazioni"}))

nav = st.navigation(list(PAGINE.values()), position="hidden")


def _pagina_corrente() -> str:
    """Chiave della pagina aperta, confrontando l'url_path."""
    for chiave, pagina in PAGINE.items():
        if pagina.url_path == nav.url_path:
            return chiave
    return "agenda"


def barra_in_basso() -> None:
    """Menu fisso in fondo, stile app. Lo stile sta in theme.py (.st-key-bottombar).

    Si disegna PRIMA del contenuto della pagina: tante pagine chiudono con
    st.stop() quando non hanno niente da mostrare (il selettore atleta, per
    dirne una) e tutto quello che viene dopo non verrebbe mai disegnato, barra
    compresa. Tanto la barra e' in position: fixed, quindi dove sta nel DOM
    non cambia nulla.
    """
    corrente = _pagina_corrente()
    with st.container(key="bottombar"):
        cols = st.columns(len(VOCI))
        for col, (chiave, icona, etichetta, accese) in zip(cols, VOCI):
            attiva = corrente in accese
            if col.button(f"{icona}\n\n{etichetta}", key=f"nav_{chiave}",
                          use_container_width=True,
                          type="primary" if attiva else "secondary"):
                if not attiva or corrente != chiave:
                    st.switch_page(PAGINE[chiave])


barra_in_basso()
nav.run()
