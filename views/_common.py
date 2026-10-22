"""
views/_common.py — pezzi di interfaccia condivisi fra le pagine.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

import auth
import data
import season as season_mod
from theme import fmt_int


# ══════════════════════════════════════════════════════════════════
# Stato condiviso
# ══════════════════════════════════════════════════════════════════

def season_year() -> int:
    return int(st.session_state.get("season_year", season_mod.current_season_year()))


def pool_filter() -> str:
    return st.session_state.get("pool_filter", "Tutte")


# Etichetta mostrata -> nome dello stile a database. A DB la farfalla si
# chiama "Farfalla", in vasca la chiamano tutti delfino.
TUTTE_LE_GARE = "Tutte le gare"
STILI_UI = {
    "Stile Libero": "Stile Libero",
    "Dorso": "Dorso",
    "Rana": "Rana",
    "Delfino": "Farfalla",
    "Misti": "Misti",
}


def stroke_filter() -> str:
    return st.session_state.get("stroke_filter", TUTTE_LE_GARE)


# ══════════════════════════════════════════════════════════════════
# Programma di gara: giornate e fasce orarie
# ══════════════════════════════════════════════════════════════════
# Le gare di una manifestazione si susseguono per giornata e per fascia
# oraria. A database stanno in races.race_date e races.session (1 mattino,
# 2 pomeriggio, 3 sera), tutte e due nullable: lo storico le ha vuote e
# ricade sull'elenco piatto di sempre.
SESSIONI = {1: "Mattino", 2: "Pomeriggio", 3: "Sera"}
# Il nome del giorno senza passare dal locale di sistema, che su Streamlit
# Cloud e' inglese e non si puo' dare per buono.
GIORNI_SETTIMANA = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì",
                    "sabato", "domenica"]


def etichetta_giornata(quando) -> str:
    """'sabato 21/11': il giorno della settimana dice piu' dell'anno."""
    d = pd.to_datetime(quando, errors="coerce")
    if pd.isna(d):
        return ""
    return f"{GIORNI_SETTIMANA[d.weekday()]} {d.strftime('%d/%m')}"


def blocchi_programma(gare: pd.DataFrame) -> list[tuple[str, pd.DataFrame]]:
    """
    Spezza le gare in blocchi (intestazione, righe) seguendo il programma.

    L'ordine arriva gia' dalla query: qui si taglia dove cambia la coppia
    giornata/fascia, che per questo deve essere contigua. La data compare
    nell'intestazione solo se le giornate sono piu' di una: su una
    manifestazione di un giorno solo ripeterla a ogni blocco e' rumore.

    Se nessuna gara ha il programma compilato torna un blocco unico senza
    intestazione, cioe' l'elenco piatto di prima. Le gare senza programma
    dentro una manifestazione che ce l'ha finiscono invece in un blocco
    finale dichiarato, non mescolate alle altre.
    """
    if gare.empty:
        return []

    vuota = pd.Series([pd.NA] * len(gare), index=gare.index)
    quando = pd.to_datetime(gare["race_date"] if "race_date" in gare.columns
                            else vuota, errors="coerce")
    fascia = pd.to_numeric(gare["session"] if "session" in gare.columns
                           else vuota, errors="coerce")

    if quando.isna().all() and fascia.isna().all():
        return [("", gare)]

    piu_giornate = quando.dropna().dt.date.nunique() > 1

    def _titolo(giorno, numero) -> str:
        pezzi = []
        if piu_giornate and giorno is not None:
            pezzi.append(etichetta_giornata(giorno).capitalize())
        if numero in SESSIONI:
            pezzi.append(SESSIONI[numero])
        return " · ".join(pezzi) or "Orario non indicato"

    chiavi = [(d.date() if pd.notna(d) else None,
               int(f) if pd.notna(f) else None)
              for d, f in zip(quando, fascia)]

    blocchi: list[tuple[str, pd.DataFrame]] = []
    inizio = 0
    for i in range(1, len(chiavi) + 1):
        if i == len(chiavi) or chiavi[i] != chiavi[inizio]:
            blocchi.append((_titolo(*chiavi[inizio]), gare.iloc[inizio:i]))
            inizio = i
    return blocchi


# Manifestazioni ufficiali FIN o no. A database e' competitions.is_fin, qui
# dentro gira come None / True / False: None vuol dire "non filtrare".
TUTTE_LE_MANIF = "Tutte"
FIN_UI = {TUTTE_LE_MANIF: None, "Ufficiali FIN": True, "Non ufficiali": False}


def fin_filter() -> bool | None:
    """Valore da passare ai loader: None, True o False."""
    return FIN_UI.get(st.session_state.get("fin_filter", TUTTE_LE_MANIF))


def etichetta_punti(is_fin, lunga: bool = False) -> str:
    """Come si chiamano i punti di quella manifestazione.

    `athlete_races.fin_score` porta due grandezze diverse: sulle gare del
    calendario federale e' il punteggio FIN, sulle giornate di circuito e' il
    punteggio del regolamento Acquasport (10-8-7-6-5-4-3-2-1 ai primi nove).
    Chiamarli tutti "punti FIN" e' sbagliato, e fa sembrare un errore un 10
    accanto a un tempo.

    `lunga` da' la forma "punteggio ...", per le etichette dei riquadri.
    """
    nome = "FIN" if bool(is_fin) else "Acquasport"
    return f"punteggio {nome}" if lunga else f"punti {nome}"


def apply_fin(df: pd.DataFrame, col: str = "is_fin") -> pd.DataFrame:
    """Stesso filtro, ma su un DataFrame gia' caricato.

    Serve solo dove la riga e' la manifestazione (l'agenda): sui tempi il
    filtro deve stare nella query, perche' li' c'e' di mezzo il miglior tempo
    per atleta e scartare righe dopo lascerebbe dei buchi.
    """
    scelta = fin_filter()
    if scelta is None or df.empty or col not in df.columns:
        return df
    return df[df[col].astype(bool) == scelta].copy()


def apply_stroke(df: pd.DataFrame, col: str = "stroke") -> pd.DataFrame:
    scelta = stroke_filter()
    if scelta == TUTTE_LE_GARE or df.empty or col not in df.columns:
        return df
    return df[df[col] == STILI_UI.get(scelta, scelta)].copy()


def apply_pool(df: pd.DataFrame, col: str = "pool_length") -> pd.DataFrame:
    pf = pool_filter()
    if pf == "Tutte" or df.empty or col not in df.columns:
        return df
    return df[df[col] == int(pf.replace("m", ""))].copy()


# ══════════════════════════════════════════════════════════════════
# Classifiche: il parimerito
# ══════════════════════════════════════════════════════════════════
# Nel nuoto il cronometro si ferma al centesimo: due atleti con lo stesso
# tempo al centesimo hanno fatto lo stesso risultato e stanno nella stessa
# posizione, punto. Il confronto si fa quindi sui centesimi interi e non sui
# secondi in virgola mobile, che per la stessa prestazione possono uscire
# 28.9 da una parte e 28.900000000000002 dall'altra e romperebbero il
# parimerito senza che si veda a video.


def centesimi(tempi: pd.Series) -> pd.Series:
    """Il tempo in centesimi interi, che e' la precisione della disciplina."""
    return (pd.to_numeric(tempi, errors="coerce") * 100).round().astype("Int64")


