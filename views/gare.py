"""
views/gare.py — elenco gare della stagione e dettaglio dei passaggi.

I parziali a DB sono tempi di frazione (la somma fa il tempo finale) e la
granularita' e' quasi sempre ogni 50 m, anche in vasca corta. split_table()
in data.py deduce i metri per frazione e segnala i casi irregolari.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import data
import season as season_mod
from theme import (RESP_H, RESP_H_SMALL, apply_axes, chart, delta_html,
                   fmt_int, fmt_time, kpi, palette, plotly_layout, pool_label,
                   section)
from views._common import (apply_pool, inline_filters, no_athlete_notice,
                           page_header, season_year, selected_athlete)

P = palette()

row = selected_athlete()
if row is None:
    no_athlete_notice()
    st.stop()

sy = season_year()
athlete_id = int(row["athlete_id"])

page_header("Gare e passaggi", str(row["full_name"]).title())
inline_filters("gare")

races = apply_pool(data.load_races(athlete_id, sy).copy())
if races.empty:
    st.info("Nessuna gara in questa stagione con i filtri selezionati.")
    st.stop()

races["comp_date"] = pd.to_datetime(races["comp_date"])
races["etichetta"] = (
    races["comp_date"].dt.strftime("%d/%m/%Y") + " · " + races["event_label"]
    + " (" + races["pool_length"].apply(lambda v: pool_label(v, breve=True)) + ") · "
    + races["time_sec"].apply(fmt_time)
)

k = st.columns(4)
k[0].markdown(kpi(len(races), "Gare"), unsafe_allow_html=True)
k[1].markdown(kpi(int(races["comp_id"].nunique()), "Manifestazioni", "gold"),
              unsafe_allow_html=True)
k[2].markdown(kpi(int((races["n_split"] > 0).sum()), "Con passaggi", "green"),
              unsafe_allow_html=True)
k[3].markdown(kpi(fmt_int(races["fin_score"].max()), "Miglior punteggio FIN", "gold"),
              unsafe_allow_html=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

sel = st.selectbox("Gara", options=races.index.tolist(),
                   format_func=lambda i: races.loc[i, "etichetta"])
gara = races.loc[sel]

# ══════════════════════════════════════════════════════════════════
# Dettaglio gara
# ══════════════════════════════════════════════════════════════════
cat = gara.get("category") or "—"
link = gara.get("website_link")
link_html = (f'<a href="{link}" target="_blank" style="color:var(--teal);'
             f'text-decoration:none">Risultati ufficiali ↗</a>') if link else ""

st.markdown(f"""
<div class="glass-card-accent">
  <div style="display:flex;justify-content:space-between;align-items:center;
       flex-wrap:wrap;gap:12px">
    <div>
      <div style="font-family:'Bebas Neue',sans-serif;font-size:26px;letter-spacing:3px">
        {gara['event_label']} <span style="color:var(--muted);font-size:18px">
        {pool_label(gara['pool_length'])}</span></div>
      <div style="font-family:'Barlow Condensed',sans-serif;font-size:13px;color:var(--muted)">
        {gara['comp_date'].strftime('%d/%m/%Y')} · {gara.get('comp_type') or 'Manifestazione'}
        · cronometraggio {str(gara.get('timing') or '—').lower()} · {link_html}</div>
    </div>
    <div style="text-align:right">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:40px;color:var(--teal);
           line-height:1">{fmt_time(gara['time_sec'])}</div>
      <div style="font-family:'Barlow Condensed',sans-serif;font-size:12px;color:var(--muted)">
        <span class="badge-cat">{cat}</span> &nbsp; {fmt_int(gara.get('fin_score'))} punti FIN</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Passaggi ──────────────────────────────────────────────────────
splits = data.load_splits(int(gara["athlete_race_id"]))
if splits.empty:
    st.info("Per questa gara non ci sono parziali a database. "
            "Li pubblica la FIN solo quando il cronometraggio e' automatico, "
            "e comunque vanno importati da FIN Veneto.")
