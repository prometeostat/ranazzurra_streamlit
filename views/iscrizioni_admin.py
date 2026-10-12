"""
views/iscrizioni_admin.py — le iscrizioni ricevute, per allenatori e admin.

Si sceglie la manifestazione e si vede chi si e' iscritto, a quali gare e
con quale tempo, con le staffette tenute da parte perche' sono gare a se'.
In fondo il foglio Excel da scaricare per organizzare la trasferta.

Letture e basta: qui dentro non si scrive niente. Le correzioni passano da
Inserisci tempi (tempi e punti) o dall'atleta stesso finche' la finestra di
iscrizione e' aperta.
"""
from __future__ import annotations

import datetime as _dt
import io

import pandas as pd
import streamlit as st

import auth
import crud
from theme import fmt_time
from views._common import page_header

page_header("Iscrizioni gare", "Chi si e' iscritto e a cosa")

if not auth.is_staff():
    st.info("Sezione riservata ad allenatori e amministratore.")
    st.stop()

manif = crud.elenco_manifestazioni()
if manif.empty:
    st.warning("Nessuna manifestazione a database.")
    st.stop()

# Solo le manifestazioni ancora da nuotare: le iscrizioni di una gara
# passata non servono piu' a organizzare niente, e per i risultati c'e'
# Inserisci tempi.
OGGI = _dt.date.today()
attive = manif[manif["is_deleted"] == False].copy()          # noqa: E712
attive["start_date"] = pd.to_datetime(attive["start_date"], errors="coerce")
attive = attive[attive["start_date"].dt.date >= OGGI].sort_values("start_date")
if attive.empty:
    st.info("Nessuna manifestazione in programma: qui compaiono solo quelle "
            "dalla data di oggi in avanti.")
    st.stop()

ELENCO = {int(r["comp_id"]): r for r in attive.to_dict("records")}
opzioni = list(ELENCO)


def _etichetta(comp_id: int) -> str:
    r = ELENCO[int(comp_id)]
    q = r["start_date"]
    giorno = "—" if pd.isna(q) else q.strftime("%d/%m/%Y")
    return f"{giorno} · {r.get('nome') or 'Manifestazione'}"


# Si parte dalla prima in calendario, che e' quella su cui si lavora.
if st.session_state.get("isca_sel") not in opzioni:
    st.session_state["isca_sel"] = opzioni[0]

comp_id = st.selectbox("Manifestazione", opzioni, key="isca_sel",
                       format_func=_etichetta)
riga = ELENCO[int(comp_id)]

isc = crud.iscrizioni_manifestazione(int(comp_id))
if isc.empty:
    st.info("Nessuna iscrizione registrata per questa manifestazione. "
            "Compaiono qui appena gli atleti si iscrivono, oppure appena "
            "carichi i tempi da Inserisci tempi.")
    st.stop()

isc["relay"] = isc["is_relay"].astype(bool)
individuali = isc[~isc["relay"]]
staffette = isc[isc["relay"]]

k = st.columns(3)
k[0].metric("Atleti", int(isc["athlete_id"].nunique()))
k[1].metric("Gare individuali", len(individuali))
k[2].metric("Frazioni staffetta", len(staffette))

limite = riga.get("max_races_per_athlete")
if pd.notna(limite) and int(limite) > 0:
    troppi = (individuali.groupby("atleta").size()
              .loc[lambda s: s > int(limite)])
    if not troppi.empty:
        st.warning("Oltre il limite di " + str(int(limite)) + " gare "
                   "individuali: " + ", ".join(f"{n} ({q})"
                                               for n, q in troppi.items()))

# ── Filtri ────────────────────────────────────────────────────────
c1, c2 = st.columns([2, 3])
tipo = c1.radio("Gare", ["Tutte", "Individuali", "Staffette"],
                horizontal=True, key="isca_tipo")
cerca = c2.text_input("Cerca", placeholder="Atleta, gara…", key="isca_cerca")

vista = isc
if tipo == "Individuali":
    vista = isc[~isc["relay"]]
elif tipo == "Staffette":
    vista = isc[isc["relay"]]
if cerca.strip():
    chiave = cerca.strip().lower()
    testo = (vista["atleta"].fillna("") + " " + vista["etichetta"].fillna("")
             + " " + vista["gara"].fillna(""))
    vista = vista[testo.str.lower().str.contains(chiave, na=False)]

