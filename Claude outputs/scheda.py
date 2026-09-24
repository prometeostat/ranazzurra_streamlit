"""
views/scheda.py — Scheda atleta.

Due schermate:
  1. selettore: ricerca, preferiti, elenco atleti
  2. scheda vera: intestazione, ultime tre manifestazioni, filtri periodo e
     vasca, elenco dei tempi per stile

Nessun grafico: gli andamenti stanno in Confronto, i passaggi in Gare.
"""
from __future__ import annotations

import html

import pandas as pd
import streamlit as st

import data
import season as season_mod
from theme import fmt_int, fmt_time, kpi, pool_label
from views._common import (anagrafica, apply_pool, apply_stroke, apri_atleta,
                           e_preferito, hero, inline_filters, page_header,
                           preferiti, season_year, selected_athlete,
                           toggle_preferito)

ORDINE_STILI = ["Stile Libero", "Dorso", "Rana", "Farfalla", "Misti"]
N_BLOCCHI = 3          # manifestazioni mostrate come blocchetti
GARE_PER_BLOCCO = 8    # righe dentro il blocchetto, poi "+ altre"
MAX_RISULTATI = 12     # righe mostrate dalla ricerca


def _ordine_stile(nome: str) -> int:
    return ORDINE_STILI.index(nome) if nome in ORDINE_STILI else len(ORDINE_STILI)


def _distanza(v) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def _manifestazione(nome, link) -> str:
    """Nome della manifestazione, cliccabile quando c'e' il website_link."""
    testo = html.escape(str(nome or "Manifestazione"))
    url = str(link or "").strip()
    if url.lower().startswith(("http://", "https://")):
        return (f'<a href="{html.escape(url, quote=True)}" target="_blank" '
                f'rel="noopener">{testo}</a>')
    return testo


# ══════════════════════════════════════════════════════════════════
# Schermata 1 — selettore atleta
# ══════════════════════════════════════════════════════════════════

def _riga_atleta(r: dict, chiave: str) -> None:
    aid = int(r["athlete_id"])
    anno = r.get("birth_year")
    anno = int(anno) if pd.notna(anno) else None
    cat = season_mod.master_category(anno, season_year(), r.get('sex'))
    fav = e_preferito(aid)

    c_star, c_info, c_apri = st.columns([1, 7, 2], vertical_alignment="center")
    if c_star.button("★" if fav else "☆", key=f"fav_{chiave}_{aid}",
                     help="Togli dai preferiti" if fav else "Aggiungi ai preferiti"):
        toggle_preferito(aid)
        st.rerun()
    c_info.markdown(
        f'''<div class="ath-row">
          <div class="ath-name">{str(r["full_name"]).title()}</div>
          <div class="ath-meta">{cat} ({anno if anno else "—"})</div>
          <div class="ath-team">{r.get("team") or "—"}</div>
        </div>''', unsafe_allow_html=True)
    if c_apri.button("Apri", key=f"open_{chiave}_{aid}", use_container_width=True):
        apri_atleta(aid)
        st.rerun()


