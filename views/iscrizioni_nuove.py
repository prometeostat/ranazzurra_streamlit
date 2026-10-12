"""
views/iscrizioni_nuove.py — l'atleta si iscrive alle gare.

Si sceglie la manifestazione fra quelle aperte, si spuntano le gare e si
conferma dopo il riepilogo. L'elenco di quello che si e' gia' fatto sta
nell'altra pagina, Lista iscrizioni.

Tre cose che valgono sempre, e che stanno in crud.salva_iscrizioni perche'
l'interfaccia da sola non basta: si scrive solo dentro la finestra della
manifestazione (che parte 30 giorni prima dell'apertura ufficiale), non si
superano le gare individuali concesse, e ognuno tocca solo le proprie righe.
L'id dell'atleta arriva da auth.current_user(), cioe' dalla sessione creata
al login, mai da un widget o dall'indirizzo.

Niente griglia editabile qui dentro: servono caselle che si spengono da
sole quando il limite e' pieno, e una cella di st.data_editor non si puo'
disabilitare una per una.

Le staffette sono gare a parte: elenco loro, nessun tempo d'iscrizione (la
squadra la fa l'allenatore) e fuori dal conteggio del limite.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

import auth
import crud
from theme import fmt_time, pool_label, section
from views._common import blocchi_programma, page_header

page_header("Nuove iscrizioni", "Scegli le gare e il tempo")

utente = auth.current_user() or {}
mio_id = utente.get("athlete_id")
if mio_id is None:
    st.info("Le iscrizioni sono per i tesserati: il tuo account non e' "
            "collegato a una scheda atleta.")
    st.stop()
mio_id = int(mio_id)

_msg = st.session_state.pop("isc_msg", None)
if _msg:
    st.success(_msg)

meet = crud.manifestazioni_iscrivibili()


if meet.empty:
    st.info("Nessuna manifestazione aperta alle iscrizioni in questo "
            "momento. Le raccogliamo dai 30 giorni prima dell'apertura "
            "ufficiale: le date le trovi in Agenda.")
    st.stop()

# ══════════════════════════════════════════════════════════════════
# Manifestazione
# ══════════════════════════════════════════════════════════════════
ELENCO = {int(r["comp_id"]): r for r in meet.to_dict("records")}
opzioni = list(ELENCO)

pre = st.session_state.pop("isc_comp", None)
if pre is not None and int(pre) in ELENCO:
    st.session_state["isc_sel"] = int(pre)
if st.session_state.get("isc_sel") not in opzioni:
    st.session_state["isc_sel"] = opzioni[0]


def _giorno(v) -> str:
    q = pd.to_datetime(v, errors="coerce")
    return "—" if pd.isna(q) else q.strftime("%d/%m/%Y")


def _etichetta_meet(comp_id: int) -> str:
    r = ELENCO[int(comp_id)]
    return f"{_giorno(r['start_date'])} · {r.get('nome') or 'Manifestazione'}"


def _azzera() -> None:
    """Cambiando manifestazione il riepilogo aperto non deve seguirci."""
    st.session_state.pop("isc_conferma", None)


comp_id = st.selectbox("Manifestazione", opzioni, key="isc_sel",
                       format_func=_etichetta_meet, on_change=_azzera)
riga = ELENCO[int(comp_id)]

finestra = crud.finestra_iscrizioni(int(comp_id))
massimo = finestra.get("max_gare")

meta = []
if riga.get("organizzatore"):
    meta.append(str(riga["organizzatore"]))
meta.append("nessun limite di gare individuali" if massimo is None
            else f"massimo {massimo} gare individuali")

st.markdown(
    f'''<div class="ag-card">
      <div class="ag-data">{_giorno(riga["start_date"])}</div>
      <div class="ag-nome">{str(riga.get("nome") or "Manifestazione")}</div>
      <div class="ag-meta">{" · ".join(meta)}</div>
    </div>''', unsafe_allow_html=True)

# Scadenza bene in vista: e' l'unica data che fa perdere la gara.
chiusura = pd.to_datetime(riga.get("chiusura"), errors="coerce")
if not pd.isna(chiusura):
    mancano = (chiusura.date() - pd.Timestamp.today().date()).days
    coda = ("ultimo giorno" if mancano == 0 else
            "scaduta" if mancano < 0 else
            "manca 1 giorno" if mancano == 1 else f"mancano {mancano} giorni")
    st.html(
        '<div class="isc-scadenza">'
        '<span class="isc-scadenza-lbl">Iscrizioni entro il</span>'
        f'<span class="isc-scadenza-data">{chiusura.strftime("%d/%m/%Y")}</span>'
        f'<span class="isc-scadenza-coda">{coda}</span></div>')

if not finestra.get("aperta"):
    st.warning(crud.motivo_chiusura(finestra))
    st.stop()

gare = crud.gare_iscrizione(int(comp_id), mio_id)
if gare.empty:
    st.info("Il programma gare non e' ancora stato caricato per questa "
            "manifestazione.")
    st.stop()

individuali = gare[~gare["is_relay"].astype(bool)].copy()
staffette = gare[gare["is_relay"].astype(bool)].copy()

# ══════════════════════════════════════════════════════════════════
# Scelta delle gare
# ══════════════════════════════════════════════════════════════════
# Le spunte e i tempi vivono in session_state con una chiave per gara, cosi'
# sopravvivono ai rerun che servono a spegnere le caselle quando il limite
# e' pieno. La chiave porta dentro il comp_id: cambiando manifestazione si
# riparte da capo.


def _k_sel(race_id: int) -> str:
    return f"isc_s_{int(comp_id)}_{int(race_id)}"


def _k_tempo(race_id: int) -> str:
    return f"isc_t_{int(comp_id)}_{int(race_id)}"


for _, g in gare.iterrows():
    rid = int(g["race_id"])
    st.session_state.setdefault(_k_sel(rid), pd.notna(g["entry_id"]))
    if not bool(g["is_relay"]):
        # Il campo parte con il tempo gia' dichiarato; se non c'e' ancora,
        # con il personale, che resta modificabile.
        if pd.notna(g["entry_sec"]):
            iniziale = crud.tempo_in_testo(g["entry_sec"])
        elif pd.notna(g["pb_sec"]):
            iniziale = crud.tempo_in_testo(g["pb_sec"])
        else:
            iniziale = ""
        st.session_state.setdefault(_k_tempo(rid), iniziale)

scelte_ind = [int(r) for r in individuali["race_id"]
              if st.session_state.get(_k_sel(int(r)))]
pieno = massimo is not None and len(scelte_ind) >= massimo


def _riga_gara(g: dict, con_tempo: bool) -> None:
    """Una gara per riga: casella con il nome a sinistra, tempo a destra.

    Nome e vasca stanno nell'etichetta della casella e non in una colonna a
    parte: su un telefono tre colonne diventano tre righe, e una gara sola
    si mangiava mezzo schermo.
    """
    rid = int(g["race_id"])
    spuntata = bool(st.session_state.get(_k_sel(rid)))
    # Quando il limite e' pieno le gare non ancora scelte si spengono: per
    # cambiarne una bisogna prima togliere quella che non serve piu'.
    blocca = con_tempo and pieno and not spuntata
    nome = str(g.get("name") or g.get("etichetta"))
    sotto = pool_label(g["pool_length"], breve=True)
    if con_tempo and pd.notna(g.get("pb_sec")):
        sotto += f" · PB {fmt_time(g['pb_sec'])}"
    etichetta = f"**{nome}** &nbsp; :grey[{sotto}]"

    if con_tempo:
        c_gara, c_tempo = st.columns([5, 3], vertical_alignment="center")
        c_gara.checkbox(etichetta, key=_k_sel(rid), disabled=blocca,
                        help=("Hai gia' il massimo di gare individuali: "
                              "togline una per scegliere questa."
                              if blocca else None))
        c_tempo.text_input("tempo", key=_k_tempo(rid),
                           label_visibility="collapsed",
                           placeholder="mm:ss.dd", disabled=not spuntata)
    else:
        st.checkbox(etichetta, key=_k_sel(rid))


section("Gare individuali")
if individuali.empty:
    st.caption("Nessuna gara individuale in programma.")
else:
    st.caption("Spunta le gare: nel campo a destra trovi gia' il tuo "
               "personale sulla stessa distanza e nella stessa vasca, "
               "cambialo se vuoi. Lasciandolo vuoto vale il personale.")
    # Le gare arrivano gia' nell'ordine di programma: qui si mettono solo le
    # intestazioni di giornata e fascia dove il programma cambia. Se la
    # manifestazione non ce l'ha, torna un blocco solo senza titolo e
    # l'elenco resta quello di sempre.
    for titolo, fetta in blocchi_programma(individuali):
        if titolo:
            st.markdown(f'<div class="stroke-head">{titolo}</div>',
                        unsafe_allow_html=True)
        for _, g in fetta.iterrows():
            _riga_gara(g.to_dict(), con_tempo=True)

if massimo is not None:
    quante = len([r for r in individuali["race_id"]
                  if st.session_state.get(_k_sel(int(r)))])
    if quante >= massimo:
        st.info(f"Hai raggiunto il massimo di {massimo} gare individuali: "
                "per sceglierne un'altra togli prima una di queste.")
    else:
        st.caption(f"Scelte {quante} gare individuali su {massimo}.")

if not staffette.empty:
    section("Staffette")
    st.caption("Qui dai solo la disponibilita': squadre e frazioni le decide "
               "l'allenatore, e le staffette non contano nel limite.")
    # Stesse intestazioni delle individuali: anche una staffetta ha la sua
    # giornata e la sua fascia, e vederle sparse non aiuterebbe nessuno. I
    # blocchi si calcolano sulle sole staffette, quindi la numerazione delle
    # fasce e' quella loro.
    for titolo, fetta in blocchi_programma(staffette):
        if titolo:
            st.markdown(f'<div class="stroke-head">{titolo}</div>',
                        unsafe_allow_html=True)
        for _, g in fetta.iterrows():
            _riga_gara(g.to_dict(), con_tempo=False)


def _scelte() -> list[dict]:
    fuori = []
    for _, g in gare.iterrows():
        rid = int(g["race_id"])
        fuori.append({
            "race_id": rid,
            "iscritto": bool(st.session_state.get(_k_sel(rid))),
            "tempo": (None if bool(g["is_relay"])
                      else st.session_state.get(_k_tempo(rid))),
            "entry_id": (None if pd.isna(g["entry_id"])
                         else int(g["entry_id"])),
        })
    return fuori


# ══════════════════════════════════════════════════════════════════
# Riepilogo e conferma
# ══════════════════════════════════════════════════════════════════
scelte = _scelte()

if not st.session_state.get("isc_conferma"):
    if st.button("Rivedi e conferma", type="primary",
                 use_container_width=True):
        st.session_state["isc_conferma"] = True
        st.rerun()
else:
    section("Riepilogo")
    righe = ""
    for s in scelte:
        if not s["iscritto"]:
            continue
        g = gare[gare["race_id"] == s["race_id"]].iloc[0]
        if bool(g["is_relay"]):
            tempo = "disponibilita'"
        elif (s["tempo"] or "").strip():
            tempo = s["tempo"]
        elif pd.notna(g["pb_sec"]):
            tempo = crud.tempo_in_testo(g["pb_sec"])
        else:
            tempo = "senza tempo"
        righe += (f'<div class="mf-row"><div class="mf-chi">'
                  f'<div class="mf-nome">{str(g["name"] or g["etichetta"])}'
                  f'</div><span class="badge-cat">'
                  f'{pool_label(g["pool_length"], breve=True)}</span></div>'
                  f'<div class="mf-dx"><div class="mf-tempo">{tempo}</div>'
                  f'</div></div>')
    if righe:
        st.html(f'<div class="glass-card" style="padding:12px 10px">{righe}</div>')
    else:
        st.warning("Non hai selezionato nessuna gara: confermando vengono "
                   "tolte tutte le iscrizioni che avevi.")

    c1, c2 = st.columns(2)
    if c1.button("Conferma iscrizione", type="primary",
                 use_container_width=True):
        conteggi, errori = crud.salva_iscrizioni(mio_id, int(comp_id), scelte)
        if errori:
            for e in errori:
                st.error(e)
            st.caption("Non e' stato salvato niente: correggi e riprova.")
        else:
            pezzi = [f"{v} {k}" for k, v in conteggi.items() if v]
            st.session_state["isc_msg"] = (
                "Iscrizioni aggiornate: " + ", ".join(pezzi) + "."
                if pezzi else "Non c'era niente da cambiare.")
            st.session_state["isc_conferma"] = False
            # Le chiavi dei widget restano valide: al prossimo giro i valori
            # arrivano comunque da database, che adesso e' aggiornato.
            for _, g in gare.iterrows():
                st.session_state.pop(_k_sel(int(g["race_id"])), None)
                st.session_state.pop(_k_tempo(int(g["race_id"])), None)
            st.rerun()
    if c2.button("Torna indietro", use_container_width=True):
        st.session_state["isc_conferma"] = False
        st.rerun()
