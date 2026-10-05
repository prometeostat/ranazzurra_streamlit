"""
views/cerca.py — pagina indice della sezione Cerca.

Due porte d'ingresso: la scheda di un atleta e le classifiche di squadra.
Sotto, il widget Manifestazioni: si scegle una manifestazione dal menu e si
vede gara per gara chi era iscritto, con tempo e punteggio FIN.
"""
from __future__ import annotations

import html

import pandas as pd
import streamlit as st

import auth
import data
import season as season_mod
from theme import fmt_time, pool_label, section
from views._common import inline_filters, page_header, season_year

page_header("Cerca", "Atleti, classifiche e manifestazioni")


def _voce(icona: str, titolo: str, sottotitolo: str, pagina: str, chiave: str) -> None:
    """La scheda e' il bottone: icona, titolo e sottotitolo sono tre paragrafi
    dell'etichetta, impaginati dal CSS legato alla chiave hub_*."""
    if st.button(f"{icona}\n\n{titolo}\n\n{sottotitolo}",
                 key=f"hub_{chiave}", use_container_width=True):
        st.switch_page(pagina)


_voce("🏊", "Atleta", "Tempi, personali e storico gara per gara",
      "views/scheda.py", "scheda")
_voce("🏆", "Classifiche", "I migliori tempi di squadra, per specialita'",
      "views/classifiche.py", "classifiche")

# ══════════════════════════════════════════════════════════════════
# Manifestazioni
# ══════════════════════════════════════════════════════════════════
section("Manifestazioni")
inline_filters("cerca", pool=False)

agenda = data.load_agenda(season_year()).copy()
if not agenda.empty:
    agenda["start_date"] = pd.to_datetime(agenda["start_date"], errors="coerce")
    # Solo quelle dove siamo scesi in acqua: le altre non hanno gare da mostrare.
    agenda = (agenda[agenda["nostre_gare"].fillna(0) > 0]
              .sort_values("start_date", ascending=False))

if agenda.empty:
    st.info("Nessuna manifestazione con nostri risultati nel periodo "
            "selezionato. Allarga il periodo a tutte le stagioni.")
    st.stop()

ELENCO = {int(r["comp_id"]): r for r in agenda.to_dict("records")}


def _etichetta_manif(comp_id: int) -> str:
    r = ELENCO[int(comp_id)]
    quando = r["start_date"]
    giorno = "—" if pd.isna(quando) else quando.strftime("%d/%m/%Y")
    return f"{giorno} · {str(r.get('nome') or 'Manifestazione')}"


opzioni = list(ELENCO)
if st.session_state.get("cerca_manif") not in opzioni:
    st.session_state["cerca_manif"] = opzioni[0]
comp_id = st.selectbox("Manifestazione", opzioni, key="cerca_manif",
                       format_func=_etichetta_manif,
                       help="Ci sono le manifestazioni del periodo in cui "
                            "abbiamo gareggiato, dalla piu' recente.")

riga = ELENCO[int(comp_id)]
quando = riga["start_date"]
giorno = "—" if pd.isna(quando) else quando.strftime("%d/%m/%Y")
nome_grezzo = str(riga.get("nome") or "Manifestazione")
nome = html.escape(nome_grezzo)
url = (str(riga.get("pdf_link") or "").strip()
       or str(riga.get("website_link") or "").strip())
if url.lower().startswith(("http://", "https://")):
    nome = (f'<a href="{html.escape(url, quote=True)}" target="_blank" '
            f'rel="noopener">{nome} ↗</a>')

res = data.load_competition_results(int(comp_id))
n_gare = 0 if res.empty else len(
    res.groupby(["is_relay", "stroke", "distance", "pool_length"], dropna=False))
n_atleti = 0 if res.empty else int(res["athlete_id"].nunique())

meta = [str(riga.get("organizzatore") or "").strip() or "—"]
if riga.get("vasche"):
    meta.append("vasca " + str(riga["vasche"]).replace("/", "m e ") + "m")
