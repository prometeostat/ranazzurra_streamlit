"""
views/_calcolatore_comune.py — i pezzi che le due modalita' si dividono.

Calcolatore Punti e Calcolatore Tempo chiedono le stesse quattro cose (gara,
vasca, sesso, categoria) e si distinguono solo per l'ultimo campo e per il
risultato. Quello che hanno in comune sta qui, cosi' un cambio ai selettori
vale per tutte e due e non si rischia che una pagina si comporti in modo
diverso dall'altra.

Il calcolo vero non sta qui: sta in punteggi.py, che non importa Streamlit.
Questo file e' interfaccia e niente altro.
"""
from __future__ import annotations

import html

import pandas as pd
import streamlit as st

import auth
import punteggi
import season as season_mod
from theme import pool_label, section
from views._common import anagrafica, season_year

# Vasca: il nome del campo e' lo stesso del filtro di sistema, ma qui la
# scelta e' secca, non c'e' "Tutte". Le tabelle federali sono due, una per
# vasca, e un punteggio senza vasca non esiste.
VASCHE = {"25m — vasca corta": 25, "50m — vasca lunga": 50}


def carica_tabella() -> pd.DataFrame | None:
    """
    I tempi base, o None con il motivo a video.

    Un errore qui non e' un dettaglio: senza tabella federale non c'e'
    niente da calcolare, e un punteggio sbagliato e' peggio di un punteggio
    mancante. Quindi si dice cosa non torna e si ferma la pagina.
    """
    try:
        return punteggi.tabella()
    except punteggi.TempiBaseNonValidi as e:
        st.error(f"Non riesco a leggere i tempi base. {e}", icon="⚠️")
        st.caption("Il file si chiama "
                   f"`dati/{punteggi.FILE_TEMPI_BASE.name}` ed e' la tabella "
                   "FIN delle gare individuali. Avvisa l'amministratore.")
        return None
    except Exception as e:                                # noqa: BLE001
        st.error(f"Non riesco a leggere i tempi base: {e}", icon="⚠️")
        return None


def _mie_impostazioni() -> tuple[str | None, str | None]:
    """
    Sesso e categoria di chi sta usando l'app, per partire dai suoi valori.

    Legge l'anagrafica gia' cachata, la stessa del Profilo: nessuna query in
    piu'. Se l'account non e' agganciato a una scheda atleta non si indovina
    niente e i selettori partono dal primo valore.

    Nota sui nomi: season_mod.master_category() torna "M45" per un maschio e
    "F45" per una femmina, mentre nella tabella FIN "M45" vuol dire Master
    45 e il sesso sta a parte. Qui si prende solo la fascia numerica, che e'
    l'unica cosa che le due scritture hanno in comune.
    """
    mio = (auth.current_user() or {}).get("athlete_id")
    if mio is None:
        return None, None
    tutti = anagrafica(season_year())
    if tutti.empty:
        return None, None
    riga = tutti[tutti["athlete_id"] == mio]
    if riga.empty:
        return None, None
    r = riga.iloc[0]
    sesso = str(r.get("sex") or "").upper()[:1] or None
    anno = int(r["birth_year"]) if pd.notna(r.get("birth_year")) else None
    if anno is None:
        return sesso, None
    banda = season_mod.master_band(anno, season_year())
    return sesso, punteggi.categoria_da_banda(banda)


def _predefinito(chiave: str, valori: list, suggerito=None):
    """
    Allinea un valore in sessione all'elenco che esiste adesso.

    Serve perche' cambiando vasca l'elenco delle gare cambia (i 100 misti
    esistono solo in corta) e Streamlit protesta se la chiave in sessione
    porta un valore che non e' piu' tra le opzioni. Si sistema prima di
    creare il widget.
    """
    if st.session_state.get(chiave) in valori:
        return
    st.session_state[chiave] = (suggerito if suggerito in valori
                                else valori[0])


