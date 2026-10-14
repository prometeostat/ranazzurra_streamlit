"""
views/_iscrizioni_form.py — il modulo delle iscrizioni, una volta sola.

Due pagine lo chiamano con un modo diverso: `iscrizioni_nuove.py` con
"nuova", per chi si iscrive, e `iscrizioni_modifica.py` con "modifica", per
chi torna a cambiare quello che aveva scelto. Cambiano l'elenco delle
manifestazioni proposte e le parole a video; le gare, i tempi, il limite
delle individuali e il salvataggio sono gli stessi, perche' sono la stessa
cosa e scriverli due volte voleva dire vederli divergere.

Tre regole valgono sempre, e stanno in `crud.salva_iscrizioni` perche'
l'interfaccia da sola non basta: si scrive solo dentro la finestra della
manifestazione (dai 30 giorni prima dell'apertura ufficiale al giorno PRIMA
della chiusura), non si superano le gare individuali concesse, e ognuno
tocca solo le proprie righe. L'id dell'atleta arriva da
`auth.current_user()`, cioe' dalla sessione creata al login, mai da un
widget o dall'indirizzo.

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

# Titolo e sottotitolo delle due porte.
MODI = {
    "nuova": ("Iscriviti", "Scegli le gare e il tempo"),
    "modifica": ("Modifica", "Cambia gare e tempi"),
}


def _giorno(v) -> str:
    q = pd.to_datetime(v, errors="coerce")
    return "—" if pd.isna(q) else q.strftime("%d/%m/%Y")


def _elenco_aperte() -> dict[int, dict]:
    """Le manifestazioni su cui si puo' scrivere oggi."""
    meet = crud.manifestazioni_iscrivibili()
    if meet.empty:
        return {}
    return {int(r["comp_id"]): {
        "nome": r.get("nome"),
        "start_date": r.get("start_date"),
        "chiusura": r.get("chiusura"),
        "ultimo_giorno": r.get("ultimo_giorno"),
        "organizzatore": r.get("organizzatore"),
        "aperta": True,
    } for r in meet.to_dict("records")}


def _elenco_mie(athlete_id: int) -> dict[int, dict]:
    """
    Le manifestazioni ancora da nuotare in cui l'atleta ha gia' delle gare.

    Ci restano anche quelle col termine scaduto: sono proprio quelle per cui
    serve dirlo chiaramente invece di farle sparire dal menu.
    """
    teste = crud.mie_manifestazioni(int(athlete_id))
    if teste.empty:
        return {}
    teste = teste[teste["futura"].fillna(False).astype(bool)]
    return {int(r["comp_id"]): {
        "nome": r.get("manifestazione"),
        "start_date": r.get("start_date"),
        "chiusura": r.get("chiusura"),
        "ultimo_giorno": r.get("ultimo_giorno"),
        "organizzatore": None,
        "aperta": bool(r.get("aperta")),
        "gare": int(r.get("gare") or 0),
    } for r in teste.to_dict("records")}


def _scheda_manifestazione(riga: dict, massimo: int | None) -> None:
    """La testata con data, nome e due righe di contesto."""
    meta = []
    if riga.get("organizzatore"):
        meta.append(str(riga["organizzatore"]))
    if riga.get("gare"):
        meta.append(f"{riga['gare']} gare tue")
    meta.append("nessun limite di gare individuali" if massimo is None
                else f"massimo {massimo} gare individuali")
    st.markdown(
        f'''<div class="ag-card">
          <div class="ag-data">{_giorno(riga.get("start_date"))}</div>
          <div class="ag-nome">{str(riga.get("nome") or "Manifestazione")}</div>
          <div class="ag-meta">{" · ".join(meta)}</div>
        </div>''', unsafe_allow_html=True)


def _scadenza(riga: dict, aperta: bool) -> None:
    """
    La data che fa perdere la gara, bene in vista.

    Non e' `close_registration_date` ma il giorno prima: l'ultimo giorno
    serve alla squadra per portare le adesioni sul portale federale, e un
    atleta che legge la data ufficiale si presenta un giorno tardi.

    La spiegazione sotto esce solo finche' si puo' scrivere: a termine
    scaduto la stessa cosa la dice gia', e meglio, il messaggio di chiusura.
    """
    ultimo = pd.to_datetime(riga.get("ultimo_giorno"), errors="coerce")
    if pd.isna(ultimo):
        return
    mancano = (ultimo.date() - pd.Timestamp.today().date()).days
    coda = ("ultimo giorno" if mancano == 0 else
            "scaduta" if mancano < 0 else
            "manca 1 giorno" if mancano == 1 else f"mancano {mancano} giorni")
    st.html(
        '<div class="isc-scadenza">'
        '<span class="isc-scadenza-lbl">Iscrizioni entro il</span>'
        f'<span class="isc-scadenza-data">{ultimo.strftime("%d/%m/%Y")}</span>'
        f'<span class="isc-scadenza-coda">{coda}</span></div>')
    chiusura = pd.to_datetime(riga.get("chiusura"), errors="coerce")
    if aperta and not pd.isna(chiusura):
        st.caption(f"La chiusura ufficiale e' il "
                   f"{chiusura.strftime('%d/%m/%Y')}: l'ultimo giorno resta "
                   "alla squadra per portare le adesioni sul portale "
                   "federale, quindi da qui si scrive fino al giorno prima.")