meta.append(f"{n_gare} gare")
meta.append(f"{n_atleti} atleti")

st.markdown(f'''<div class="ag-card">
  <div class="ag-data">{giorno}</div>
  <div class="ag-nome">{nome}</div>
  <div class="ag-meta">{html.escape(" · ".join(meta))}</div>
</div>''', unsafe_allow_html=True)

if res.empty:
    st.info("Nessun risultato a database per questa manifestazione.")
    st.stop()

# La categoria master dipende dalla stagione in cui si e' nuotato, non da
# quella che stiamo guardando: settembre fa da spartiacque.
_d = pd.to_datetime(res["comp_date"].iloc[0], errors="coerce")
stagione = (season_mod.current_season_year() if pd.isna(_d)
            else (_d.year if _d.month >= 9 else _d.year - 1))

me = (auth.current_user() or {}).get("athlete_id")

def _categoria(r: dict) -> str:
    """Categoria di quella stagione. Nei giovanili non c'e' la fascia, e in
    gare miste senza il sesso non si capirebbe chi e' chi."""
    anno = r.get("birth_year")
    if pd.isna(anno):
        return "—"
    cat = season_mod.master_category(int(anno), stagione, r.get("sex"))
    if cat == "Giovanile":
        return f"Giov. {str(r.get('sex') or '').upper()[:1] or '—'}"
    return cat


def _blocco(relay: bool, stroke: str, dist: str, pool, g: pd.DataFrame) -> str:
    titolo = (f"Staffetta {dist} {stroke}" if relay
              else f"{stroke} {dist}m")
    vasca = pool_label(pool)
    tempi = int(g["time_sec"].notna().sum())
    cappello = f"{vasca} · {len(g)} iscritti"
    if tempi < len(g):
        cappello += f" · {tempi} con tempo"

    righe = ""
    for i, r in enumerate(g.to_dict("records"), start=1):
        mio = me is not None and int(r["athlete_id"]) == int(me)
        # Nelle staffette il tempo e' quello della squadra, ripetuto su ogni
        # frazionista: numerare i frazionisti darebbe una classifica finta.
        pos = "" if relay or pd.isna(r["time_sec"]) else f"{i}"
        tempo = fmt_time(r["time_sec"]) if pd.notna(r["time_sec"]) else "—"
        punti = ("" if pd.isna(r.get("fin_score"))
                 else f'{int(r["fin_score"])} punti FIN')
        righe += (
            f'<div class="mf-row{" mf-mio" if mio else ""}">'
            f'<div class="mf-pos">{pos}</div>'
            f'<div class="mf-chi"><div class="mf-nome">'
            f'{html.escape(str(r["full_name"]).title())}</div>'
            f'<span class="badge-cat">{_categoria(r)}</span></div>'
            f'<div class="mf-dx"><div class="mf-tempo">{tempo}</div>'
            f'<div class="mf-punti">{punti}</div></div>'
            f'</div>'
        )

    return (
        f'<div class="glass-card" style="padding:12px 10px;margin-bottom:10px">'
        f'<div class="combo-head"><div class="combo-name">{html.escape(titolo)}'
        f'</div><div class="combo-pb">{html.escape(cappello)}</div></div>'
        f'{righe}</div>'
    )


gruppi = res.groupby(["is_relay", "stroke", "distance", "pool_length"],
                     sort=False, dropna=False)
st.html("".join(
    _blocco(bool(relay), str(stroke), str(dist), pool, g)
    for (relay, stroke, dist, pool), g in gruppi
))

st.caption(
    f"{n_gare} gare e {n_atleti} atleti nostri in {nome_grezzo}, "
    f"{giorno}. L'ordine dentro ogni gara e' quello del tempo; gli iscritti "
    "senza tempo (non partiti, ritirati o squalificati) restano in elenco "
    "senza posizione. Nelle staffette il tempo e' quello della squadra, "
    "uguale per tutti i frazionisti, e il punteggio FIN non viene assegnato. "
    "La categoria e' quella della stagione "
    f"{season_mod.label(stagione)}."
)
