"""
views/iscrizioni_mie.py — le iscrizioni che ho gia' fatto.

Il filtro parte vuoto e contiene solo le manifestazioni per cui mi sono
iscritto davvero: sceglierne una riempie la tabella con le sue gare e i
tempi d'iscrizione. Qui si guarda e basta; finche' la finestra e' aperta,
il bottone in fondo riporta alla pagina dove si cambia.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

import auth
import crud
from theme import fmt_time, pool_label
from views._common import page_header

page_header("Lista iscrizioni", "Quello a cui sei iscritto")

utente = auth.current_user() or {}
mio_id = utente.get("athlete_id")
if mio_id is None:
    st.info("Le iscrizioni sono per i tesserati: il tuo account non e' "
            "collegato a una scheda atleta.")
    st.stop()
mio_id = int(mio_id)

mie = crud.mie_iscrizioni(mio_id)
if mie.empty:
    st.info("Non risulti iscritto a nessuna gara. Le iscrizioni si fanno "
            "da Iscrizioni, Nuove iscrizioni, oppure dal bottone Iscriviti "
            "in Agenda.")
    st.stop()

mie = mie.copy()
mie["start_date"] = pd.to_datetime(mie["start_date"], errors="coerce")

# Una voce per manifestazione, dalla piu' vicina. Il selettore parte vuoto:
# si sceglie, e solo allora compare la tabella.
teste = (mie.sort_values("start_date")
            .drop_duplicates(subset="comp_id")[["comp_id", "manifestazione",
                                                "start_date", "aperta"]])
ELENCO = {int(r["comp_id"]): r for r in teste.to_dict("records")}


def _etichetta(comp_id: int) -> str:
    r = ELENCO[int(comp_id)]
    q = r["start_date"]
    giorno = "—" if pd.isna(q) else q.strftime("%d/%m/%Y")
    return f"{giorno} · {r['manifestazione']}"


comp_id = st.selectbox("Manifestazione", list(ELENCO), index=None,
                       format_func=_etichetta, key="mie_manif",
                       placeholder="Scegli una manifestazione…")

st.caption(f"Sei iscritto a {len(ELENCO)} manifestazioni, "
           f"{len(mie)} gare in tutto.")

if comp_id is None:
    st.stop()

riga = ELENCO[int(comp_id)]
vista = mie[mie["comp_id"] == int(comp_id)].copy()
# L'ordine di programma arriva gia' dalla query (giornata, fascia, numero,
# e in fondo le gare senza programma): qui non si riordina piu' niente, se
# no il numero di gara perderebbe senso.

stato = "aperte" if bool(riga["aperta"]) else "chiuse"
chiusura = pd.to_datetime(vista["chiusura"].iloc[0], errors="coerce")
st.markdown(
    f'''<div class="ag-card">
      <div class="ag-data">{"—" if pd.isna(riga["start_date"])
                            else riga["start_date"].strftime("%d/%m/%Y")}</div>
      <div class="ag-nome">{riga["manifestazione"]}</div>
      <div class="ag-meta">{len(vista)} gare · iscrizioni {stato}
        {"" if pd.isna(chiusura)
         else "· chiusura " + chiusura.strftime("%d/%m/%Y")}</div>
    </div>''', unsafe_allow_html=True)

def _vuoto(v, come=str) -> str:
    """Il trattino al posto della cella vuota, come nel resto dell'app."""
    return "—" if pd.isna(v) else come(v)


st.dataframe(
    pd.DataFrame({
        "Gara": vista["etichetta"],
        "Tipo": vista["is_relay"].map(
            lambda r: "Staffetta" if r else "Individuale"),
        "Vasca": vista["pool_length"].map(lambda v: pool_label(v, breve=True)),
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
    },
)

if bool(riga["aperta"]):
    if st.button("Modifica queste iscrizioni", type="primary",
                 use_container_width=True):
        st.session_state["isc_comp"] = int(comp_id)
        st.switch_page("views/iscrizioni_nuove.py")
else:
    st.caption("Le iscrizioni per questa manifestazione sono chiuse: per una "
               "correzione serve l'amministratore.")