def _elenco_iscritte(gare: pd.DataFrame) -> None:
    """Le gare a cui l'atleta e' iscritto, da guardare e basta."""
    mie = gare[gare["entry_id"].notna()]
    if mie.empty:
        st.info("Non risulti iscritto a nessuna gara di questa "
                "manifestazione.")
        return
    for titolo, fetta in blocchi_programma(mie):
        if titolo:
            st.markdown(f'<div class="stroke-head">{titolo}</div>',
                        unsafe_allow_html=True)
        righe = ""
        for g in fetta.to_dict("records"):
            if bool(g["is_relay"]):
                tempo = "disponibilità"
            elif pd.notna(g.get("entry_sec")):
                tempo = fmt_time(g["entry_sec"])
            else:
                tempo = "senza tempo"
            righe += (f'<div class="mf-row"><div class="mf-chi">'
                      f'<div class="mf-nome">'
                      f'{str(g.get("name") or g.get("etichetta"))}</div>'
                      f'<span class="badge-cat">'
                      f'{pool_label(g["pool_length"], breve=True)}</span></div>'
                      f'<div class="mf-dx"><div class="mf-tempo">{tempo}</div>'
                      f'</div></div>')
        st.html(f'<div class="glass-card" style="padding:12px 10px">{righe}</div>')