def classifica(df: pd.DataFrame, colonna: str = "pb_sec",
               quanti: int | None = None,
               a_parita: tuple[str, ...] = (),
               uno_per: str | None = None) -> pd.DataFrame:
    """
    Ordina una classifica e assegna le posizioni, parimerito compresi.

    Restituisce una copia con due colonne in piu': `posizione` (1, 1, 2, 2,
    3: chi ha lo stesso tempo ha lo stesso numero e la numerazione non salta)
    e `tempo_cent`, il tempo in centesimi su cui la posizione e' stata decisa.
    La riga resta quella di partenza, intera: data, manifestazione e link
    sono quelli della gara in cui quel tempo e' stato nuotato davvero, anche
    quando due atleti a pari merito arrivano da due manifestazioni diverse.

    `a_parita` sono le colonne che mettono in fila chi ha lo stesso tempo, per
    non lasciare l'ordine al caso: servono solo a video e non toccano la
    posizione, che dipende dal solo tempo.

    `uno_per` tiene una riga sola per soggetto (`athlete_id` nelle classifiche
    di squadra): fra le sue sopravvive la prima secondo l'ordine qui sopra,
    cioe' il tempo migliore e, a parita' di tempo, quello che decide
    `a_parita`. Le posizioni si calcolano dopo, se no un secondo tempo dello
    stesso atleta si porterebbe via un gradino e la numerazione salterebbe.

    `quanti` taglia la classifica alle prime N righe, ma **estesa a tutto il
    parimerito**: se la N-esima e la N+1-esima hanno lo stesso tempo escono
    tutte e due. Tagliare a N righe secche faceva sparire dalla classifica un
    atleta che in quella posizione ci stava a pieno titolo.
    """
    if df.empty or colonna not in df.columns:
        return df.copy()

    fuori = df.copy()
    fuori["tempo_cent"] = centesimi(fuori[colonna])
    fuori = fuori[fuori["tempo_cent"].notna()]
    if fuori.empty:
        fuori["posizione"] = pd.Series(dtype="int64")
        return fuori

    # mergesort perche' e' stabile: a parita' di chiave l'ordine di partenza
    # resta quello, e due letture della stessa pagina danno la stessa fila.
    chiavi = ["tempo_cent"] + [c for c in a_parita if c in fuori.columns]
    fuori = fuori.sort_values(chiavi, kind="mergesort").reset_index(drop=True)

    if uno_per and uno_per in fuori.columns:
        fuori = fuori.drop_duplicates(subset=uno_per, keep="first")

    fuori["posizione"] = (fuori["tempo_cent"].rank(method="dense")
                          .astype(int))

    if quanti is not None and len(fuori) > quanti:
        limite = int(fuori["tempo_cent"].iloc[quanti - 1])
        fuori = fuori[fuori["tempo_cent"] <= limite]
    return fuori.reset_index(drop=True)