def _selettore() -> None:
    page_header("Scheda atleta", "Scegli un atleta")

    atleti = anagrafica()
    if atleti.empty:
        st.warning("Anagrafica vuota.")
        st.stop()

    cerca = st.text_input("Cerca atleta", placeholder="Cognome o nome…",
                          label_visibility="collapsed", key="cerca_atleta")

    mio = st.session_state.get("athlete_id")
    pref = preferiti()

    if cerca.strip():
        chiave = cerca.strip().lower()
        trovati = atleti[atleti["full_name"].str.lower().str.contains(chiave, na=False)]
        st.markdown('<div class="section-title">Risultati</div>', unsafe_allow_html=True)
        if trovati.empty:
            st.info("Nessun atleta trovato. Prova con il solo cognome.")
            return
        for r in trovati.head(MAX_RISULTATI).to_dict("records"):
            _riga_atleta(r, "cerca")
        if len(trovati) > MAX_RISULTATI:
            st.caption(f"Mostrati {MAX_RISULTATI} risultati su {len(trovati)}: "
                       "scrivi qualche lettera in piu'.")
        return

    if mio is not None and (atleti["athlete_id"] == mio).any():
        st.markdown('<div class="section-title">La mia scheda</div>',
                    unsafe_allow_html=True)
        _riga_atleta(atleti[atleti["athlete_id"] == mio].iloc[0].to_dict(), "mio")

    if pref:
        preferite = atleti[atleti["athlete_id"].isin(pref)]
        if not preferite.empty:
            st.markdown('<div class="section-title">Preferiti</div>',
                        unsafe_allow_html=True)
            for r in preferite.to_dict("records"):
                _riga_atleta(r, "pref")

    # L'anagrafica intera non si srotola: sta in una tendina.
    st.markdown('<div class="section-title">Tutti gli atleti</div>',
                unsafe_allow_html=True)
    ids = atleti["athlete_id"].astype(int).tolist()
    nomi = dict(zip(ids, atleti["full_name"]))
    c_sel, c_fav, c_btn = st.columns([5, 1, 1], vertical_alignment="bottom")
    scelto = c_sel.selectbox(
        f"{len(ids)} atleti in anagrafica",
        options=[None] + ids,
        format_func=lambda i: "Scegli dall'elenco…" if i is None
        else str(nomi[i]).title(),
        key="sel_tutti",
    )
    fav_scelto = scelto is not None and e_preferito(int(scelto))
    if c_fav.button("★" if fav_scelto else "☆", key="fav_tutti",
                    use_container_width=True, disabled=scelto is None,
                    help="Togli dai preferiti" if fav_scelto
                    else "Aggiungi ai preferiti"):
        toggle_preferito(int(scelto))
        st.rerun()
    if c_btn.button("Apri", key="open_tutti", use_container_width=True,
                    disabled=scelto is None, type="primary"):
        apri_atleta(int(scelto))
        st.rerun()

    st.caption("Cerca per cognome oppure scegli dall'elenco. I preferiti "
               "restano per tutta la sessione: per tenerli anche cambiando "
               "dispositivo serve una tabellina a database, dimmelo e la aggiungo.")


# ══════════════════════════════════════════════════════════════════
# Router della pagina
# ══════════════════════════════════════════════════════════════════

row = selected_athlete()
if not st.session_state.get("scheda_aperta") or row is None:
    _selettore()
    st.stop()

sy = season_year()
athlete_id = int(row["athlete_id"])
sesso = row.get("sex")
anno_nascita = int(row["birth_year"]) if pd.notna(row.get("birth_year")) else None

c_back, c_fav = st.columns([2, 3], vertical_alignment="center")
if c_back.button("‹  Cambia atleta", use_container_width=True):
    st.session_state["scheda_aperta"] = False
    st.rerun()
_fav = e_preferito(athlete_id)
if c_fav.button("★  Nei preferiti" if _fav else "☆  Aggiungi ai preferiti",
                use_container_width=True,
                type="primary" if _fav else "secondary"):
    toggle_preferito(athlete_id)
    st.rerun()

hero(row)

with st.spinner("Caricamento…"):
    gare = data.load_races(athlete_id, sy).copy()
    alltime = data.load_alltime_pb(athlete_id).copy()

if gare.empty:
    st.info(f"Nessuna gara registrata in {season_mod.label(sy).lower()}.")
    inline_filters("scheda", strokes=True)
    st.stop()

gare["comp_date"] = pd.to_datetime(gare["comp_date"])
gare["luogo"] = gare["comp_type"].fillna("Manifestazione").astype(str)