def scelte(tb: pd.DataFrame, prefisso: str) -> dict:
    """
    I quattro selettori. Torna gara, vasca, sesso, categoria e il tempo base
    corrispondente (cent_base, None se quella casella della tabella e' vuota).

    L'ordine dei campi segue il ragionamento di chi li compila: prima la
    vasca, perche' decide quali gare esistono, poi la gara, poi chi sei.
    """
    mio_sesso, mia_categoria = _mie_impostazioni()

    # Due per riga anche sul telefono. A uno per riga i quattro selettori si
    # mangiavano mezzo schermo e spingevano il risultato sotto il bordo, che
    # e' il contrario di quello che serve a chi fa un conto. Il CSS sta in
    # theme.py, agganciato alla chiave calc_scelte.
    with st.container(key=f"calc_scelte_{prefisso}"):
        c1, c2 = st.columns(2)
        etichette = list(VASCHE)
        _predefinito(f"{prefisso}_vasca", etichette)
        vasca = VASCHE[c1.selectbox("Vasca", options=etichette,
                                    key=f"{prefisso}_vasca")]

        elenco_gare = punteggi.gare(tb, vasca)
        _predefinito(f"{prefisso}_gara", elenco_gare)
        gara = c2.selectbox("Gara", options=elenco_gare,
                            key=f"{prefisso}_gara")

        c3, c4 = st.columns(2)
        sessi = list(punteggi.SESSI)
        _predefinito(f"{prefisso}_sesso", sessi, mio_sesso)
        sesso = c3.selectbox(
            "Sesso", options=sessi, key=f"{prefisso}_sesso",
            format_func=lambda s: punteggi.ETICHETTE_SESSO.get(s, s))

        elenco_cat = punteggi.categorie(tb, vasca)
        _predefinito(f"{prefisso}_categoria", elenco_cat, mia_categoria)
        categoria = c4.selectbox(
            "Categoria", options=elenco_cat, key=f"{prefisso}_categoria",
            format_func=punteggi.etichetta_categoria)

    return {"gara": gara, "vasca": vasca, "sesso": sesso,
            "categoria": categoria,
            "cent_base": punteggi.tempo_base(tb, gara, vasca, sesso, categoria)}


def riquadro_tempo_base(s: dict) -> None:
    """Il tempo base scelto, scritto in chiaro: e' il numero da cui dipende
    tutto il resto e chi ha la tabella federale sotto mano deve poterlo
    confrontare in un secondo."""
    cent = s["cent_base"]
    valore = punteggi.testo_da_cent(cent) if cent is not None else "—"
    tono = "" if cent is not None else "gold"
    st.markdown(
        f'<div class="kpi-wrap">'
        f'<div class="kpi-val {tono}">{html.escape(valore)}</div>'
        f'<div class="kpi-lbl">Tempo base · 1000 punti</div>'
        f'<div class="kpi-sub">{html.escape(str(s["gara"]))} · '
        f'{html.escape(punteggi.ETICHETTE_SESSO.get(s["sesso"], s["sesso"]))} · '
        f'{html.escape(punteggi.etichetta_categoria(s["categoria"]))} · '
        f'{html.escape(pool_label(s["vasca"]))}</div>'
        f'<div class="kpi-sub">Tabella FIN {punteggi.STAGIONE_TABELLA}</div>'
        f'</div>', unsafe_allow_html=True)


def riga_scarto(scarto_cent: int | None) -> str:
    """'1.37 piu' veloce del tempo base', o il contrario. Lo scarto e' in
    centesimi e positivo vuol dire sotto il tempo base."""
    if scarto_cent is None:
        return ""
    if scarto_cent == 0:
        return "Esattamente il tempo base."
    quanto = punteggi.testo_da_cent(abs(scarto_cent))
    verso = "piu' veloce del" if scarto_cent > 0 else "piu' lento del"
    return f"{quanto} {verso} tempo base."


