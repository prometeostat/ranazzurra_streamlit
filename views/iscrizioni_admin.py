"""
views/iscrizioni_admin.py — le iscrizioni ricevute, per allenatori e admin.

Si sceglie la manifestazione e si vede chi si e' iscritto, a quali gare e
con quale tempo, con le staffette tenute da parte perche' sono gare a se'.
In fondo il foglio Excel da scaricare per il portale federale.

La tabella si lavora come un foglio di calcolo. **Atleta**, **Gara** (due
tendine) e **Tempo iscrizione** si correggono nella cella; il **+** in
fondo aggiunge un'iscrizione e il **cestino** a destra la toglie. Serve per
tutto quello che arriva fuori dalla finestra: uno ha chiesto i 100 e
intendeva i 200, un altro manda il tempo giusto per messaggio il giorno
prima, un terzo da' l'adesione a voce in vasca, un quarto da' forfait il
venerdi' sera. Prima bisognava farselo correggere dall'atleta, e a finestra
chiusa non si poteva piu'.

Cambiare gara o atleta **sposta** la riga invece di rifarla, cosi' si porta
dietro la sua storia; togliere e' un soft delete come in tutta l'app, e
rimettere la stessa coppia atleta-gara riattiva la riga di prima. Le righe
che hanno gia' il tempo di gara non si tolgono e non si intestano a un
altro: per i risultati c'e' Inserisci tempi.
"""
from __future__ import annotations

import datetime as _dt
import io

import pandas as pd
import streamlit as st
from openpyxl.styles import Font

import auth
import crud
from views._common import page_header

page_header("Iscrizioni gare", "Chi si e' iscritto e a cosa")

if not auth.is_staff():
    st.info("Sezione riservata ad allenatori e amministratore.")
    st.stop()

msg = st.session_state.pop("isca_msg", None)
if msg:
    st.success(msg)

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

# Senza nemmeno un'iscrizione la tabella si disegna comunque, vuota: e'
# proprio il caso in cui serve il +, perche' le adesioni arrivano a voce e
# le mette dentro la segreteria. Le colonne vanno dichiarate a mano con il
# loro tipo, se no da un DataFrame senza righe non si ricavano.
COLONNE_VUOTE = {
    "entry_id": "Int64", "athlete_id": "Int64", "atleta": "object",
    "fin_code": "float", "race_id": "Int64", "gara": "object",
    "etichetta": "object", "is_relay": "bool", "entry_sec": "float",
    "race_date": "datetime64[ns]", "sessione": "object", "race_order": "float",
}

isc = crud.iscrizioni_manifestazione(int(comp_id))
vuota = isc.empty
if vuota:
    isc = pd.DataFrame({c: pd.Series(dtype=t)
                        for c, t in COLONNE_VUOTE.items()})
    st.info("Nessuna iscrizione registrata per questa manifestazione. "
            "Compaiono qui appena gli atleti si iscrivono, oppure appena le "
            "aggiungi tu con il + in fondo alla tabella.")

isc["relay"] = isc["is_relay"].astype(bool)
individuali = isc[~isc["relay"]]
staffette = isc[isc["relay"]]

if not vuota:
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

if vista.empty and not vuota:
    st.caption("Nessuna iscrizione con questi filtri. La tabella resta "
               "scrivibile: il + in fondo aggiunge comunque una riga.")


def _giornata(v) -> str:
    return "—" if pd.isna(v) else pd.to_datetime(v).strftime("%d/%m/%Y")


def _numero(v) -> str:
    return "—" if pd.isna(v) else str(int(v))


# ── Le due tendine ────────────────────────────────────────────────
# Quella della gara porta tutte le gare della manifestazione, staffette
# comprese: chi corregge sa cosa sta facendo, e una frazione finita per
# sbaglio fra le individuali va rimessa a posto proprio da qui.
gare = crud.gare_manifestazione(int(comp_id))
if gare.empty:
    st.warning("Questa manifestazione non ha gare: il programma si compila "
               "in Anagrafica manifestazioni, nel riquadro Programma. Senza "
               "gare non si puo' iscrivere nessuno.")
    st.stop()

ETICHETTE: dict[int, str] = {}
for r in gare.to_dict("records"):
    rid = int(r["race_id"])
    nome = str(r.get("name") or r.get("etichetta") or rid)
    vasca = ("" if pd.isna(r.get("pool_length"))
             else f' · {int(r["pool_length"])}m')
    ETICHETTE[rid] = f"{nome}{vasca}"