def anagrafica(sy: int | None = None) -> pd.DataFrame:
    """
    Anagrafica completa per la stagione scelta: chi ha gareggiato piu' chi e'
    solo a ruolino. Serve al selettore atleta, che deve mostrare tutti.
    """
    sy = season_year() if sy is None else sy
    tutti = data.load_all_athletes(sy)
    if tutti.empty:
        return tutti
    return tutti[tutti["is_deleted"] != True].copy()   # noqa: E712


def selected_athlete() -> pd.Series | None:
    """
    L'atleta aperto. Chiunque puo' vedere chiunque: se non e' stato scelto
    nessuno restituisce None e la pagina mostra l'invito a sceglierlo.
    """
    aid = st.session_state.get("athlete_id")
    if aid is None:
        return None
    sy = season_year()
    for df in (data.load_athletes(sy), anagrafica(sy)):
        if df.empty:
            continue
        riga = df[df["athlete_id"] == aid]
        if not riga.empty:
            return riga.iloc[0]
    return None


def apri_atleta(athlete_id: int) -> None:
    """Apre la scheda di un atleta da qualunque punto dell'app."""
    st.session_state["athlete_id"] = int(athlete_id)
    st.session_state["scheda_aperta"] = True


# ══════════════════════════════════════════════════════════════════
# Preferiti
# ══════════════════════════════════════════════════════════════════
# Le stelle stanno a database, su `athlete_favorites`, legate a chi le ha
# messe: sopravvivono al refresh, al logout e al cambio di dispositivo.
# Prima vivevano in `st.session_state` e duravano quanto la sessione, che su
# Community Cloud finisce da sola appena l'app va in pausa.
#
# Chi usa l'app senza essere collegato a una scheda atleta (l'ospite della
# modalita' "open", o un account che l'anagrafica non ha agganciato) non ha
# una riga a cui legarle: per lui restano in sessione come prima. E' l'unico
# caso rimasto, e la pagina Profilo lo dice.


