"""
views/confronto.py — due atleti testa a testa.

Niente grafici e niente riepiloghi: si guardano i tempi. Due atleti alla
volta e solo le gare nuotate da tutti e due, se no non e' un confronto.
Sotto a ogni tempo ci sono la data, il punteggio FIN di quella gara e il
nome della manifestazione, che porta al PDF dei risultati.

Il database contiene solo i nostri tesserati, quindi il confronto resta
interno alla squadra.
"""
from __future__ import annotations

import html

import pandas as pd
import streamlit as st

import auth
import data
import season as season_mod
from theme import fmt_int, fmt_time, pool_label, section
from views._common import (apply_pool, inline_filters, page_header,
                           pool_filter, season_year)

TUTTE = "Tutte le gare in comune"

sy = season_year()
page_header("Confronta", "Due atleti testa a testa")

atleti = data.load_athletes(sy)
if atleti.empty or len(atleti) < 2:
    st.info("Servono almeno due atleti con gare nel periodo selezionato.")
    st.stop()

nomi = {int(i): str(n).title()
        for i, n in zip(atleti["athlete_id"], atleti["full_name"])}
ids = list(nomi)

# ══════════════════════════════════════════════════════════════════
# Chi contro chi
# ══════════════════════════════════════════════════════════════════
io_atleta = (auth.current_user() or {}).get("athlete_id")
def_a = next((i for i in (io_atleta, st.session_state.get("athlete_id"))
              if i in nomi), ids[0])
def_b = next((i for i in ids if i != def_a), ids[0])

# Cambiando periodo l'elenco cambia e il valore salvato puo' non esserci
# piu': si sistema prima di creare il widget, cosi' Streamlit non protesta.
for chiave, predefinito in (("conf_a", def_a), ("conf_b", def_b)):
    if st.session_state.get(chiave) not in ids:
        st.session_state[chiave] = predefinito

c1, c2 = st.columns(2)
a = int(c1.selectbox("Atleta", options=ids, key="conf_a",
                     format_func=lambda i: nomi[i]))
b = int(c2.selectbox("Contro", options=ids, key="conf_b",
                     format_func=lambda i: nomi[i]))
if a == b:
    st.info("Scegli due atleti diversi.")
    st.stop()

inline_filters("confronto")

df = apply_pool(data.load_compare((a, b), sy).copy())
if df.empty:
    st.info("Nessun tempo con i filtri selezionati.")
    st.stop()

df["key"] = df["event_label"] + " · " + df["pool_length"].apply(pool_label)

# ══════════════════════════════════════════════════════════════════
# Solo le gare nuotate da entrambi
# ══════════════════════════════════════════════════════════════════
in_comune = set(df.groupby("key")["athlete_id"].nunique()
                .pipe(lambda s: s[s >= 2]).index)
# L'ordine buono e' quello della query: stile, distanza, vasca.
ordine = [k for k in dict.fromkeys(df["key"]) if k in in_comune]

if not ordine:
    st.info(f"{nomi[a]} e {nomi[b]} non hanno gare in comune in "
            f"{season_mod.label(sy).lower()}. Allarga il periodo oppure "
            "togli il filtro vasca.")
    st.stop()

if st.session_state.get("conf_gara") not in [TUTTE] + ordine:
    st.session_state["conf_gara"] = TUTTE
gara = st.selectbox("Gara", options=[TUTTE] + ordine, key="conf_gara",
                    help="In elenco ci sono solo le gare nuotate da tutti e due.")

scelte = ordine if gara == TUTTE else [gara]
dfc = df[df["key"].isin(scelte)]

# ══════════════════════════════════════════════════════════════════
# Tempo contro tempo
# ══════════════════════════════════════════════════════════════════
section(f"Gare in comune · {len(scelte)}")


def _distacco(gap: float) -> str:
    """Sotto il minuto bastano i centesimi, sopra serve il formato gara."""
    return f"+{gap:.2f}" if gap < 60 else f"+{fmt_time(gap)}"


def _lato(r: dict, vince: bool, destra: bool = False) -> str:
    """Tempo, data e punteggio FIN di quella gara, manifestazione col link."""
    classi = " ".join(filter(None, ["vs-side", "vs-dx" if destra else "",
                                    "vincente" if vince else ""]))
    punti = (f' · {fmt_int(r.get("fin_score"))} FIN'
             if pd.notna(r.get("fin_score")) else "")
    quando = pd.to_datetime(r.get("comp_date"))
    data_txt = "—" if pd.isna(quando) else quando.strftime("%d/%m/%Y")

    grezzo = str(r.get("comp_name") or "").strip() or "Manifestazione"
    nome = html.escape(grezzo)
    # Il link chiesto e' il PDF dei risultati; quando manca resta il sito.
    url = (str(r.get("pdf_link") or "").strip()
           or str(r.get("website_link") or "").strip())
    if url.lower().startswith(("http://", "https://")):
        nome = (f'<a href="{html.escape(url, quote=True)}" target="_blank" '
                f'rel="noopener" title="{html.escape(grezzo, quote=True)}">'
                f'{nome}</a>')

    return (f'<div class="{classi}">'
            f'<div class="vs-t">{fmt_time(r["pb_sec"])}</div>'
            f'<div class="vs-meta">{data_txt}{punti}</div>'
            f'<div class="vs-meet">{nome}</div>'
            f'</div>')


mappa = {(r["key"], int(r["athlete_id"])): r for r in dfc.to_dict("records")}
avanti_a = avanti_b = pari = 0
righe = ""
for k in scelte:
    ra, rb = mappa.get((k, a)), mappa.get((k, b))
    if ra is None or rb is None or pd.isna(ra["pb_sec"]) or pd.isna(rb["pb_sec"]):
        continue
    ta, tb = float(ra["pb_sec"]), float(rb["pb_sec"])

    # I tempi a database sono in centesimi: sotto il centesimo e' pari.
    if abs(ta - tb) < 0.005:
        vince_a = vince_b = False
        mezzo = "pari"
        pari += 1
    elif ta < tb:
        vince_a, vince_b, mezzo = True, False, _distacco(tb - ta)
        avanti_a += 1
    else:
        vince_a, vince_b, mezzo = False, True, _distacco(ta - tb)
        avanti_b += 1

    righe += (f'<div class="vs-row">'
              f'<div class="vs-ev">{html.escape(str(k))}</div>'
              f'{_lato(ra, vince_a)}'
              f'<div class="vs-gap">{mezzo}</div>'
              f'{_lato(rb, vince_b, destra=True)}'
              f'</div>')

st.markdown(f'<div class="vs-head">'
            f'<div class="vs-nome">{html.escape(nomi[a])}</div>'
            f'<div class="vs-vs">vs</div>'
            f'<div class="vs-nome vs-dx">{html.escape(nomi[b])}</div>'
            f'</div>{righe}', unsafe_allow_html=True)

totale = avanti_a + avanti_b + pari
if totale:
    if avanti_a > avanti_b:
        bilancio = f"{nomi[a]} avanti in {avanti_a} gare su {totale}"
    elif avanti_b > avanti_a:
        bilancio = f"{nomi[b]} avanti in {avanti_b} gare su {totale}"
    else:
        bilancio = f"Parita', {avanti_a} gare a testa su {totale}"
    if pari:
        bilancio += f", {pari} a pari tempo"
    vasca = pool_filter()
    st.caption(f"{bilancio}. Miglior tempo di ciascuno in "
               f"{season_mod.label(sy).lower()}, "
               f"{'tutte le vasche' if vasca == 'Tutte' else f'vasca {vasca}'}. "
               "Il nome della manifestazione porta al PDF dei risultati.")
