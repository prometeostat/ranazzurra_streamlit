"""
views/cerca.py — pagina indice della sezione Cerca.

Due porte d'ingresso: la scheda di un atleta e le classifiche di squadra.
Sotto, le ultime manifestazioni con il link ai risultati ufficiali.
"""
from __future__ import annotations

import html

import pandas as pd
import streamlit as st

import data
from views._common import page_header, season_year

page_header("Cerca", "Atleti e classifiche")


def _voce(icona: str, titolo: str, sottotitolo: str, pagina: str, chiave: str) -> None:
    """La scheda e' il bottone: icona, titolo e sottotitolo sono tre paragrafi
    dell'etichetta, impaginati dal CSS legato alla chiave hub_*."""
    if st.button(f"{icona}\n\n{titolo}\n\n{sottotitolo}",
                 key=f"hub_{chiave}", use_container_width=True):
        st.switch_page(pagina)


_voce("🏊", "Atleta", "Tempi, personali e storico gara per gara",
      "views/scheda.py", "scheda")
_voce("🏆", "Classifiche", "Per specialita', per categoria e a punti FIN",
      "views/classifiche.py", "classifiche")

# ── Ultime manifestazioni ─────────────────────────────────────────
st.markdown('<div class="section-title">Ultime manifestazioni</div>',
            unsafe_allow_html=True)

agenda = data.load_agenda(season_year()).copy()
if agenda.empty:
    st.info("Nessuna manifestazione nel periodo selezionato.")
else:
    agenda["start_date"] = pd.to_datetime(agenda["start_date"])
    ultime = agenda.sort_values("start_date", ascending=False).head(4)
    blocco = ""
    for r in ultime.to_dict("records"):
        nome = html.escape(str(r.get("nome") or "Manifestazione"))
        url = str(r.get("website_link") or "").strip()
        titolo = (f'<a href="{html.escape(url, quote=True)}" target="_blank" '
                  f'rel="noopener">{nome}</a>') if url.lower().startswith("http") else nome
        blocco += (f'<div class="ag-card">'
                   f'<div class="ag-data">{r["start_date"].strftime("%d/%m/%Y")}</div>'
                   f'<div class="ag-nome">{titolo}</div>'
                   f'<div class="ag-meta">{int(r.get("nostre_gare") or 0)} nostre gare · '
                   f'{int(r.get("nostri_atleti") or 0)} atleti</div></div>')
    st.markdown(blocco, unsafe_allow_html=True)
    if st.button("Vedi tutta l'agenda", use_container_width=True, key="vai_agenda"):
        st.switch_page("views/agenda.py")