def nota_in_fondo() -> None:
    st.caption(
        f"Il punteggio si calcola con la formula FIN, lineare: "
        f"(tempo base ÷ tempo realizzato) × 1000. Nuotare il tempo base vale "
        f"1000 punti esatti. I tempi base sono quelli della tabella "
        f"individuale {punteggi.STAGIONE_TABELLA}, come pubblicata: l'app non "
        "li ricalcola. Le cifre dopo il centesimo si tagliano, non si "
        "arrotondano.")


# ══════════════════════════════════════════════════════════════════
# Il campo del tempo e il bottone
# ══════════════════════════════════════════════════════════════════
# Il tempo si scrive in tre caselle numeriche, non in un campo di testo:
# sul telefono apre la tastiera dei numeri, non si puo' digitare niente di
# storto, e si vede a colpo d'occhio dove vanno i minuti e dove i centesimi.
# Le frecciette di st.number_input sono nascoste dal CSS (vedi theme.py,
# .st-key-calc_azione): su tre caselle affiancate mangiavano tutto lo
# spazio, e nessuno regola un tempo di gara un centesimo per clic.
#
# Tutto sta dentro un st.form: il conto si fa quando si premo Calcola, non
# mentre si digita, cosi' non compaiono punteggi a mezzo mentre si scrive il
# secondo numero. Il form sta a sua volta in un container con la chiave
# calc_azione, perche' st.form non lascia una classe st-key- a cui
# agganciare il CSS del bottone verde.

CHIAVE_AZIONE = "calc_azione"


def campo_tempo(prefisso: str) -> tuple[int | None, str | None, bool]:
    """
    'Inserisci tempo' con le tre caselle e il bottone Calcola.

    Torna (centesimi, errore, premuto). `premuto` e' vero nel giro in cui si
    e' cliccato Calcola: la pagina mostra il risultato solo allora.
    """
    section("Inserisci tempo")
    with st.container(key=CHIAVE_AZIONE):
        with st.form(key=f"{prefisso}_form", border=False):
            c1, c2, c3 = st.columns(3)
            mm = c1.number_input("Minuti", min_value=0, max_value=59, step=1,
                                 key=f"{prefisso}_mm", format="%d")
            ss = c2.number_input("Secondi", min_value=0, max_value=59, step=1,
                                 key=f"{prefisso}_ss", format="%d")
            cc = c3.number_input("Centesimi", min_value=0, max_value=99,
                                 step=1, key=f"{prefisso}_cc", format="%d")
            premuto = st.form_submit_button(
                "Calcola", type="primary", use_container_width=True)
    cent, err = punteggi.cent_da_pezzi(mm, ss, cc)
    return cent, err, bool(premuto)


def campo_punteggio(prefisso: str) -> tuple[object, str | None, bool]:
    """
    'Punteggio desiderato' con il suo bottone Calcola.

    Stessa forma di campo_tempo(): (punteggio, errore, premuto). Qui una
    casella sola basta, ma resta numerica e dentro al form per le stesse
    ragioni.
    """
    section("Punteggio desiderato")
    with st.container(key=CHIAVE_AZIONE):
        with st.form(key=f"{prefisso}_form", border=False):
            valore = st.number_input(
                "Punti FIN", min_value=0.0, max_value=5000.0, step=10.0,
                format="%.2f", key=f"{prefisso}_punti",
                help="Il tempo base vale 1000 punti.")
            premuto = st.form_submit_button(
                "Calcola", type="primary", use_container_width=True)
    # Zero e' lo stato in cui la pagina si apre, non un errore.
    if not valore:
        return None, None, bool(premuto)
    # Si passa per il parser di punteggi, che e' l'unico posto dove vive la
    # regola sui due decimali: la casella numerica ne accetta anche di piu'.
    p, err = punteggi.punti_da_testo(f"{float(valore):.2f}")
    return p, err, bool(premuto)