# ══════════════════════════════════════════════════════════════════
# Riepilogo del periodo
# ══════════════════════════════════════════════════════════════════
# Contano la stagione scelta, non il filtro vasca: quello vale per l'elenco.
k = st.columns(3)
k[0].markdown(kpi(len(gare), "Gare"), unsafe_allow_html=True)
k[1].markdown(kpi(int(gare["comp_id"].nunique()), "Manifestazioni", "gold"),
              unsafe_allow_html=True)
k[2].markdown(kpi(fmt_int(gare["fin_score"].max()), "Miglior punteggio FIN", "green"),
              unsafe_allow_html=True)
st.caption(f"Periodo: {season_mod.label(sy).lower()}.")

# ══════════════════════════════════════════════════════════════════
# Ultime manifestazioni
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title" style="margin-top:8px">Ultime gare</div>',
            unsafe_allow_html=True)

meet = (gare.groupby("comp_id")
        .agg(data_gara=("comp_date", "max"),
             luogo=("luogo", "first"),
             vasca=("pool_length", "first"),
             link=("website_link", "first"),
             n_gare=("athlete_race_id", "count"))
        .reset_index()
        .sort_values("data_gara", ascending=False))

ultimi = meet.head(N_BLOCCHI).to_dict("records")


def _righe_gara(comp_id: int, limite: int | None = None) -> str:
    g = gare[gare["comp_id"] == comp_id].sort_values("event_label")
    totale = len(g)
    if limite:
        g = g.head(limite)
    righe = "".join(
        f'<div class="meet-line"><span class="meet-ev">{r["event_label"]}</span>'
        f'<span class="meet-t">{fmt_time(r["time_sec"])}</span></div>'
        for r in g.to_dict("records")
    )
    if limite and totale > limite:
        resto = totale - limite
        righe += (f'<div class="meet-line"><span class="meet-ev">'
                  f'+ altre {resto} gar{"a" if resto == 1 else "e"}</span></div>')
    return righe