def _chi_guarda() -> int | None:
    """L'atleta a cui appartengono le stelle, o None se non ce n'e' uno."""
    aid = (auth.current_user() or {}).get("athlete_id")
    return None if aid is None else int(aid)


def preferiti() -> list[int]:
    """Gli id degli atleti preferiti, in ordine alfabetico."""
    chi = _chi_guarda()
    if chi is None:
        return [int(x) for x in st.session_state.get("preferiti", [])]
    # import locale: crud importa db, e tenerlo in cima a questo modulo
    # allungherebbe l'avvio di ogni pagina anche dove le stelle non servono
    import crud
    df = crud.preferiti_di(chi)
    return [] if df.empty else [int(x) for x in df["athlete_id"].dropna()]


def preferiti_dettaglio() -> pd.DataFrame:
    """
    I preferiti con il nome gia' dentro, per la pagina Profilo.

    Li porta su la query, non l'anagrafica della stagione scelta: un
    preferito che quest'anno non ha ancora gareggiato, o che ha smesso,
    deve comparire lo stesso. Prima l'elenco si incrociava con l'anagrafica
    del periodo e quelli fuori sparivano dalla pagina, stella compresa, e
    non c'era piu' modo di toglierla.
    """
    vuoto = pd.DataFrame(columns=["athlete_id", "full_name", "inattivo"])
    chi = _chi_guarda()
    if chi is not None:
        import crud
        return crud.preferiti_di(chi)

    ids = preferiti()
    tutti = anagrafica()
    if not ids or tutti.empty:
        return vuoto
    fuori = tutti[tutti["athlete_id"].isin(ids)][["athlete_id", "full_name"]].copy()
    fuori["inattivo"] = False
    return fuori


def e_preferito(athlete_id: int) -> bool:
    return int(athlete_id) in preferiti()


def toggle_preferito(athlete_id: int) -> None:
    """
    Accende o spegne la stella, scrivendo subito a database.

    Durante un'emulazione non si scrive: la riga finirebbe addosso
    all'atleta emulato e sarebbe indistinguibile da una sua.
    """
    aid = int(athlete_id)
    chi = _chi_guarda()

    if chi is None:
        pref = preferiti()
        st.session_state["preferiti"] = ([x for x in pref if x != aid]
                                         if aid in pref else pref + [aid])
        return

    if auth.sola_lettura():
        st.toast("Stai guardando come un altro atleta: i preferiti non si "
                 "toccano.", icon="👁")
        return

    import crud
    fatto = (crud.togli_preferito(chi, aid) if aid in preferiti()
             else crud.aggiungi_preferito(chi, aid))
    if not fatto:
        # Manca la tabella `athlete_favorites`: il codice e' arrivato prima
        # della migrazione. Meglio dirlo che lasciare la stella che non
        # reagisce senza spiegare perche'.
        st.toast("I preferiti non sono ancora attivi su questo database.",
                 icon="⚠️")


# ══════════════════════════════════════════════════════════════════
# Blocchi di interfaccia
# ══════════════════════════════════════════════════════════════════

def no_athlete_notice() -> None:
    st.info("Scegli un atleta dalla Scheda atleta per vedere questa pagina.")
    st.page_link("views/scheda.py", label="Vai alla scheda atleta →")