if vista.empty:
    st.info("Nessuna iscrizione con questi filtri.")
    st.stop()


def _tempo(v) -> str:
    return "—" if pd.isna(v) else fmt_time(v)


def _giornata(v) -> str:
    return "—" if pd.isna(v) else pd.to_datetime(v).strftime("%d/%m/%Y")


def _numero(v) -> str:
    return "—" if pd.isna(v) else str(int(v))


# Le righe arrivano gia' nell'ordine di programma: giornata, fascia, numero,
# e dentro per cognome. Le colonne sono quelle che servono in vasca.
tabella = pd.DataFrame({
    "Atleta": vista["atleta"].str.title(),
    "Gara": vista.apply(lambda r: str(r["gara"] or r["etichetta"]), axis=1),
    "Tempo iscrizione": vista["entry_sec"].map(_tempo),
    "Giornata": vista["race_date"].map(_giornata),
    "Fascia": vista["sessione"].map(lambda v: "—" if pd.isna(v) else str(v)),
    "N.": vista["race_order"].map(_numero),
})
st.dataframe(
    tabella, use_container_width=True, hide_index=True,
    column_config={
        "N.": st.column_config.TextColumn(
            "N.", help="Numero di programma dentro la fascia oraria."),
    },
)
st.caption(f"{len(vista)} iscrizioni su {len(isc)} della manifestazione, "
           "nell'ordine del programma. Giornata e fascia si compilano in "
           "Anagrafica manifestazioni, nel riquadro Programma: dove mancano "
           "la riga resta in fondo con i trattini.")

# ── Excel ─────────────────────────────────────────────────────────
# Un foglio solo, le colonne che servono in vasca: niente e-mail e niente
# dati che non c'entrano con l'organizzazione della trasferta.
def _mmssdd(v) -> str:
    """Nel foglio i tempi hanno tutti la stessa forma mm:ss.dd, anche sotto
    il minuto: cosi' la colonna si ordina e si somma senza sorprese."""
    if pd.isna(v):
        return ""
    s_ = float(v)
    minuti, resto = int(s_ // 60), s_ % 60
    return f"{minuti:02d}:{resto:05.2f}"


# Le stesse colonne della tabella, con davanti il nome della manifestazione:
# manifestazione, atleta, gara, tempo d'iscrizione, poi quando si nuota.
export = pd.DataFrame({
    "Manifestazione": str(riga.get("nome") or ""),
    "Atleta": vista["atleta"].str.title(),
    "Gara": vista.apply(lambda r: str(r["gara"] or r["etichetta"]), axis=1),
    "Tempo iscrizione": vista["entry_sec"].map(_mmssdd),
    "Giornata": vista["race_date"].map(
        lambda v: "" if pd.isna(v) else pd.to_datetime(v).strftime("%d/%m/%Y")),
    "Fascia": vista["sessione"].map(lambda v: "" if pd.isna(v) else str(v)),
    "N.": vista["race_order"].map(
        lambda v: "" if pd.isna(v) else int(v)),
})


@st.cache_data(ttl=60, show_spinner=False)
def _excel(df: pd.DataFrame, titolo: str) -> bytes:
    """Foglio in memoria, senza file temporanei."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as scrittore:
        df.to_excel(scrittore, index=False, sheet_name="Iscrizioni")
        foglio = scrittore.sheets["Iscrizioni"]
        for i, colonna in enumerate(df.columns, start=1):
            larghezza = max([len(str(colonna))]
                            + [len(str(v)) for v in df[colonna].head(200)]) + 2
            foglio.column_dimensions[
                foglio.cell(row=1, column=i).column_letter
            ].width = min(larghezza, 42)
        foglio.freeze_panes = "A2"
    return buffer.getvalue()


nome_file = (f"iscrizioni_{str(riga.get('nome') or 'manifestazione')[:40]}"
             .replace(" ", "_").replace("/", "-") + ".xlsx")
st.download_button("⬇  Scarica le iscrizioni in Excel",
                   _excel(export, str(riga.get("nome") or "")),
                   file_name=nome_file, type="primary",
                   use_container_width=True,
                   mime=("application/vnd.openxmlformats-officedocument"
                         ".spreadsheetml.sheet"))
st.caption("Il foglio contiene le righe mostrate qui sopra, filtri "
           "compresi.")
