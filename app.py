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
    # Ripiego per chi non e' collegato a una scheda atleta: le stelle di
    # tutti gli altri stanno a database, vedi views/_common.preferiti().
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
    "risultati": st.Page("views/risultati.py", title="Manifestazioni",
                         url_path="manifestazioni"),
    "iscrizioni": st.Page("views/iscrizioni.py", title="Iscrizioni",
                          url_path="iscrizioni"),
    "iscrizioni_nuove": st.Page("views/iscrizioni_nuove.py",
                                title="Iscriviti",
                                url_path="iscriviti"),
    "iscrizioni_modifica": st.Page("views/iscrizioni_modifica.py",
                                   title="Modifica iscrizioni",
                                   url_path="modifica-iscrizioni"),
    "iscrizioni_mie": st.Page("views/iscrizioni_mie.py",
                              title="Le mie iscrizioni",
                              url_path="le-mie-iscrizioni"),
    "profilo": st.Page("views/profilo.py", title="Profilo", url_path="profilo"),
    "novita": st.Page("views/novita.py", title="Novità", url_path="novita"),
}
# Le iscrizioni ricevute le guardano anche gli allenatori, non solo
# l'amministratore: la pagina si registra per tutti e due e dentro c'e' il
# controllo auth.is_staff().
if auth.is_staff():
    PAGINE["gestione"] = st.Page("views/gestione.py", title="Gestione",
                                 url_path="gestione")
    PAGINE["iscrizioni_admin"] = st.Page("views/iscrizioni_admin.py",
                                         title="Iscrizioni gare",
                                         url_path="iscrizioni-gare")
if auth.is_admin():
    PAGINE["atleti"] = st.Page("views/anagrafica.py", title="Anagrafica atleti",
                               url_path="anagrafica-atleti")
    PAGINE["manifestazioni"] = st.Page("views/manifestazioni.py",
                                       title="Anagrafica manifestazioni",
                                       url_path="anagrafica-manifestazioni")
    PAGINE["tempi"] = st.Page("views/tempi.py", title="Inserisci tempi",
                              url_path="inserisci-tempi")
    PAGINE["accessi"] = st.Page("views/accessi.py", title="Registro accessi",
                                url_path="registro-accessi")

# Voci della barra: (chiave pagina, emoji, etichetta, pagine che la accendono)
VOCI = [
    ("agenda", "📅", "Agenda", {"agenda"}),
    ("confronta", "⚖️", "Confronta", {"confronta"}),
    ("cerca", "🔍", "Cerca",
     {"cerca", "scheda", "classifiche", "risultati", "iscrizioni",
      "iscrizioni_nuove", "iscrizioni_modifica", "iscrizioni_mie"}),
    ("profilo", "👤", "Profilo", {"profilo", "novita"}),
]
if auth.is_staff():
    VOCI.append(("gestione", "🛠️", "Gestione",
                 {"gestione", "iscrizioni_admin", "atleti", "manifestazioni",
                  "tempi", "accessi"}))

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


def fascia_emulazione() -> None:
    """
    Avviso fisso quando l'amministratore sta guardando con gli occhi di un
    altro: dice chi, ricorda che e' in sola lettura e offre il rientro.

    Sta qui e non dentro page_header perche' deve comparire su ogni pagina,
    e il bottone legge l'utente VERO: durante l'emulazione i permessi sono
    quelli dell'atleta, quindi un controllo su is_admin() chiuderebbe la
    porta da dentro.
    """
    if not auth.in_emulazione():
        return
    finto = auth.current_user() or {}
    vero = auth.utente_vero() or {}
    c_testo, c_btn = st.columns([4, 1.5], vertical_alignment="center")
    c_testo.warning(
        f"Stai guardando l'app come **{str(finto.get('full_name', '')).title()}**, "
        "in sola lettura. Sei collegato come "
        f"{str(vero.get('full_name', '')).title()}.", icon="👁")
    if c_btn.button("Torna me stesso", type="primary",
                    use_container_width=True, key="fine_emulazione"):
        auth.smetti_emulazione()
        st.session_state["athlete_id"] = vero.get("athlete_id")
        # Un rerun e basta: si resta dov'eravamo, ma con i propri occhi e
        # con le pagine riservate di nuovo in elenco. Uno switch_page qui
        # non potrebbe puntare a una pagina admin, che in questo giro non e'
        # nemmeno registrata.
        st.rerun()


barra_in_basso()
fascia_emulazione()
nav.run()