# Due gare possono chiamarsi uguale (stessa gara in due vasche, o due
# batterie con lo stesso nome): l'etichetta e' la chiave con cui la tendina
# torna indietro, quindi deve essere unica o si riscriverebbe la riga
# sbagliata. Dove si ripete le si attacca il numero di programma.
_conta: dict[str, int] = {}
for rid, et in ETICHETTE.items():
    _conta[et] = _conta.get(et, 0) + 1
for rid, et in list(ETICHETTE.items()):
    if _conta[et] > 1:
        ETICHETTE[rid] = f"{et} #{rid}"
INDIETRO = {v: k for k, v in ETICHETTE.items()}
OPZIONI = list(ETICHETTE.values())

# Quella dell'atleta porta la squadra attiva piu' chi e' gia' iscritto a
# questa manifestazione, anche se nel frattempo e' stato disattivato in
# anagrafica: se no la sua riga resterebbe senza etichetta e al salvataggio
# si perderebbe l'atleta.
atleti = crud.elenco_atleti()
if atleti.empty:
    st.warning("Nessun atleta in anagrafica: non si possono gestire "
               "iscrizioni.")
    st.stop()

dentro = set(isc["athlete_id"].dropna().astype(int))
squadra = atleti[(atleti["is_deleted"] == False)                   # noqa: E712
                 & (atleti["is_athlete"].astype(bool))]
if dentro:
    squadra = pd.concat([squadra, atleti[atleti["athlete_id"].isin(dentro)]])
    squadra = squadra.drop_duplicates(subset="athlete_id")


def _nome(r) -> str:
    return (f'{str(r.get("last_name") or "").strip()} '
            f'{str(r.get("first_name") or "").strip()}').strip().title()


# Stesso problema delle gare: l'etichetta e' la chiave, quindi due omonimi
# vanno distinti. Prima con l'anno di nascita, e se non basta con l'id.
NOMI = {int(r["athlete_id"]): _nome(r) for r in squadra.to_dict("records")}
ANNI = {int(r["athlete_id"]): pd.to_datetime(r.get("birth_date"),
                                             errors="coerce")
        for r in squadra.to_dict("records")}
_quanti: dict[str, int] = {}
for aid, nome in NOMI.items():
    _quanti[nome] = _quanti.get(nome, 0) + 1
for aid, nome in list(NOMI.items()):
    if _quanti[nome] > 1:
        anno = ANNI.get(aid)
        NOMI[aid] = nome if pd.isna(anno) else f"{nome} ({anno.year})"
_quanti.clear()
for aid, nome in NOMI.items():
    _quanti[nome] = _quanti.get(nome, 0) + 1
for aid, nome in list(NOMI.items()):
    if _quanti[nome] > 1:
        NOMI[aid] = f"{nome} #{aid}"
ATLETI_INDIETRO = {v: k for k, v in NOMI.items()}
ATLETI_OPZIONI = sorted(NOMI.values())

if not ATLETI_OPZIONI:
    st.warning("Nessun atleta attivo in anagrafica: non si possono gestire "
               "iscrizioni.")
    st.stop()

# ── La tabella ────────────────────────────────────────────────────
# Le righe arrivano gia' nell'ordine di programma: giornata, fascia, numero,
# e dentro per cognome. Le colonne sono quelle che servono in vasca.
# entry_id viaggia nella tabella ma non si vede (column_order lo esclude):
# st.data_editor segue le righe per posizione, e senza un identificatore nel
# dato non si saprebbe quale iscrizione si sta correggendo. Le righe
# aggiunte in tabella ce l'hanno vuoto, ed e' proprio cosi' che si
# riconoscono.
tabella = pd.DataFrame({
    "entry_id": vista["entry_id"].astype("Int64"),
    "Atleta": vista["athlete_id"].map(
        lambda v: NOMI.get(int(v), "—") if pd.notna(v) else "—"),
    "Gara": vista["race_id"].map(
        lambda v: ETICHETTE.get(int(v), "—") if pd.notna(v) else "—"),
    "Tempo iscrizione": vista["entry_sec"].map(crud.tempo_in_testo),
    "Giornata": vista["race_date"].map(_giornata),
    "Fascia": vista["sessione"].map(lambda v: "—" if pd.isna(v) else str(v)),
    "N.": vista["race_order"].map(_numero),
})
# Il tipo delle colonne va forzato: su una tabella senza righe le map()
# tornano serie di float, e la griglia disegnerebbe caselle numeriche al
# posto del testo e delle tendine.
for _c in ("Atleta", "Gara", "Tempo iscrizione", "Giornata", "Fascia", "N."):
    tabella[_c] = tabella[_c].astype("object")

puo_scrivere = not auth.sola_lettura()
if not puo_scrivere:
    st.info("Stai guardando come un altro atleta: da qui non si scrive.")

