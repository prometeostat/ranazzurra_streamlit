"""
views/iscrizioni_mie.py — Vedi le mie iscrizioni.

Tutto quello a cui l'atleta si e' iscritto, passato e futuro: il menu parte
dalle manifestazioni ancora da nuotare, dalla piu' vicina, e continua con lo
storico dalla piu' recente. Qui si guarda e basta; finche' il termine e'
aperto, il bottone in fondo porta alla pagina Modifica.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

import auth
import crud
from theme import fmt_time, pool_label
from views._common import page_header

page_header("Le mie iscrizioni", "Tutte, passate e future")

utente = auth.current_user() or {}
mio_id = utente.get("athlete_id")
if mio_id is None:
    st.info("Le iscrizioni sono per i tesserati: il tuo account non e' "
            "collegato a una scheda atleta.")
    st.stop()
mio_id = int(mio_id)

mie = crud.mie_iscrizioni(mio_id)
if mie.empty:
    st.info("Non risulti iscritto a nessuna gara.")
    if st.button("Vai a Iscriviti", type="primary", use_container_width=True,
                 key="mie_vai_nuova"):
        st.switch_page("views/iscrizioni_nuove.py")
    st.caption("Si puo' partire anche dal bottone Iscriviti in Agenda, "
               "accanto a ogni manifestazione aperta.")
    st.stop()

mie = mie.copy()
mie["start_date"] = pd.to_datetime(mie["start_date"], errors="coerce")

# Una voce per manifestazione, nell'ordine che arriva dalla query: prima
# quelle da nuotare, dalla piu' vicina, poi lo storico dalla piu' recente.
teste = crud.mie_manifestazioni(mio_id)
ELENCO = {int(r["comp_id"]): r for r in teste.to_dict("records")}
FUTURE = [c for c, r in ELENCO.items() if bool(r.get("futura"))]


def _etichetta(comp_id: int) -> str:
    r = ELENCO[int(comp_id)]
    q = pd.to_datetime(r["start_date"], errors="coerce")
    giorno = "—" if pd.isna(q) else q.strftime("%d/%m/%Y")
    coda = "  ·  da nuotare" if bool(r.get("futura")) else ""
    return f"{giorno} · {r['manifestazione']}{coda}"


comp_id = st.selectbox("Manifestazione", list(ELENCO), index=None,
                       format_func=_etichetta, key="mie_manif",
                       placeholder="Scegli una manifestazione…")

_passate = len(ELENCO) - len(FUTURE)
st.caption(
    f"Sei iscritto a {len(ELENCO)} manifestazioni, {len(mie)} gare in tutto: "
    f"{len(FUTURE)} da nuotare e {_passate} gia' fatte. In elenco prima "
    "quelle da nuotare, dalla piu' vicina.")

if comp_id is None:
    st.stop()

riga = ELENCO[int(comp_id)]
vista = mie[mie["comp_id"] == int(comp_id)].copy()
# L'ordine di programma arriva gia' dalla query (giornata, fascia, numero,
# e in fondo le gare senza programma): qui non si riordina piu' niente, se
# no il numero di gara perderebbe senso.

# Il termine per cambiare e' il giorno prima della chiusura ufficiale: la
# riga `aperta` arriva dalla stessa condizione SQL usata per scrivere.
si_cambia = bool(riga.get("aperta"))
ultimo = pd.to_datetime(riga.get("ultimo_giorno"), errors="coerce")
quando = pd.to_datetime(riga.get("start_date"), errors="coerce")

_termine = "" if pd.isna(ultimo) else f" il {ultimo.strftime('%d/%m/%Y')}"
if si_cambia:
    stato = f"modificabili entro{_termine}" if _termine else "modificabili"
elif bool(riga.get("futura")):
    stato = f"termine per le modifiche scaduto{_termine}"
else:
    stato = "manifestazione conclusa"

st.markdown(
    f'''<div class="ag-card">
      <div class="ag-data">{"—" if pd.isna(quando)
                            else quando.strftime("%d/%m/%Y")}</div>
      <div class="ag-nome">{riga["manifestazione"]}</div>
      <div class="ag-meta">{len(vista)} gare · {stato}</div>
    </div>''', unsafe_allow_html=True)


def _vuoto(v, come=str) -> str:
    """Il trattino al posto della cella vuota, come nel resto dell'app."""
    return "—" if pd.isna(v) else come(v)


def _stato_gara(r: dict) -> str:
    """Dove sta quella riga: iscritto, disponibilita' data, gara nuotata."""
    if pd.notna(r.get("time_sec")):
        return "Nuotata"
    return "Disponibilità" if bool(r.get("is_relay")) else "Iscritto"


st.dataframe(
    pd.DataFrame({
        "Gara": vista["etichetta"],
        "Tipo": vista["is_relay"].map(
            lambda r: "Staffetta" if r else "Individuale"),
        "Vasca": vista["pool_length"].map(lambda v: pool_label(v, breve=True)),
        "Stato": [_stato_gara(r) for r in vista.to_dict("records")],
        "Tempo iscrizione": vista["entry_sec"].map(
            lambda v: _vuoto(v, fmt_time)),
        # Giornata e fascia arrivano dal programma della manifestazione: su
        # quelle vecchie sono vuote e restano due trattini.
        "Giornata": vista["race_date"].map(
            lambda v: _vuoto(v, lambda d: d.strftime("%d/%m/%Y"))),
        "Fascia": vista["sessione"].map(lambda v: _vuoto(v)),
        "N.": vista["race_order"].map(lambda v: _vuoto(v, lambda n: str(int(n)))),
        "Tempo gara": vista["time_sec"].map(lambda v: _vuoto(v, fmt_time)),
    }),
    use_container_width=True, hide_index=True,
    column_config={
        "N.": st.column_config.TextColumn(
            "N.", help="Numero di programma dentro la fascia oraria."),
        "Stato": st.column_config.TextColumn(
            "Stato", help="Iscritto: tempo dichiarato, gara da nuotare. "
                          "Disponibilità: staffetta, la squadra la fa "
                          "l'allenatore. Nuotata: c'è il tempo di gara."),
    },
)

if auth.sola_lettura():
    st.caption("Stai guardando come un altro atleta: le iscrizioni si "
               "leggono e basta.")
elif si_cambia:
    if st.button("Modifica queste iscrizioni", type="primary",
                 use_container_width=True):
        st.session_state["isc_comp"] = int(comp_id)
        st.switch_page("views/iscrizioni_modifica.py")
elif bool(riga.get("futura")):
    st.caption("Il termine per cambiare e' passato: l'ultimo giorno prima "
               "della chiusura serve alla squadra per portare le adesioni "
               "sul portale federale. Per una correzione serve "
               "l'amministratore.")
else:
    st.caption("Manifestazione conclusa: questa e' la fotografia di quello a "
               "cui ti eri iscritto.")
