"""
views/tempi.py — inserimento manuale di tempi e punteggi, solo admin.

Si sceglie la manifestazione, poi la gara, e sotto compare una griglia con
gli iscritti: atleta, tempo, punti FIN e categoria. Si modifica come un
foglio di calcolo, si aggiungono righe in fondo, si tolgono con il cestino,
e un bottone solo scrive tutto a database.

Perche' una griglia e non un form riga per riga: una gara sono dieci o
quindici atleti presi da un PDF, e passare da dieci salvataggi separati
sarebbe una pena. Il salvataggio e' comunque atomico dal punto di vista
della validazione: se una riga e' sbagliata non parte nessuna query.

Il tracciato del database resta quello di sempre: niente cancellazioni
fisiche (is_deleted = TRUE), creation_user_id su quello che nasce,
last_modification_user_id su quello che cambia, deletion_user_id su quello
che si toglie.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

import auth
import crud
from views._common import page_header

page_header("Inserisci tempi", "Gara per gara, atleta per atleta")

if not auth.is_admin():
    st.info("L'inserimento dei tempi e' riservato all'amministratore.")
    st.stop()

msg = st.session_state.pop("tempi_msg", None)
if msg:
    st.success(msg)

# ── Manifestazione ────────────────────────────────────────────────
manif = crud.elenco_manifestazioni()
if manif.empty:
    st.warning("Nessuna manifestazione a database.")
    st.stop()

attive = manif[manif["is_deleted"] == False].copy()          # noqa: E712
if attive.empty:
    st.warning("Nessuna manifestazione attiva.")
    st.stop()
attive["start_date"] = pd.to_datetime(attive["start_date"], errors="coerce")
attive = attive.sort_values("start_date", ascending=False)

ELENCO = {int(r["comp_id"]): r for r in attive.to_dict("records")}
opzioni = list(ELENCO)


def _etichetta(comp_id: int) -> str:
    r = ELENCO[int(comp_id)]
    q = r["start_date"]
    giorno = "—" if pd.isna(q) else q.strftime("%d/%m/%Y")
    return f"{giorno} · {r.get('nome') or 'Manifestazione'}"


# Arrivando dal bottone in Anagrafica manifestazioni la gara e' gia' scelta.
pre_comp = st.session_state.pop("tempi_comp", None)
pre_race = st.session_state.pop("tempi_race", None)
if pre_comp is not None and int(pre_comp) in ELENCO:
    st.session_state["tempi_sel_comp"] = int(pre_comp)
if st.session_state.get("tempi_sel_comp") not in opzioni:
    st.session_state["tempi_sel_comp"] = opzioni[0]

comp_id = st.selectbox("Manifestazione", opzioni, key="tempi_sel_comp",
                       format_func=_etichetta)

# ── Gara ──────────────────────────────────────────────────────────
gare = crud.gare_manifestazione(int(comp_id))
if gare.empty:
    st.info("Questa manifestazione non ha gare. Creale da Anagrafica "
            "manifestazioni, Modifica, sezione Gare.")
    st.stop()

ids_gare = gare["race_id"].astype(int).tolist()
etich_gare = {
    int(r["race_id"]): (f'{r["name"] or r["etichetta"]} · '
                        f'{int(r["pool_length"])}m · '
                        f'{int(r["iscritti"])} iscritti')
    for _, r in gare.iterrows()
}
if pre_race is not None and int(pre_race) in ids_gare:
    st.session_state["tempi_sel_gara"] = int(pre_race)
if st.session_state.get("tempi_sel_gara") not in ids_gare:
    st.session_state["tempi_sel_gara"] = ids_gare[0]

race_id = st.selectbox("Gara", ids_gare, key="tempi_sel_gara",
                       format_func=lambda i: etich_gare.get(i, str(i)))

# ── Griglia ───────────────────────────────────────────────────────
iscritti = crud.iscritti_gara(int(race_id))
atleti = crud.elenco_atleti()


def _nome(r) -> str:
    anno = pd.to_datetime(r.get("birth_date"), errors="coerce")
    anno = "" if pd.isna(anno) else f" ({anno.year})"
    return f'{r["last_name"]} {r["first_name"]}{anno}'


# Nelle opzioni ci sono gli atleti attivi piu' quelli gia' iscritti a questa
# gara, anche se nel frattempo sono stati disattivati: se no la loro riga
# resterebbe senza etichetta e il salvataggio li butterebbe fuori.
dentro = set(iscritti["athlete_id"].dropna().astype(int)) if not iscritti.empty else set()
sel = atleti[(atleti["is_deleted"] == False)                      # noqa: E712
             & (atleti["is_athlete"].astype(bool))] if not atleti.empty else atleti
if not atleti.empty and dentro:
    sel = pd.concat([sel, atleti[atleti["athlete_id"].isin(dentro)]])
    sel = sel.drop_duplicates(subset="athlete_id")

NOMI = {int(r["athlete_id"]): _nome(r) for _, r in sel.iterrows()}
IDS = {v: k for k, v in NOMI.items()}
OPZIONI = sorted(NOMI.values())

if not OPZIONI:
    st.warning("Nessun atleta in anagrafica: non si possono inserire tempi.")
    st.stop()

if iscritti.empty:
    partenza = pd.DataFrame({"entry_id": pd.Series(dtype="Int64"),
                             "Atleta": pd.Series(dtype="object"),
                             "Tempo": pd.Series(dtype="object"),
                             "Punti": pd.Series(dtype="float"),
                             "Categoria": pd.Series(dtype="object")})
else:
    partenza = pd.DataFrame({
        "entry_id": iscritti["entry_id"].astype("Int64"),
        "Atleta": iscritti["athlete_id"].map(lambda a: NOMI.get(int(a), "—")),
        "Tempo": iscritti["time_sec"].map(crud.tempo_in_testo),
        # Punti in virgola mobile e non Int64: con i numeri interi di pandas
        # la griglia scrive "None" nelle celle vuote invece di lasciarle
        # bianche. Il valore torna indietro intero lo stesso, ci pensa _righe.
        "Punti": pd.to_numeric(iscritti["fin_score"], errors="coerce"),
        "Categoria": iscritti["categoria"].fillna(""),
    })

st.caption("Tempo: 29.45 · 1:02.35 · 1:01:02.35. Lascia il tempo vuoto per "
           "chi era iscritto ma non è partito, si è ritirato o è stato "
           "squalificato. Le staffette vogliono una riga per frazionista, "
           "tutte con il tempo della squadra.")

# La chiave porta dentro il race_id: cambiando gara Streamlit deve ripartire
# da zero, se no si porta dietro le modifiche in sospeso e le applica alla
# gara sbagliata, riga per riga.
modificate = st.data_editor(
    partenza, key=f"grid_tempi_{int(race_id)}", num_rows="dynamic",
    use_container_width=True, hide_index=True,
    column_order=("Atleta", "Tempo", "Punti", "Categoria"),
    column_config={
        "Atleta": st.column_config.SelectboxColumn("Atleta", options=OPZIONI,
                                                   required=True, width="large"),
        "Tempo": st.column_config.TextColumn("Tempo", width="small"),
        "Punti": st.column_config.NumberColumn("Punti FIN", min_value=0,
                                               max_value=crud.PUNTI_MAX,
                                               step=1, format="%d",
                                               width="small"),
        "Categoria": st.column_config.TextColumn(
            "Categoria", width="small",
            help="Com'è scritta sui risultati, per esempio M35. Si può "
                 "lasciare vuota."),
    },
)


def _righe(df: pd.DataFrame) -> list[dict]:
    fuori = []
    for _, r in df.iterrows():
        nome = r.get("Atleta")
        fuori.append({
            "entry_id": (None if pd.isna(r.get("entry_id"))
                         else int(r["entry_id"])),
            "athlete_id": IDS.get(nome),
            "tempo": r.get("Tempo"),
            "punti": (None if pd.isna(r.get("Punti")) else int(r["Punti"])),
            "categoria": r.get("Categoria"),
        })
    return fuori


if st.button("Salva i tempi", type="primary", use_container_width=True):
    conteggi, errori = crud.salva_tempi(int(race_id), _righe(modificate),
                                        _righe(partenza))
    if errori:
        for e in errori:
            st.error(e)
        st.caption("Non è stato scritto niente: correggi e salva di nuovo.")
    else:
        pezzi = [f"{v} {k}" for k, v in conteggi.items() if v]
        st.session_state["tempi_msg"] = (
            "Salvato: " + ", ".join(pezzi) + "." if pezzi
            else "Non c'era niente da cambiare.")
        st.rerun()

st.caption(f"{len(partenza)} iscritti a database per questa gara. Il cestino "
           "a destra toglie una riga: l'iscrizione non viene cancellata "
           "davvero, va a is_deleted = TRUE come tutto il resto dell'app.")