# La chiave porta dentro manifestazione e filtri: cambiando uno dei tre la
# tabella e' un'altra, e Streamlit deve ripartire da zero invece di
# riapplicare per posizione le modifiche in sospeso a righe diverse.
chiave_griglia = f"isca_grid_{int(comp_id)}_{tipo}_{cerca.strip().lower()}"
modificate = st.data_editor(
    tabella, key=chiave_griglia,
    num_rows="dynamic" if puo_scrivere else "fixed",
    use_container_width=True, hide_index=True, disabled=not puo_scrivere,
    column_order=("Atleta", "Gara", "Tempo iscrizione", "Giornata",
                  "Fascia", "N."),
    column_config={
        "Atleta": st.column_config.SelectboxColumn(
            "Atleta", options=ATLETI_OPZIONI, required=True, width="medium",
            help="Su una riga nuova e' chi si iscrive. Su una riga che c'e' "
                 "gia', cambiarlo intesta l'iscrizione a un altro."),
        "Gara": st.column_config.SelectboxColumn(
            "Gara", options=OPZIONI, required=True, width="large",
            help="Sposta l'iscrizione su un'altra gara di questa "
                 "manifestazione."),
        "Tempo iscrizione": st.column_config.TextColumn(
            "Tempo iscrizione", width="small",
            help="29.45 · 1:02.35 · 1:01:02.35. Vuoto vuol dire iscritto "
                 "senza tempo."),
        "Giornata": st.column_config.TextColumn("Giornata", disabled=True),
        "Fascia": st.column_config.TextColumn("Fascia", disabled=True),
        "N.": st.column_config.TextColumn(
            "N.", disabled=True,
            help="Numero di programma dentro la fascia oraria."),
    },
)


def _righe(df: pd.DataFrame) -> list[dict]:
    """Dalla griglia alla forma che vuole crud: id, atleta, gara, tempo."""
    return [{"entry_id": (None if pd.isna(r.get("entry_id"))
                          else int(r["entry_id"])),
             "athlete_id": ATLETI_INDIETRO.get(r.get("Atleta")),
             "race_id": INDIETRO.get(r.get("Gara")),
             "tempo": r.get("Tempo iscrizione")}
            for _, r in df.iterrows()]


# Il riassunto di cosa e' stato scritto, al singolare e al plurale: tre
# conteggi in fila dicono piu' di "Salvato".
ESITI = (("modificate", "1 iscrizione corretta", "{n} iscrizioni corrette"),
         ("inserite", "1 iscrizione aggiunta", "{n} iscrizioni aggiunte"),
         ("tolte", "1 iscrizione tolta", "{n} iscrizioni tolte"))

if puo_scrivere and st.button("Salva le iscrizioni", type="primary",
                              use_container_width=True):
    conteggi, errori = crud.salva_iscrizioni_staff(
        int(comp_id), _righe(modificate), _righe(tabella))
    pezzi = []
    for campo, uno, molti in ESITI:
        quante = int(conteggi.get(campo) or 0)
        if quante:
            pezzi.append(uno if quante == 1 else molti.format(n=quante))
    for e in errori:
        st.error(e)
    if errori and not pezzi:
        st.caption("Non è stato scritto niente: correggi e salva di nuovo.")
    elif pezzi:
        st.session_state["isca_msg"] = ", ".join(pezzi).capitalize() + "."
        st.rerun()
    elif not errori:
        st.info("Non c'era niente da cambiare.")

st.caption(f"{len(vista)} iscrizioni su {len(isc)} della manifestazione, "
           "nell'ordine del programma. Atleta, gara e tempo si correggono "
           "qui, il + in fondo aggiunge una riga e il cestino la toglie. "
           "Giornata, fascia e numero no: si compilano in Anagrafica "
           "manifestazioni, nel riquadro Programma, e dove mancano la riga "
           "resta in fondo con i trattini. Chi ha già il tempo di gara non "
           "si toglie e non si intesta a un altro: quello è un risultato e "
           "si tocca da Inserisci tempi. Cambiando filtro o ricerca prima "
           "di salvare, le modifiche non salvate si perdono.")

# ── Excel: il tracciato del portale federale ──────────────────────
# Cinque colonne e basta, nell'ordine che vuole la FIN:
#
#   ID manifestazione | Codice FIN | Atleta | Gara | Tempo iscrizione
#   150103            | 281728     | Modenese Mirko | 400 Misti - Maschi e Femmine | 06:30.00
#
# Non e' piu' il foglio di servizio di prima (giornata, fascia, numero di
# programma): quello serviva a noi a bordo vasca, questo si carica sul
# portale e deve avere le colonne che si aspetta lui, con quei nomi e in
# quell'ordine.
#
# **Le celle dei dati sono testo**. Non e' un vezzo: un codice come 150103
# letto da Excel come numero perde un eventuale zero iniziale, e un tempo
# come 06:30.00 diventa un orario e si porta dietro una data. Per questo le
# colonne si scrivono gia' come stringhe e il formato si forza a "@" dopo
# la scrittura. L'intestazione invece resta col formato di default ed e' in
# grassetto, come nel file del portale.

