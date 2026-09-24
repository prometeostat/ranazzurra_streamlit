"""
views/classifiche.py — classifica interna di squadra, una schermata sola.

Si sceglie la specialita' e, volendo, la categoria: senza filtro escono i
migliori tempi assoluti, con il filtro i migliori di quella categoria.
Maschi e femmine sono due classifiche separate, come in gara.

La categoria e' quella della stagione in cui il tempo e' stato nuotato: le
fasce FIN si spostano ogni anno, quindi un tempo del 2019 va confrontato
con la categoria di allora, non con quella di oggi.
"""
from __future__ import annotations

import html

import pandas as pd
import streamlit as st

import auth
import data
import season as season_mod
from theme import fmt_time, pool_label, rank_html, section
from views._common import apply_pool, inline_filters, page_header, season_year

TOP = 5
TUTTE_CAT = "Tutte le categorie"

sy = season_year()
page_header("Classifiche", "Master Conegliano")
inline_filters("classifiche")

rk = apply_pool(data.load_club_ranking(sy).copy())
if rk.empty:
    st.info("Nessun tempo con i filtri selezionati.")
    st.stop()

rk["key"] = rk["event_label"] + " · " + rk["pool_length"].apply(pool_label)
me = (auth.current_user() or {}).get("athlete_id")

# L'ordine e' quello della query: stile, distanza, vasca.
specialita = list(dict.fromkeys(rk["key"]))
if st.session_state.get("rk_event") not in specialita:
    st.session_state["rk_event"] = specialita[0]

c1, c2 = st.columns(2)
key = c1.selectbox("Specialità", specialita, key="rk_event")

dsp = rk[rk["key"] == key]
bande = sorted({int(b) for b in dsp["banda"].dropna()})
opzioni = [TUTTE_CAT] + bande


def _etichetta(v) -> str:
    """0 e' il giovanile; per le altre vale sia al maschile sia al femminile."""
    if isinstance(v, str):
        return v
    return "Giovanile" if int(v) == 0 else f"M{int(v)} / F{int(v)}"


if st.session_state.get("rk_cat") not in opzioni:
    st.session_state["rk_cat"] = TUTTE_CAT
cat = c2.selectbox("Categoria", opzioni, key="rk_cat", format_func=_etichetta,
                   help="La categoria e' quella della stagione in cui il tempo "
                        "e' stato nuotato.")

d = dsp if cat == TUTTE_CAT else dsp[dsp["banda"] == cat]

INTESTAZIONE = "".join(
    f'<th style="text-align:left;padding:6px 5px;color:var(--muted);font-size:10px;'
    f'letter-spacing:1px;text-transform:uppercase;white-space:nowrap">{h}</th>'
    for h in ("Pos.", "Atleta", "Cat.", "Tempo", "Gap")
)


def _classifica(sesso: str) -> None:
    g = d[d["sex"] == sesso]
    if g.empty:
        st.info("Nessun tempo con questi filtri.")
        return

    # Un atleta compare una volta sola, col suo tempo migliore fra quelli
    # che restano dopo il filtro di categoria.
    g = (g.sort_values("pb_sec").groupby("athlete_id", as_index=False).first()
         .sort_values("pb_sec").head(TOP).reset_index(drop=True))
    testa = float(g["pb_sec"].iloc[0])

    righe = ""
    for i, r in enumerate(g.to_dict("records"), start=1):
        mio = me is not None and int(r["athlete_id"]) == int(me)
        sfondo = ' style="background:rgba(0,194,199,0.07)"' if mio else ""
        quando = pd.to_datetime(r["comp_date"])
        dove = html.escape(str(r.get("comp_name") or "").strip(), quote=True)
        titolo = (f'{"" if pd.isna(quando) else quando.strftime("%d/%m/%Y")} · '
                  f'{season_mod.label(int(r["stagione"]))} · {dove}')
        gap = "—" if i == 1 else f'+{r["pb_sec"] - testa:.2f}'
        righe += (
            f'<tr{sfondo}>'
            f'<td style="padding:9px 5px;white-space:nowrap">{rank_html(i)}</td>'
            f'<td style="padding:9px 5px;color:var(--white);font-weight:600">'
            f'{html.escape(str(r["full_name"]).title())}</td>'
            f'<td style="padding:9px 5px;white-space:nowrap">'
            f'<span class="badge-cat">{r["categoria"]}</span></td>'
            f'<td style="padding:9px 5px;color:var(--teal);font-weight:600;'
            f'font-size:15px;white-space:nowrap" title="{titolo}">'
            f'{fmt_time(r["pb_sec"])}</td>'
            f'<td style="padding:9px 5px;color:var(--muted);white-space:nowrap">'
            f'{gap}</td>'
            f'</tr>'
        )

    st.html(f"""
    <div class="glass-card" style="overflow-x:auto;padding:12px 8px">
    <table style="width:100%;border-collapse:collapse;font-family:'Barlow Condensed',sans-serif;
                  font-size:13px;min-width:0">
      <thead><tr style="border-bottom:1px solid var(--border)">{INTESTAZIONE}</tr></thead>
      <tbody>{righe}</tbody>
    </table></div>""")


section("Maschi")
_classifica("M")

section("Femmine")
_classifica("F")

st.caption(
    f"I migliori {TOP} tempi di {key.lower()} in "
    f"{season_mod.label(sy).lower()}"
    + ("" if cat == TUTTE_CAT else f", categoria {_etichetta(cat)}")
    + ". Un atleta compare una volta sola, col suo tempo migliore. La "
      "categoria accanto al nome e' quella della stagione in cui ha nuotato "
      "quel tempo: passa il mouse sul tempo per vedere data e manifestazione."
)
