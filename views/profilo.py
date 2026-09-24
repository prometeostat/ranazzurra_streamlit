"""
views/profilo.py — account, tema e preferiti.

Qui sono finite le cose che prima stavano nella barra laterale, che adesso
non c'e' piu': la navigazione e' la barra in basso.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

import auth
import data
import season as season_mod
import theme
from views._common import (anagrafica, apri_atleta, page_header, preferiti,
                           season_year, toggle_preferito)

page_header("Profilo", "Account e impostazioni")

user = auth.current_user() or {}
sy = season_year()

# ── Chi sono ──────────────────────────────────────────────────────
mio = user.get("athlete_id")
if mio is not None:
    tutti = anagrafica(sy)
    riga = tutti[tutti["athlete_id"] == mio] if not tutti.empty else pd.DataFrame()
    if not riga.empty:
        r = riga.iloc[0]
        anno = int(r["birth_year"]) if pd.notna(r.get("birth_year")) else None
        st.markdown(
            f'''<div class="glass-card" style="border-left:4px solid var(--teal)">
              <div class="hero-name">{str(r["full_name"]).title()}</div>
              <div class="hero-sub">{r.get("team") or "—"}</div>
              <div class="hero-meta">
                {season_mod.master_category(anno, sy, r.get("sex"))}
                &nbsp;·&nbsp; anno <span>{anno or "—"}</span>
                &nbsp;·&nbsp; cod. FIN <span>{theme.fmt_int(r.get("fin_code"))}</span>
              </div></div>''', unsafe_allow_html=True)
        if st.button("Apri la mia scheda", type="primary", use_container_width=True):
            apri_atleta(int(mio))
            st.switch_page("views/scheda.py")

ruolo = {"admin": "Amministratore", "allenatore": "Allenatore"}.get(
    user.get("role", ""), "Atleta")
st.caption(f"Sei collegato come {user.get('full_name', '—')} · {ruolo}.")

# ── Preferiti ─────────────────────────────────────────────────────
st.markdown('<div class="section-title">Preferiti</div>', unsafe_allow_html=True)
pref = preferiti()
if not pref:
    st.caption("Nessun preferito. La stella si trova nel selettore atleta "
               "della Scheda atleta.")
else:
    tutti = anagrafica(sy)
    elenco = tutti[tutti["athlete_id"].isin(pref)] if not tutti.empty else pd.DataFrame()
    for r in elenco.to_dict("records"):
        aid = int(r["athlete_id"])
        c1, c2, c3 = st.columns([6, 2, 1], vertical_alignment="center")
        c1.markdown(f'<div class="ath-row"><div class="ath-name">'
                    f'{str(r["full_name"]).title()}</div>'
                    f'<div class="ath-team">{r.get("team") or "—"}</div></div>',
                    unsafe_allow_html=True)
        if c2.button("Apri", key=f"pref_apri_{aid}", use_container_width=True):
            apri_atleta(aid)
            st.switch_page("views/scheda.py")
        if c3.button("★", key=f"pref_tog_{aid}", help="Togli dai preferiti"):
            toggle_preferito(aid)
            st.rerun()

# ── Impostazioni ──────────────────────────────────────────────────
st.markdown('<div class="section-title">Impostazioni</div>', unsafe_allow_html=True)


def _salva_tema() -> None:
    """Il tema scelto finisce in una chiave non-widget, se no si perde.

    Streamlit ripulisce lo stato dei widget che non vengono ridisegnati: al
    cambio pagina il radio del tema sparisce e con lui la scelta, e l'app
    tornava scura. La chiave del widget e' sua, il valore buono sta in
    ui_theme e lo rilegge theme.mode() a ogni rerun.
    """
    st.session_state["ui_theme"] = st.session_state["profilo_tema"]


st.session_state["profilo_tema"] = theme.mode()
st.radio("Tema", options=["dark", "light"],
         format_func=lambda m: "Scuro" if m == "dark" else "Chiaro",
         horizontal=True, key="profilo_tema", on_change=_salva_tema)

with st.expander("Installa l'app sul telefono"):
    st.markdown(
        "**iPhone**: apri in Safari, tocca Condividi e poi Aggiungi a Home.  \n"
        "**Android**: menu di Chrome, Aggiungi a schermata Home.  \n\n"
        "Si apre a schermo intero come un'app. Serve la connessione: i dati "
        "arrivano dal database in tempo reale.")

st.markdown("---")
if st.button("Esci", use_container_width=True):
    auth.logout()