cols = st.columns(N_BLOCCHI)
for col, m in zip(cols, ultimi):
    cid = int(m["comp_id"])
    url = str(m.get("link") or "").strip()
    cliccabile = url.lower().startswith(("http://", "https://"))
    n = int(m["n_gare"])

    # Niente bottone "Dettaglio": e' il blocchetto intero a portare ai
    # risultati ufficiali.
    freccia = '<span class="meet-go">↗</span>' if cliccabile else ""
    card = (f'<div class="meet-card">'
            f'<div class="meet-city">{html.escape(str(m["luogo"])[:60])}{freccia}</div>'
            f'<div class="meet-meta">{m["data_gara"].strftime("%d/%m/%Y")}'
            f' · {pool_label(m["vasca"])} · {n} gar{"a" if n == 1 else "e"}</div>'
            f'{_righe_gara(cid, GARE_PER_BLOCCO)}'
            f'</div>')
    if cliccabile:
        # Il tag di apertura resta su una riga sua: cosi' il markdown lo
        # legge come blocco HTML e non lo impacchetta dentro un paragrafo.
        apri = (f'<a class="meet-link" target="_blank" rel="noopener" '
                f'href="{html.escape(url, quote=True)}">')
        card = f"{apri}\n{card}\n</a>"
    col.markdown(card, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# Elenco gare, con filtro periodo e vasca
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Elenco gare</div>', unsafe_allow_html=True)
inline_filters("scheda", strokes=True)

elenco = apply_stroke(apply_pool(gare))
if elenco.empty:
    st.info("Nessun tempo con i filtri selezionati.")
    st.stop()

# Stagione di ogni gara, stessa regola di season.py (1 set - 31 ago)
mesi = elenco["comp_date"].dt.month
elenco["stagione"] = elenco["comp_date"].dt.year.where(
    mesi >= 9, elenco["comp_date"].dt.year - 1)

# Il migliore di OGNI stagione, non il migliore assoluto: altrimenti con
# "Tutte le stagioni" resterebbe una riga sola per combinazione e il badge PB
# si accenderebbe su tutte, confrontando un tempo con se stesso.
CHIAVE = ["stroke", "distance", "pool_length"]
idx = elenco.groupby(CHIAVE + ["stagione"])["time_sec"].idxmin()
righe = elenco.loc[idx].copy()

if not alltime.empty:
    righe = righe.merge(alltime[CHIAVE + ["pb_alltime_sec"]], on=CHIAVE, how="left")
else:
    righe["pb_alltime_sec"] = pd.NA

# PB: il tempo coincide col personale di sempre di quella combinazione, e
# una riga sola per combinazione anche se lo stesso tempo e' stato ripetuto.
# I tempi a DB sono in centesimi, quindi si confrontano arrotondati.
righe = righe.sort_values("comp_date")          # il primo a segnarlo tiene il badge
coincide = (righe["time_sec"].round(2)
            == pd.to_numeric(righe["pb_alltime_sec"], errors="coerce").round(2))
righe["pb"] = coincide & (
    coincide.groupby([righe[c] for c in CHIAVE]).cumsum() == 1)
righe["gap"] = righe["time_sec"] - pd.to_numeric(righe["pb_alltime_sec"],
                                                 errors="coerce")

righe["ord_stile"] = righe["stroke"].apply(_ordine_stile)
righe["ord_dist"] = righe["distance"].apply(_distanza)
righe = righe.sort_values(["ord_stile", "ord_dist", "pool_length", "stagione"],
                          ascending=[True, True, True, False])

for stile in righe["stroke"].unique():
    st.markdown(f'<div class="stroke-head">{stile}</div>', unsafe_allow_html=True)
    dello_stile = righe[righe["stroke"] == stile]

    for (dist, vasca), gruppo in dello_stile.groupby(["distance", "pool_length"],
                                                     sort=False):
        pb_combo = pd.to_numeric(gruppo["pb_alltime_sec"], errors="coerce").min()
        personale = (f'<span class="combo-pb">personale {fmt_time(pb_combo)}</span>'
                     if pd.notna(pb_combo) else "")
        blocco = (f'<div class="combo-head">'
                  f'<span class="combo-name">{_distanza(dist)} {stile} · '
                  f'{pool_label(vasca)}</span>{personale}</div>')

        for r in gruppo.to_dict("records"):
            pb = bool(r["pb"])
            badge = '<span class="pb-badge">PB</span>' if pb else ""
            gap = (f'<span class="evt-gap">+{r["gap"]:.2f}</span>'
                   if not pb and pd.notna(r["gap"]) and r["gap"] > 0 else "")
            punti = (f' · {fmt_int(r["fin_score"])} punti FIN'
                     if pd.notna(r.get("fin_score")) else "")
            blocco += (
                f'<div class="evt-row">'
                f'  <div><div class="evt-season">'
                f'{season_mod.short_label(int(r["stagione"]))}'
                f'<span class="badge-cat" style="margin-left:6px">'
                f'{season_mod.master_category(anno_nascita, int(r["stagione"]), sesso)}'
                f'</span></div>'
                f'  <div class="evt-meta">'
                f'{pd.to_datetime(r["comp_date"]).strftime("%d/%m/%Y")}{punti}</div>'
                f'  <div class="evt-meet">'
                f'{_manifestazione(r.get("comp_type"), r.get("website_link"))}</div></div>'
                f'  <div style="text-align:right">'
                f'    <span class="evt-time{" pb" if pb else ""}">'
                f'{fmt_time(r["time_sec"])}</span> {badge}{gap}</div>'
                f'</div>')
        st.markdown(f'<div class="combo-box">{blocco}</div>', unsafe_allow_html=True)

st.caption("Una riga per stagione con il miglior tempo di quella stagione. "
           "Il badge PB segna il personale di sempre di quella specialita' e "
           "vasca; sulle altre righe c'e' il distacco da quel tempo. Con una "
           "sola stagione selezionata resta una riga per specialita'.")