def hero(row: pd.Series) -> None:
    initials = (str(row["first_name"])[:1] + str(row["last_name"])[:1]).upper()
    sex_emoji = "♂️" if row["sex"] == "M" else "♀️"
    anno = row.get("birth_year")
    anno = int(anno) if pd.notna(anno) else None
    cat = season_mod.master_category(anno, season_year(), row.get('sex'))
    squadra = row.get("team") or "—"
    st.markdown(f"""
<div class="glass-card" style="border-left:4px solid var(--teal);
     background:linear-gradient(120deg,rgba(0,194,199,0.06),rgba(10,22,40,0.3));">
  <div style="display:flex; align-items:center; gap:20px;">
    <div style="width:70px;height:70px;border-radius:50%;
         background:linear-gradient(135deg,#1a3a6e,#00c2c7);
         display:flex;align-items:center;justify-content:center;
         font-family:'Bebas Neue',sans-serif;font-size:26px;color:#0a1628;
         box-shadow:0 0 30px rgba(0,194,199,0.4);flex-shrink:0;">{initials}</div>
    <div>
      <div class="hero-name">{str(row['full_name']).title()}</div>
      <div class="hero-sub">{squadra}</div>
      <div class="hero-meta">{sex_emoji} {cat}
           &nbsp;·&nbsp; anno <span>{anno if anno else '—'}</span>
           &nbsp;·&nbsp; cod. FIN <span>{fmt_int(row.get('fin_code'))}</span></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    sub = (f'<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:12px;'
           f'letter-spacing:2px;color:var(--muted);text-transform:uppercase">{subtitle}</div>'
           if subtitle else "")
    st.markdown(
        f"""<div style="margin-bottom:8px">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:30px;letter-spacing:4px;
             color:var(--white)">{title}</div>{sub}</div>""",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════
# Filtri in pagina, sincronizzati con la barra laterale
# ══════════════════════════════════════════════════════════════════

def _sync(src: str, dst: str) -> None:
    """Callback: copia il valore del widget di pagina nello stato condiviso."""
    st.session_state[dst] = st.session_state[src]


def inline_filters(prefix: str = "pg", pool: bool = True,
                   strokes: bool = False, fin: bool = True,
                   on_fin=None) -> None:
    """
    Periodo (All Time o singola stagione), vasca, manifestazioni ufficiali e,
    dove serve, tipo di gara. Usa chiavi proprie e ricopia la scelta in
    season_year / pool_filter / fin_filter / stroke_filter con on_change: il
    callback gira a inizio rerun, quindi le pagine si ridisegnano gia'
    allineate.

    on_fin e' un callback in piu' per chi deve reagire al cambio di filtro
    (la pagina Manifestazioni, che butta via la tabella aperta).
    """
    cols = st.columns([3, 4] if pool else [1])
    seasons = data.load_seasons()
    options = [season_mod.ALL] + seasons
    cur = season_year()
    if cur not in options:
        options = [cur] + options

    k_season = f"{prefix}_season"
    st.session_state[k_season] = cur        # tiene allineato il widget
    cols[0].selectbox("Periodo", options=options, key=k_season,
                      format_func=season_mod.label,
                      on_change=_sync, args=(k_season, "season_year"))

    if pool:
        k_pool = f"{prefix}_pool"
        st.session_state[k_pool] = pool_filter()
        cols[1].radio("Vasca", ["25m", "50m", "Tutte"], horizontal=True, key=k_pool,
                      on_change=_sync, args=(k_pool, "pool_filter"),
                      help="Tutte include anche le gare di fondo, che non hanno "
                           "una lunghezza vasca.")

    if fin:
        k_fin = f"{prefix}_fin"
        st.session_state[k_fin] = st.session_state.get("fin_filter",
                                                       TUTTE_LE_MANIF)

        def _sync_fin() -> None:
            st.session_state["fin_filter"] = st.session_state[k_fin]
            if on_fin is not None:
                on_fin()

        st.radio("Manifestazioni", list(FIN_UI), horizontal=True, key=k_fin,
                 on_change=_sync_fin,
                 help="Ufficiali FIN sono le gare del calendario federale. "
                      "Fuori restano il circuito Aquasport, le traversate in "
                      "acque libere e le gare sociali.")

    if strokes:
        k_stile = f"{prefix}_stile"
        st.session_state[k_stile] = stroke_filter()
        st.radio("Gara", [TUTTE_LE_GARE] + list(STILI_UI), horizontal=True,
                 key=k_stile, on_change=_sync, args=(k_stile, "stroke_filter"))