def disegna(modo: str = "nuova") -> None:
    """Disegna la pagina delle iscrizioni nel modo richiesto."""
    titolo, sottotitolo = MODI.get(modo, MODI["nuova"])
    page_header(titolo, sottotitolo)

    # Cambiando porta il riepilogo aperto non deve seguirci: era stato
    # costruito su un altro elenco di manifestazioni.
    if st.session_state.get("isc_modo") != modo:
        st.session_state["isc_modo"] = modo
        st.session_state.pop("isc_conferma", None)

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

    # ══════════════════════════════════════════════════════════════
    # Manifestazione
    # ══════════════════════════════════════════════════════════════
    ELENCO = _elenco_mie(mio_id) if modo == "modifica" else _elenco_aperte()

    if not ELENCO:
        if modo == "modifica":
            st.info("Non hai iscrizioni da cambiare su manifestazioni ancora "
                    "da nuotare. Quelle vecchie le trovi in Vedi le mie "
                    "iscrizioni.")
            if st.button("Vai a Iscriviti", type="primary",
                         use_container_width=True, key="isc_vai_nuova"):
                st.switch_page("views/iscrizioni_nuove.py")
        else:
            st.info("Nessuna manifestazione aperta alle iscrizioni in questo "
                    "momento. Le raccogliamo dai 30 giorni prima "
                    "dell'apertura ufficiale fino al giorno prima della "
                    "chiusura: le date le trovi in Agenda.")
        st.stop()

    opzioni = list(ELENCO)

    pre = st.session_state.pop("isc_comp", None)
    if pre is not None and int(pre) in ELENCO:
        st.session_state["isc_sel"] = int(pre)
    if st.session_state.get("isc_sel") not in opzioni:
        st.session_state["isc_sel"] = opzioni[0]

    def _etichetta_meet(comp_id: int) -> str:
        r = ELENCO[int(comp_id)]
        coda = "" if r.get("aperta", True) else "  ·  termine scaduto"
        return (f"{_giorno(r['start_date'])} · "
                f"{r.get('nome') or 'Manifestazione'}{coda}")

    def _azzera() -> None:
        """Cambiando manifestazione il riepilogo aperto non deve seguirci."""
        st.session_state.pop("isc_conferma", None)

    comp_id = st.selectbox("Manifestazione", opzioni, key="isc_sel",
                           format_func=_etichetta_meet, on_change=_azzera)
    riga = dict(ELENCO[int(comp_id)])

    # La finestra si rilegge a database: l'elenco qui sopra arriva da una
    # lettura cachata 60 secondi, e fra quella e adesso il termine puo'
    # essere scaduto.
    finestra = crud.finestra_iscrizioni(int(comp_id))
    massimo = finestra.get("max_gare")
    for c in ("chiusura", "ultimo_giorno"):
        if finestra.get(c) is not None:
            riga[c] = finestra[c]

    _scheda_manifestazione(riga, massimo)
    _scadenza(riga, bool(finestra.get("aperta")))

    gare = crud.gare_iscrizione(int(comp_id), mio_id)

    if not finestra.get("aperta"):
        # Termine scaduto: in Modifica le iscrizioni si vedono comunque, in
        # sola lettura, perche' e' la domanda per cui si e' aperta la pagina.
        st.warning(crud.motivo_chiusura(finestra))
        if modo == "modifica" and not gare.empty:
            section("Le tue gare")
            _elenco_iscritte(gare)
        st.stop()

    # Emulazione: si guarda e basta. Una riga scritta da qui sarebbe
    # indistinguibile da una scritta dall'atleta, quindi l'elenco delle gare
    # si ferma prima delle caselle.
    if auth.sola_lettura():
        st.info("Stai guardando come un altro atleta: da qui non si scrive. "
                "Per vedere le sue gare e i suoi tempi usa Vedi le mie "
                "iscrizioni.")
        st.stop()

    if gare.empty:
        st.info("Il programma gare non e' ancora stato caricato per questa "
                "manifestazione.")
        st.stop()

    individuali = gare[~gare["is_relay"].astype(bool)].copy()
    staffette = gare[gare["is_relay"].astype(bool)].copy()

    # ══════════════════════════════════════════════════════════════
    # Scelta delle gare
    # ══════════════════════════════════════════════════════════════
    # Le spunte e i tempi vivono in session_state con una chiave per gara,
    # cosi' sopravvivono ai rerun che servono a spegnere le caselle quando il
    # limite e' pieno. La chiave porta dentro il comp_id: cambiando
    # manifestazione si riparte da capo.

    def _k_sel(race_id: int) -> str:
        return f"isc_s_{int(comp_id)}_{int(race_id)}"

    def _k_tempo(race_id: int) -> str:
        return f"isc_t_{int(comp_id)}_{int(race_id)}"

    for _, g in gare.iterrows():
        rid = int(g["race_id"])
        st.session_state.setdefault(_k_sel(rid), pd.notna(g["entry_id"]))
        if not bool(g["is_relay"]):
            # Il campo parte con il tempo gia' dichiarato; se non c'e'
            # ancora, con il personale, che resta modificabile.
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

        Nome e vasca stanno nell'etichetta della casella e non in una colonna
        a parte: su un telefono tre colonne diventano tre righe, e una gara
        sola si mangiava mezzo schermo.
        """
        rid = int(g["race_id"])
        spuntata = bool(st.session_state.get(_k_sel(rid)))
        # Quando il limite e' pieno le gare non ancora scelte si spengono:
        # per cambiarne una bisogna prima togliere quella che non serve piu'.
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
        # Le gare arrivano gia' nell'ordine di programma: qui si mettono solo
        # le intestazioni di giornata e fascia dove il programma cambia. Se
        # la manifestazione non ce l'ha, torna un blocco solo senza titolo e
        # l'elenco resta quello di sempre.
        for titolo_blocco, fetta in blocchi_programma(individuali):
            if titolo_blocco:
                st.markdown(f'<div class="stroke-head">{titolo_blocco}</div>',
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
        st.caption("Qui dai solo la disponibilita': squadre e frazioni le "
                   "decide l'allenatore, e le staffette non contano nel "
                   "limite.")
        # Stesse intestazioni delle individuali: anche una staffetta ha la
        # sua giornata e la sua fascia, e vederle sparse non aiuterebbe
        # nessuno. I blocchi si calcolano sulle sole staffette, quindi la
        # numerazione delle fasce e' quella loro.
        for titolo_blocco, fetta in blocchi_programma(staffette):
            if titolo_blocco:
                st.markdown(f'<div class="stroke-head">{titolo_blocco}</div>',
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

    # ══════════════════════════════════════════════════════════════
    # Riepilogo e conferma
    # ══════════════════════════════════════════════════════════════
    scelte = _scelte()

    if not st.session_state.get("isc_conferma"):
        if st.button("Rivedi e conferma", type="primary",
                     use_container_width=True):
            st.session_state["isc_conferma"] = True
            st.rerun()
        return

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