else:
    tab_df, warn = data.split_table(splits["seg_sec"].tolist(),
                                    gara["distance"], gara["pool_length"])
    if warn:
        st.warning(warn)

    section("Passaggi vasca per vasca")

    somma = float(tab_df["seg_sec"].sum())
    scarto = somma - float(gara["time_sec"])
    c = st.columns(4)
    c[0].markdown(kpi(fmt_time(tab_df["seg_sec"].min()), "Frazione più veloce", "green"),
                  unsafe_allow_html=True)
    c[1].markdown(kpi(fmt_time(tab_df["seg_sec"].max()), "Frazione più lenta"),
                  unsafe_allow_html=True)
    c[2].markdown(kpi(f"{tab_df['seg_sec'].std():.2f}s" if len(tab_df) > 1 else "—",
                      "Deviazione standard", "gold"), unsafe_allow_html=True)
    prima_meta = tab_df["seg_sec"].iloc[:len(tab_df) // 2].sum() if len(tab_df) > 1 else None
    seconda = tab_df["seg_sec"].iloc[len(tab_df) // 2:].sum() if len(tab_df) > 1 else None
    if prima_meta and seconda:
        diff = seconda - prima_meta
        c[3].markdown(kpi(f"{diff:+.2f}s", "Seconda metà vs prima",
                          "green" if diff <= 0 else ""), unsafe_allow_html=True)
    else:
        c[3].markdown(kpi("—", "Seconda metà vs prima"), unsafe_allow_html=True)

    if abs(scarto) > 0.06:
        st.caption(f"La somma dei parziali ({fmt_time(somma)}) non coincide con il tempo "
                   f"finale ({fmt_time(gara['time_sec'])}): scarto {scarto:+.2f}s. "
                   "Nei dati FIN capita quando manca un passaggio.")

    media = float(tab_df["seg_sec"].mean())
    colori = [P["green"] if v < media else P["red"] if v > media * 1.03 else P["teal"]
              for v in tab_df["seg_sec"]]
    fig = go.Figure(go.Bar(
        x=tab_df["etichetta"], y=tab_df["seg_sec"],
        marker=dict(color=colori, line=dict(width=0)),
        text=[f"{v:.2f}" for v in tab_df["seg_sec"]], textposition="outside",
        textfont=dict(family="Barlow Condensed", size=12),
        customdata=tab_df[["cum_sec"]].values,
        hovertemplate="<b>%{x}</b><br>Frazione: %{y:.2f}s<br>"
                      "Cumulato: %{customdata[0]:.2f}s<extra></extra>",
    ))
    fig.add_hline(y=media, line=dict(color=P["gold"], width=1, dash="dot"),
                  annotation_text=f"media {media:.2f}s",
                  annotation_font=dict(family="Barlow Condensed", color=P["gold"], size=11))
    fig.update_layout(**plotly_layout(), yaxis_title="Secondi")
    apply_axes(fig)
    chart(fig, RESP_H)

    rows_html = ""
    for r in tab_df.to_dict("records"):
        pace = (f"{r['pace_50']:.2f}" if r.get("pace_50") is not None
                and pd.notna(r["pace_50"]) else "—")
        rows_html += (
            "<tr style=\"border-bottom:1px solid var(--hairline)\">"
            f"<td style=\"padding:8px 12px\"><span class=\"event-pill\">{r['etichetta']}</span></td>"
            f"<td style=\"padding:8px 12px;color:var(--white);font-weight:600\">{r['seg_sec']:.2f}</td>"
            f"<td style=\"padding:8px 12px;color:var(--muted)\">{fmt_time(r['cum_sec'])}</td>"
            f"<td style=\"padding:8px 12px\">{delta_html(r['delta'])}</td>"
            f"<td style=\"padding:8px 12px;color:var(--muted)\">{pace}</td>"
            "</tr>"
        )
    head = "".join(
        f'<th style="text-align:left;padding:8px 12px;color:var(--muted);font-size:11px;'
        f'letter-spacing:2px;text-transform:uppercase">{h}</th>'
        for h in ("Passaggio", "Frazione (s)", "Cumulato", "Δ vs precedente", "Passo/50m")
    )
    st.html(f"""
    <div class="glass-card" style="overflow-x:auto">
    <table style="width:100%;border-collapse:collapse;font-family:'Barlow Condensed',sans-serif;
                  font-size:14px;min-width:520px">
      <thead><tr style="border-bottom:1px solid var(--border)">{head}</tr></thead>
      <tbody>{rows_html}</tbody>
    </table></div>""")

# ══════════════════════════════════════════════════════════════════
# Confronto passaggi sulla stessa specialita'
# ══════════════════════════════════════════════════════════════════
storico = data.load_splits_by_event(athlete_id, gara["stroke"], gara["distance"],
                                    int(gara["pool_length"]))
if not storico.empty and storico["athlete_race_id"].nunique() > 1:
    section("Come sono cambiati i passaggi nel tempo")
    storico = storico.copy()
    storico["comp_date"] = pd.to_datetime(storico["comp_date"])
    storico["ordine"] = storico.groupby("athlete_race_id").cumcount() + 1

    prove = (storico.groupby(["athlete_race_id", "comp_date"])["time_sec"]
             .first().reset_index().sort_values("comp_date", ascending=False))
    etichette = {int(r.athlete_race_id):
                 f"{r.comp_date.strftime('%d/%m/%y')} · {fmt_time(r.time_sec)}"
                 for r in prove.itertuples()}
    default = [int(gara["athlete_race_id"])]
    migliore = int(prove.sort_values("time_sec").iloc[0]["athlete_race_id"])
    if migliore not in default:
        default.append(migliore)

    scelte = st.multiselect("Prove da confrontare", options=list(etichette.keys()),
                            default=default, format_func=lambda i: etichette[i])
    if scelte:
        fig = go.Figure()
        for i, arid in enumerate(scelte):
            g = storico[storico["athlete_race_id"] == arid].sort_values("ordine")
            tab, _ = data.split_table(g["seg_sec"].tolist(), gara["distance"],
                                      gara["pool_length"])
            fig.add_trace(go.Scatter(
                x=tab["etichetta"], y=tab["seg_sec"], mode="lines+markers",
                name=etichette[arid],
                line=dict(width=3 if arid == int(gara["athlete_race_id"]) else 2,
                          color=[P["teal"], P["gold"], P["green"], P["purple"], P["red"]][i % 5]),
                marker=dict(size=7),
                hovertemplate="%{x}: %{y:.2f}s<extra>" + etichette[arid] + "</extra>",
            ))
        fig.update_layout(**plotly_layout(), yaxis_title="Secondi per frazione",
                          hovermode="x unified")
        apply_axes(fig)
        chart(fig, RESP_H_SMALL)

# ══════════════════════════════════════════════════════════════════
# Tutte le gare della stagione
# ══════════════════════════════════════════════════════════════════
section("Tutte le gare della stagione")
tab = races[["comp_date", "event_label", "pool_length", "time_sec",
             "fin_score", "category", "n_split"]].copy()
tab["Tempo"] = tab["time_sec"].apply(fmt_time)
tab["Data"] = tab["comp_date"].dt.strftime("%d/%m/%Y")
tab = tab.rename(columns={"event_label": "Specialità", "pool_length": "Vasca",
                          "fin_score": "Punti FIN", "category": "Categoria",
                          "n_split": "Passaggi"})
st.dataframe(
    tab[["Data", "Specialità", "Vasca", "Tempo", "Punti FIN", "Categoria", "Passaggi"]],
    use_container_width=True, hide_index=True,
)