if vista.empty:
    st.stop()                 # niente righe, niente foglio da scaricare

LARGHEZZE_FIN = {"A": 18.0, "B": 12.0, "C": 26.0, "D": 36.0, "E": 16.0}


def _mmssdd(v) -> str:
    """Il tempo come lo vuole il portale: mm:ss.cc con gli zeri davanti,
    anche sotto il minuto. 28 secondi netti diventano 00:28.00."""
    if pd.isna(v):
        return ""
    s_ = float(v)
    minuti, resto = int(s_ // 60), s_ % 60
    return f"{minuti:02d}:{resto:05.2f}"


def _codice(v) -> str:
    """Il codice FIN dell'atleta come testo. A database e' un intero, e
    sette tesserati non ce l'hanno: li' resta vuoto."""
    if v is None or pd.isna(v):
        return ""
    try:
        return str(int(v))
    except (TypeError, ValueError):
        return str(v).strip()


id_manifestazione = str(riga.get("id_federnuoto") or "").strip()

export = pd.DataFrame({
    "ID manifestazione": id_manifestazione,
    "Codice FIN": vista["fin_code"].map(_codice),
    "Atleta": vista["atleta"].str.title(),
    "Gara": vista.apply(lambda r: str(r["gara"] or r["etichetta"]), axis=1),
    "Tempo iscrizione": vista["entry_sec"].map(_mmssdd),
}, index=vista.index)


@st.cache_data(ttl=60, show_spinner=False)
def _excel(df: pd.DataFrame, titolo: str) -> bytes:
    """Foglio in memoria, senza file temporanei."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as scrittore:
        df.to_excel(scrittore, index=False, sheet_name="Iscrizioni")
        foglio = scrittore.sheets["Iscrizioni"]
        for lettera, quanto in LARGHEZZE_FIN.items():
            foglio.column_dimensions[lettera].width = quanto
        for cella in foglio[1]:
            cella.font = Font(bold=True)
        # Testo sui soli dati: vedi la nota qui sopra.
        for riga_celle in foglio.iter_rows(min_row=2, max_row=foglio.max_row,
                                           min_col=1, max_col=len(df.columns)):
            for cella in riga_celle:
                cella.number_format = "@"
        foglio.freeze_panes = "A2"
    return buffer.getvalue()


# Nome del file come quelli che arrivano dal portale: il codice davanti,
# poi il nome in minuscolo con gli underscore. Senza codice si riparte da
# "iscrizioni_".
_slug = "".join(c if c.isalnum() else "_"
                for c in str(riga.get("nome") or "manifestazione")[:40].lower())
while "__" in _slug:
    _slug = _slug.replace("__", "_")
_slug = _slug.strip("_")
nome_file = (f"{id_manifestazione}_{_slug}.xlsx" if id_manifestazione
             else f"iscrizioni_{_slug}.xlsx")

if not id_manifestazione:
    st.warning(
        "Questa manifestazione non ha l'**ID FederNuoto**: nel foglio la "
        "prima colonna resta vuota. Lo si mette in Gestione > Anagrafica "
        "manifestazioni, Modifica.", icon="⚠️")

_senza = int(export["Codice FIN"].eq("").sum())
if _senza:
    _chi = sorted(set(export.loc[export["Codice FIN"].eq(""), "Atleta"]))
    st.warning(
        f"{_senza} righe senza codice FIN dell'atleta "
        f"({', '.join(_chi[:5])}{'…' if len(_chi) > 5 else ''}): nel foglio "
        "la seconda colonna resta vuota. Il codice si mette in Anagrafica "
        "atleti.", icon="⚠️")

st.download_button("⬇  Scarica le iscrizioni in Excel",
                   _excel(export, str(riga.get("nome") or "")),
                   file_name=nome_file, type="primary",
                   use_container_width=True,
                   mime=("application/vnd.openxmlformats-officedocument"
                         ".spreadsheetml.sheet"))
st.caption("Il foglio segue il tracciato del portale federale: ID "
           "manifestazione, codice FIN, atleta, gara, tempo d'iscrizione. "
           "Contiene le righe mostrate qui sopra, filtri compresi, quindi "
           "se hai filtrato per staffette esce solo quello.")
