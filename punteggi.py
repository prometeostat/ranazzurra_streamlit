"""
punteggi.py — tempi base FIN master e punteggio, senza interfaccia.

Qui dentro non si importa Streamlit e non si tocca il database: sono tempi
base letti da un foglio Excel e quattro operazioni di aritmetica. La
separazione non e' un vezzo, serve a poter provare il calcolo da un
terminale, senza alzare l'app e senza una connessione a Postgres.

Le pagine che lo usano stanno in views/calcolatore*.py.


La formula
──────────
Il punteggio master della FIN e' lineare:

    P = (TB / TR) x 1000

dove TB e' il tempo base della tabella federale per quella combinazione di
gara, vasca, sesso e categoria, e TR e' il tempo realizzato. Nuotare
esattamente il tempo base vale 1000 punti, andare piu' forte vale di piu'.

Le cifre dopo il centesimo si tagliano, non si arrotondano: 1012.3489
diventa 1012.34 e non 1012.35.

Il calcolo gira su numeri interi di centesimi, non su float. Un tempo di
gara e' un numero intero di centesimi di secondo per definizione (il
cronometro si ferma li'), e 24.48 in virgola mobile non e' 24.48 ma
24.480000000000000426...: a forza di dividere e moltiplicare quell'errore
esce a video. Con gli interi la divisione intera *e'* il troncamento, quindi
il risultato e' esatto per costruzione e non dipende dalla precisione di un
contesto decimale.


Il file dei tempi base
──────────────────────
Unica fonte: dati/mst_tb_ind_2026-2027b.xlsx, la tabella FIN 2026/2027 per
le gare individuali. Niente valori scritti nel codice, niente letture dal
web: se la tabella cambia si sostituisce il file e basta.

Tre fogli, di cui si leggono i primi due:

  - "TEMPI BASE VASCA CORTA - EXCEL"   593 righe, vasca 25
  - "TEMPI BASE VASCA LUNGA - EXCELL"  564 righe, vasca 50
  - "VERIFICA"                         l'unione delle due, per controllo

Colonne: KEY, CATEG, COD GARA, GARA, SESSO, VASCA, CENT TOT,
TEMPO (mmsscc), TEMPO PRINT, MIN, SEC, CENT.

Il tempo base si prende da **CENT TOT**, che e' il tempo in centesimi
interi (11826 = 1:58.26). Le altre colonne del tempo sono tre scritture
diverse della stessa cosa e in otto righe su 1157 non vanno d'accordo con
CENT TOT. CENT TOT e' l'unica senza ambiguita' di lettura, ed e' l'unica
giusta nei tre casi in cui il disaccordo e' grosso (CENT = 100 stampato
senza riportare il secondo: "1:13.100" dove CENT TOT dice 1:14.00).
Nelle altre cinque righe il disaccordo e' di un centesimo.

Le righe discordi non si correggono: si leggono da CENT TOT e si mostrano
in chiaro nel pannello di controllo della pagina, cosi' chi ha il PDF
federale sotto gli occhi puo' verificarle. Vedi anomalie().

Le combinazioni assenti dal foglio (M100 nelle gare lunghe, M95 in qualche
farfalla: 19 in vasca corta e 14 in vasca lunga) restano assenti. Non si
interpolano: senza tempo base non c'e' punteggio, e la pagina lo dice.
"""
from __future__ import annotations

import datetime as _dt
import re
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal
from functools import lru_cache
from pathlib import Path

import pandas as pd

# ══════════════════════════════════════════════════════════════════
# Il file e la sua forma
# ══════════════════════════════════════════════════════════════════

CARTELLA_DATI = Path(__file__).resolve().parent / "dati"
FILE_TEMPI_BASE = CARTELLA_DATI / "mst_tb_ind_2026-2027b.xlsx"
STAGIONE_TABELLA = "2026/2027"

# Foglio da cui leggere, per vasca.
FOGLI = {
    25: "TEMPI BASE VASCA CORTA - EXCEL",
    50: "TEMPI BASE VASCA LUNGA - EXCELL",
}

# Colonne che devono esserci. Se il foglio cambia intestazione il
# caricamento si ferma con un messaggio, invece di produrre punteggi finti.
COLONNE_RICHIESTE = ("CATEG", "COD GARA", "GARA", "SESSO", "VASCA",
                     "CENT TOT", "TEMPO (mmsscc)", "MIN", "SEC", "CENT")

VASCHE = (25, 50)
SESSI = ("F", "M")
ETICHETTE_SESSO = {"F": "Femmine", "M": "Maschi"}

# Limiti di buon senso, non di legge: servono solo a non far passare per
# tempo base un numero che non lo e'.
CENT_MIN = 100              # 1.00, piu' veloce di qualunque 50
CENT_MAX = 360_000 * 10     # dieci ore


class TempiBaseNonValidi(RuntimeError):
    """Il foglio Excel non ha la forma attesa: meglio fermarsi che calcolare."""


# ══════════════════════════════════════════════════════════════════
# Tempi: testo <-> centesimi interi
# ══════════════════════════════════════════════════════════════════
# Si accettano le scritture che si usano a bordo vasca: 24.48, 1:58.26,
# 15:59.78, e con le ore per i 1500 lunghi delle categorie alte. La virgola
# vale come il punto, che sulla tastiera del telefono viene piu' comoda.

_TEMPO_RE = re.compile(
    r"^(?:(\d{1,2}):)?(?:(\d{1,2}):)?(\d{1,2})(?:[.,](\d{1,2}))?$")

_ERRORE_TEMPO = ('Tempo non valido: "{t}". Si scrive 24.48 per i secondi, '
                 "1:58.26 con i minuti, 42:58.51 per le distanze lunghe.")


def cent_da_testo(testo: str | None) -> tuple[int | None, str | None]:
    """
    Tempo scritto a mano -> centesimi interi. Ritorna (valore, errore).

    Vuoto non e' un errore, e' "non ha ancora scritto niente": torna
    (None, None) e la pagina sta zitta.
    """
    testo = (testo or "").strip()
    if not testo:
        return None, None
    m = _TEMPO_RE.match(testo)
    if not m:
        return None, _ERRORE_TEMPO.format(t=testo)
    a, b, sec, dec = m.groups()
    # Un solo gruppo prima dei secondi sono i minuti, due sono ore e minuti.
    ore, minuti = (int(a), int(b)) if b is not None else (0, int(a or 0))
    sec = int(sec)
    if minuti > 59 or sec > 59:
        return None, (f'Tempo non valido: "{testo}". Minuti e secondi vanno '
                      "da 0 a 59.")
    # Una cifra sola dopo il punto sono decimi: 24.4 e' 24.40.
    cent = int((dec or "0").ljust(2, "0"))
    totale = ore * 360_000 + minuti * 6_000 + sec * 100 + cent
    if totale <= 0:
        return None, "Un tempo di zero non esiste."
    if totale > CENT_MAX:
        return None, f'Tempo fuori scala: "{testo}".'
    return totale, None


def cent_da_pezzi(minuti, secondi, centesimi) -> tuple[int | None, str | None]:
    """
    Le tre caselle mm / ss / cc -> centesimi interi. Ritorna (valore, errore).

    E' la strada che usa la pagina: tre campi numerici separati si compilano
    meglio di uno di testo, soprattutto sul telefono, dove la tastiera che si
    apre e' quella dei numeri e non si puo' scrivere niente di storto.

    Tutto a zero vale come "non ha ancora scritto", non come errore: e' lo
    stato in cui la pagina si apre.
    """
    def _n(v) -> int | None:
        if v is None:
            return None
        try:
            return int(v)
        except (TypeError, ValueError):
            return None

    mm, ss, cc = _n(minuti), _n(secondi), _n(centesimi)
    if None in (mm, ss, cc):
        return None, "Minuti, secondi e centesimi devono essere numeri interi."
    if not (0 <= mm <= 59):
        return None, "I minuti vanno da 0 a 59."
    if not (0 <= ss <= 59):
        return None, "I secondi vanno da 0 a 59."
    if not (0 <= cc <= 99):
        return None, "I centesimi vanno da 0 a 99."
    totale = mm * 6_000 + ss * 100 + cc
    if totale == 0:
        return None, None
    return totale, None


def pezzi_da_cent(cent: int | None) -> tuple[int, int, int]:
    """Centesimi interi -> (minuti, secondi, centesimi), per riempire le tre
    caselle con un tempo che si ha gia' (il personale, per dirne uno)."""
    if cent is None or int(cent) <= 0:
        return 0, 0, 0
    resto = int(cent) % 360_000          # oltre l'ora le caselle non arrivano
    minuti, resto = divmod(resto, 6_000)
    secondi, centesimi = divmod(resto, 100)
    return minuti, secondi, centesimi


def testo_da_cent(cent: int | None) -> str:
    """Centesimi interi -> il tempo come si scrive: 58.62, 1:58.26, 1:02:03.45."""
    if cent is None:
        return "—"
    cent = int(cent)
    segno = "-" if cent < 0 else ""
    cent = abs(cent)
    ore, resto = divmod(cent, 360_000)
    minuti, resto = divmod(resto, 6_000)
    secondi, centesimi = divmod(resto, 100)
    if ore:
        return f"{segno}{ore}:{minuti:02d}:{secondi:02d}.{centesimi:02d}"
    if minuti:
        return f"{segno}{minuti}:{secondi:02d}.{centesimi:02d}"
    return f"{segno}{secondi}.{centesimi:02d}"


def secondi_da_cent(cent: int | None) -> float | None:
    """Per i confronti con i tempi a database, che sono in secondi."""
    return None if cent is None else int(cent) / 100.0


def cent_da_secondi(secondi) -> int | None:
    """Secondi del database -> centesimi interi, che e' la vera precisione."""
    if secondi is None or pd.isna(secondi):
        return None
    return int(round(float(secondi) * 100))


# ══════════════════════════════════════════════════════════════════
# Punteggi: testo <-> centesimi di punto
# ══════════════════════════════════════════════════════════════════
# Anche i punti girano su interi, in centesimi di punto: 1012.34 e' 101234.
# Stesso motivo dei tempi, e cosi' il troncamento richiesto dal regolamento
# e' una divisione intera e non un arrotondamento mascherato.

PUNTI_MIN_CENT = 1              # 0.01 punti
PUNTI_MAX_CENT = 500_000        # 5000 punti, molto oltre il possibile
# Oltre questa soglia il punteggio non e' impossibile, ma e' quasi sempre un
# tempo digitato male: la pagina lo segnala senza bloccare.
PUNTI_SOSPETTI = 1300

_PUNTI_RE = re.compile(r"^(\d{1,5})(?:[.,](\d{1,2}))?$")


def punti_da_testo(testo: str | None) -> tuple[Decimal | None, str | None]:
    """Punteggio scritto a mano -> Decimal a due decimali. (valore, errore)."""
    testo = (testo or "").strip()
    if not testo:
        return None, None
    m = _PUNTI_RE.match(testo)
    if not m:
        return None, (f'Punteggio non valido: "{testo}". Si scrive 900 '
                      "oppure 1012.34.")
    interi, dec = m.groups()
    cent = int(interi) * 100 + int((dec or "0").ljust(2, "0"))
    if cent < PUNTI_MIN_CENT:
        return None, "Un punteggio di zero non esiste."
    if cent > PUNTI_MAX_CENT:
        return None, f'Punteggio fuori scala: "{testo}".'
    return Decimal(cent).scaleb(-2), None


def testo_da_punti(punti: Decimal | None) -> str:
    """1012.3 -> '1012.34' con i due decimali sempre scritti."""
    if punti is None:
        return "—"
    return f"{Decimal(punti).quantize(Decimal('0.01')):f}"


def _punti_in_cent(punti) -> int:
    """Decimal dei punti -> centesimi di punto interi, troncando."""
    return int((Decimal(str(punti)) * 100).to_integral_value(rounding=ROUND_DOWN))


# ══════════════════════════════════════════════════════════════════
# Le due operazioni
# ══════════════════════════════════════════════════════════════════

def punti(cent_base: int, cent_reale: int) -> Decimal:
    """
    P = (TB / TR) x 1000, troncato al centesimo di punto.

    Tutto in interi: TB e TR sono centesimi di secondo, il risultato e' in
    centesimi di punto, e la divisione intera e' esattamente il troncamento
    chiesto dal regolamento. Nessun arrotondamento, nessun float di mezzo.

        TB = 5862 (58.62), TR = 6012 (1:00.12)
        5862 * 100000 // 6012 = 97504  ->  975.04 punti
    """
    tb, tr = int(cent_base), int(cent_reale)
    if tb <= 0:
        raise ValueError("Il tempo base deve essere positivo.")
    if tr <= 0:
        raise ValueError("Il tempo realizzato deve essere positivo.")
    # 1000 punti di scala x 100 centesimi di punto = 100_000
    return Decimal(tb * 100_000 // tr).scaleb(-2)


def tempo_per_punti(cent_base: int, punti_obiettivo) -> int:
    """
    TR = (TB x 1000) / P, al centesimo.

    Il centesimo che torna e' il tempo **piu' lento** che vale ancora almeno
    quel punteggio: siccome i punti si troncano, il centesimo successivo
    scende sotto l'obiettivo. Cioe' punti(TB, risultato) >= P e
    punti(TB, risultato + 1) < P, sempre.

    E' la lettura utile per chi si allena: "fino a quanto posso arrivare e
    prendere comunque 900 punti".
    """
    tb = int(cent_base)
    if tb <= 0:
        raise ValueError("Il tempo base deve essere positivo.")
    p_cent = _punti_in_cent(punti_obiettivo)
    if p_cent <= 0:
        raise ValueError("Il punteggio deve essere positivo.")
    return tb * 100_000 // p_cent


# ══════════════════════════════════════════════════════════════════
# Categorie
# ══════════════════════════════════════════════════════════════════
# Attenzione a una collisione di nomi che fa danni se la si perde di vista:
# nella tabella FIN "M45" vuol dire **Master 45**, con il sesso in una
# colonna a parte, mentre altrove nell'app (season.master_category) "M45"
# vuol dire **maschio di 45 anni** e la femmina e' "F45". Qui dentro vale
# sempre il primo significato, e il sesso viaggia separato.

BANDA_MIN, BANDA_MAX = 20, 100


def categoria_da_banda(banda: int) -> str:
    """45 -> 'M45'. Fuori tabella si accosta all'estremo piu' vicino."""
    b = int(banda) // 5 * 5
    return f"M{max(BANDA_MIN, min(b, BANDA_MAX))}"


def banda_da_categoria(categoria: str) -> int:
    """'M45' -> 45."""
    return int(str(categoria).strip().upper().lstrip("M"))


def etichetta_categoria(categoria: str) -> str:
    """'M45' -> 'M45 · 45-49 anni'. L'ultima fascia e' aperta."""
    b = banda_da_categoria(categoria)
    if b >= BANDA_MAX:
        return f"M{b} · {b} anni e oltre"
    return f"M{b} · {b}-{b + 4} anni"


def banda_da_anno(anno_nascita: int | None, anno_riferimento: int | None = None) -> int | None:
    """
    Fascia quinquennale dall'anno di nascita. La FIN guarda l'eta' compiuta
    entro il 31/12 dell'anno in cui la stagione si chiude: nel 2027 un nato
    nel 1980 ha 47 anni e sta in M45.

    Resta qui e non in season.py perche' questo modulo non deve dipendere da
    nient'altro; chi ha gia' la stagione sotto mano usa season.master_band().
    """
    if anno_nascita is None:
        return None
    try:
        anno_nascita = int(anno_nascita)
    except (TypeError, ValueError):
        return None
    if anno_riferimento is None:
        oggi = _dt.date.today()
        # La stagione agonistica chiude il 31 agosto: da settembre si guarda
        # all'anno dopo.
        anno_riferimento = oggi.year + 1 if oggi.month >= 9 else oggi.year
    return (int(anno_riferimento) - anno_nascita) // 5 * 5


# ══════════════════════════════════════════════════════════════════
# Caricamento del foglio
# ══════════════════════════════════════════════════════════════════

def _firma(percorso: Path) -> tuple[float, int]:
    """Data e dimensione del file: se cambiano, la cache si rifa'."""
    st_ = percorso.stat()
    return (st_.st_mtime, st_.st_size)


def _leggi_foglio(percorso: Path, vasca: int) -> pd.DataFrame:
    nome = FOGLI[vasca]
    # TEMPO (mmsscc) va letto come testo: e' mm ss cc attaccati e nasce con
    # lo zero davanti ("002448"). Letta come numero diventa 2448 e perde lo
    # zero, e le tre righe a sette cifre (CENT=100, tipo "0113100") si
    # leggerebbero spostate di una posizione. La colonna serve solo al
    # controllo di anomalie(), ma un controllo che sbaglia e' peggio di
    # nessun controllo.
    try:
        df = pd.read_excel(percorso, sheet_name=nome, engine="openpyxl",
                           dtype={"TEMPO (mmsscc)": str})
    except ValueError as e:                              # foglio assente
        raise TempiBaseNonValidi(
            f"Nel file dei tempi base manca il foglio \"{nome}\".") from e
    mancanti = [c for c in COLONNE_RICHIESTE if c not in df.columns]
    if mancanti:
        raise TempiBaseNonValidi(
            f"Nel foglio \"{nome}\" mancano le colonne: "
            f"{', '.join(mancanti)}.")
    df = df[df["CATEG"].notna()].copy()
    df["vasca_foglio"] = vasca
    return df


def _normalizza(grezzo: pd.DataFrame) -> pd.DataFrame:
    """Dalle colonne del foglio alla tabella con cui lavora il calcolatore."""
    out = pd.DataFrame({
        "vasca": pd.to_numeric(grezzo["VASCA"], errors="coerce").astype("Int64"),
        "categoria": grezzo["CATEG"].astype(str).str.strip().str.upper(),
        "cod_gara": pd.to_numeric(grezzo["COD GARA"], errors="coerce").astype("Int64"),
        "gara": grezzo["GARA"].astype(str).str.strip(),
        "sesso": grezzo["SESSO"].astype(str).str.strip().str.upper().str[:1],
        "cent_base": pd.to_numeric(grezzo["CENT TOT"], errors="coerce").astype("Int64"),
        "vasca_foglio": grezzo["vasca_foglio"],
    })
    def _banda(c) -> int | None:
        try:
            return banda_da_categoria(c)
        except (TypeError, ValueError):
            return None

    out["banda"] = out["categoria"].map(_banda).astype("Int64")

    buchi = out[out[["vasca", "cod_gara", "cent_base", "banda"]].isna().any(axis=1)]
    if not buchi.empty:
        raise TempiBaseNonValidi(
            f"{len(buchi)} righe del file dei tempi base hanno valori "
            "illeggibili in VASCA, COD GARA, CENT TOT o CATEG.")

    fuori = out[(out["cent_base"] < CENT_MIN) | (out["cent_base"] > CENT_MAX)]
    if not fuori.empty:
        raise TempiBaseNonValidi(
            f"{len(fuori)} tempi base sono fuori scala (CENT TOT).")

    sballate = out[out["vasca"] != out["vasca_foglio"]]
    if not sballate.empty:
        raise TempiBaseNonValidi(
            f"{len(sballate)} righe stanno nel foglio di una vasca ma ne "
            "dichiarano un'altra nella colonna VASCA.")

    cattivo_sesso = out[~out["sesso"].isin(SESSI)]
    if not cattivo_sesso.empty:
        raise TempiBaseNonValidi(
            f"{len(cattivo_sesso)} righe hanno un valore di SESSO che non e' "
            "M o F.")

    out = out.drop(columns=["vasca_foglio"])
    out["vasca"] = out["vasca"].astype(int)
    out["cod_gara"] = out["cod_gara"].astype(int)
    out["cent_base"] = out["cent_base"].astype(int)
    out["banda"] = out["banda"].astype(int)

    chiave = ["vasca", "categoria", "cod_gara", "sesso"]
    doppi = out[out.duplicated(chiave, keep=False)]
    if not doppi.empty:
        esempi = ", ".join(
            f"{r.categoria}/{r.gara}/{r.sesso}/{r.vasca}m"
            for r in doppi.head(3).itertuples())
        raise TempiBaseNonValidi(
            f"{len(doppi)} righe del file dei tempi base sono doppie sulla "
            f"stessa combinazione ({esempi}).")

    return out.sort_values(["vasca", "banda", "cod_gara", "sesso"]).reset_index(drop=True)


def _trova_anomalie(grezzo: pd.DataFrame) -> pd.DataFrame:
    """
    Righe dove CENT TOT non va d'accordo con le altre scritture del tempo.

    Non si corregge niente: vale CENT TOT (vedi la nota in cima al modulo) e
    queste righe si mostrano cosi' come sono, perche' chi ha la tabella
    federale sotto mano possa controllarle. Sono otto su 1157.
    """
    def _da_colonna_testo(valore) -> int | None:
        """'015826' -> 11826. La colonna e' mm ss cc attaccati, sei cifre."""
        testo = str(valore).strip()
        if not testo.isdigit():
            return None
        testo = testo.zfill(6)
        if len(testo) != 6:
            return None             # le tre righe con CENT=100 fanno 7 cifre
        return (int(testo[0:2]) * 6_000 + int(testo[2:4]) * 100
                + int(testo[4:6]))

    def _da_pezzi(mm, ss, cc) -> int | None:
        """MIN/SEC/CENT -> centesimi. In vasca lunga CENT porta i decimi di
        centesimo (26.98 scritto "98.5"), quindi si arrotonda all'intero."""
        try:
            return (int(mm) * 6_000 + int(ss) * 100
                    + int(Decimal(str(cc)).to_integral_value(
                        rounding=ROUND_HALF_UP)))
        except (TypeError, ValueError, ArithmeticError):
            return None

    righe = []
    for riga in grezzo.to_dict("records"):
        cent_tot = int(riga["CENT TOT"])
        da_testo = _da_colonna_testo(riga["TEMPO (mmsscc)"])
        da_pezzi = _da_pezzi(riga["MIN"], riga["SEC"], riga["CENT"])
        if cent_tot == da_testo == da_pezzi:
            continue
        righe.append({
            "vasca": int(riga["VASCA"]),
            "categoria": str(riga["CATEG"]).strip().upper(),
            "gara": str(riga["GARA"]).strip(),
            "sesso": str(riga["SESSO"]).strip().upper()[:1],
            "cent_base": cent_tot,
            "usato": testo_da_cent(cent_tot),
            "colonna_tempo": (testo_da_cent(da_testo) if da_testo is not None
                              else str(riga["TEMPO (mmsscc)"]).strip()),
            "da_min_sec_cent": (testo_da_cent(da_pezzi) if da_pezzi is not None
                                else "—"),
        })
    colonne = ["vasca", "categoria", "gara", "sesso", "cent_base", "usato",
               "colonna_tempo", "da_min_sec_cent"]
    if not righe:
        return pd.DataFrame(columns=colonne)
    return pd.DataFrame(righe)[colonne]


@lru_cache(maxsize=4)
def _carica(percorso_txt: str, firma: tuple) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Legge e controlla il file. La firma sta nella chiave di cache perche'
    sostituire il file basti a far rileggere, senza riavviare l'app."""
    percorso = Path(percorso_txt)
    grezzi = [_leggi_foglio(percorso, v) for v in VASCHE]
    grezzo = pd.concat(grezzi, ignore_index=True)
    return _normalizza(grezzo), _trova_anomalie(grezzo)


def _coppia(percorso: Path | str | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    p = Path(percorso) if percorso else FILE_TEMPI_BASE
    if not p.exists():
        raise TempiBaseNonValidi(
            f"Il file dei tempi base non c'e': {p.name} dovrebbe stare in "
            f"{p.parent.name}/.")
    tabella_, anomalie_ = _carica(str(p), _firma(p))
    return tabella_.copy(), anomalie_.copy()


def tabella(percorso: Path | str | None = None) -> pd.DataFrame:
    """
    I tempi base, una riga per combinazione.

    Colonne: vasca, categoria, banda, cod_gara, gara, sesso, cent_base.
    """
    return _coppia(percorso)[0]


def anomalie(percorso: Path | str | None = None) -> pd.DataFrame:
    """Le righe del file che si contraddicono. Vedi _trova_anomalie()."""
    return _coppia(percorso)[1]


def svuota_cache() -> None:
    """Per i test, e per chi sostituisce il file a server acceso."""
    _carica.cache_clear()


# ══════════════════════════════════════════════════════════════════
# Interrogazioni
# ══════════════════════════════════════════════════════════════════

def gare(tb: pd.DataFrame, vasca: int | None = None) -> list[str]:
    """I nomi delle gare, nell'ordine della tabella federale (COD GARA).

    L'ordine non e' alfabetico di proposito: in vasca si ragiona per stile e
    per distanza, e COD GARA e' proprio quell'ordine (stile libero, dorso,
    rana, farfalla, misti). I 100 misti esistono solo in vasca corta.
    """
    df = tb if vasca is None else tb[tb["vasca"] == int(vasca)]
    return (df[["cod_gara", "gara"]].drop_duplicates()
            .sort_values("cod_gara")["gara"].tolist())


def categorie(tb: pd.DataFrame, vasca: int | None = None) -> list[str]:
    """Le categorie dalla piu' giovane alla piu' anziana."""
    df = tb if vasca is None else tb[tb["vasca"] == int(vasca)]
    return (df[["banda", "categoria"]].drop_duplicates()
            .sort_values("banda")["categoria"].tolist())


def tempo_base(tb: pd.DataFrame, gara: str, vasca: int, sesso: str,
               categoria: str) -> int | None:
    """
    Il tempo base in centesimi, o None se quella combinazione non c'e'.

    None non e' un errore da nascondere: la tabella federale ha dei buchi
    veri (M100 in quasi tutte le farfalle, qualche 400 misti in M95) e
    riempirli per non lasciare la casella vuota vorrebbe dire inventare un
    punteggio. Chi chiama deve dirlo e fermarsi.
    """
    if tb.empty:
        return None
    righe = tb[(tb["gara"] == str(gara))
               & (tb["vasca"] == int(vasca))
               & (tb["sesso"] == str(sesso).upper()[:1])
               & (tb["categoria"] == str(categoria).strip().upper())]
    if righe.empty:
        return None
    return int(righe["cent_base"].iloc[0])


def combinazioni_mancanti(tb: pd.DataFrame) -> pd.DataFrame:
    """
    Le caselle vuote della tabella: gara x categoria x sesso, per vasca.

    Serve al pannello di controllo della pagina, per dire quante e quali
    sono invece di farle scoprire una alla volta.
    """
    righe = []
    for vasca in sorted(tb["vasca"].unique()):
        fetta = tb[tb["vasca"] == vasca]
        presenti = set(zip(fetta["categoria"], fetta["gara"], fetta["sesso"]))
        for categoria in categorie(tb, vasca):
            for nome in gare(tb, vasca):
                for sesso in SESSI:
                    if (categoria, nome, sesso) not in presenti:
                        righe.append({"vasca": int(vasca),
                                      "categoria": categoria,
                                      "gara": nome,
                                      "sesso": sesso})
    colonne = ["vasca", "categoria", "gara", "sesso"]
    if not righe:
        return pd.DataFrame(columns=colonne)
    return pd.DataFrame(righe)[colonne]


# ══════════════════════════════════════════════════════════════════
# Il risultato, pronto da mostrare
# ══════════════════════════════════════════════════════════════════

def esito_punti(tb: pd.DataFrame, gara: str, vasca: int, sesso: str,
                categoria: str, cent_reale: int | None) -> dict:
    """
    Dal tempo in centesimi al punteggio, con tutto quello che serve a
    spiegarlo in pagina: il tempo base usato, lo scarto, e l'errore se la
    combinazione non esiste.

    Torna sempre un dizionario con la stessa forma, cosi' la pagina non ha
    da ricostruire niente: {errore, cent_base, cent_reale, punti, scarto}.

    E' il cuore: la pagina ci arriva dalle tre caselle mm/ss/cc passando da
    cent_da_pezzi(), e calcola_punti() ci arriva da un tempo scritto.
    """
    esito = {"errore": None, "cent_base": None, "cent_reale": None,
             "punti": None, "scarto": None}
    if cent_reale is None:
        return esito
    if int(cent_reale) <= 0:
        esito["errore"] = "Un tempo di zero non esiste."
        return esito
    esito["cent_reale"] = int(cent_reale)

    tb_cent = tempo_base(tb, gara, vasca, sesso, categoria)
    if tb_cent is None:
        esito["errore"] = messaggio_senza_tempo_base(gara, vasca, sesso,
                                                     categoria)
        return esito
    esito["cent_base"] = tb_cent
    esito["punti"] = punti(tb_cent, int(cent_reale))
    # Positivo = piu' veloce del tempo base.
    esito["scarto"] = tb_cent - int(cent_reale)
    return esito


def calcola_punti(tb: pd.DataFrame, gara: str, vasca: int, sesso: str,
                  categoria: str, tempo: str) -> dict:
    """Come esito_punti(), ma partendo da un tempo scritto come testo."""
    cent_reale, err = cent_da_testo(tempo)
    if err:
        return {"errore": err, "cent_base": None, "cent_reale": None,
                "punti": None, "scarto": None}
    return esito_punti(tb, gara, vasca, sesso, categoria, cent_reale)


def esito_tempo(tb: pd.DataFrame, gara: str, vasca: int, sesso: str,
                categoria: str, punteggio) -> dict:
    """
    Dal punteggio al tempo da nuotare.

    `punti_resi` e' il punteggio che quel tempo vale davvero: siccome il
    tempo si ferma al centesimo, quasi sempre e' un filo sopra l'obiettivo,
    e dirlo in pagina evita la domanda "ma allora non sono 900 esatti?".
    """
    esito = {"errore": None, "cent_base": None, "punti": None,
             "cent_reale": None, "punti_resi": None, "scarto": None}
    if punteggio is None:
        return esito
    if _punti_in_cent(punteggio) <= 0:
        esito["errore"] = "Un punteggio di zero non esiste."
        return esito
    esito["punti"] = Decimal(str(punteggio))

    tb_cent = tempo_base(tb, gara, vasca, sesso, categoria)
    if tb_cent is None:
        esito["errore"] = messaggio_senza_tempo_base(gara, vasca, sesso,
                                                     categoria)
        return esito
    esito["cent_base"] = tb_cent
    cent = tempo_per_punti(tb_cent, punteggio)
    if cent <= 0:
        esito["errore"] = ("Con quel punteggio il tempo richiesto e' sotto il "
                           "centesimo di secondo: controlla il valore.")
        return esito
    esito["cent_reale"] = cent
    esito["punti_resi"] = punti(tb_cent, cent)
    esito["scarto"] = tb_cent - cent
    return esito


def calcola_tempo(tb: pd.DataFrame, gara: str, vasca: int, sesso: str,
                  categoria: str, punteggio: str) -> dict:
    """Come esito_tempo(), ma partendo da un punteggio scritto come testo."""
    p, err = punti_da_testo(punteggio)
    if err:
        return {"errore": err, "cent_base": None, "punti": None,
                "cent_reale": None, "punti_resi": None, "scarto": None}
    return esito_tempo(tb, gara, vasca, sesso, categoria, p)


def messaggio_senza_tempo_base(gara: str, vasca: int, sesso: str,
                               categoria: str) -> str:
    """Perche' quella combinazione non si calcola, detto per intero: la
    tabella federale ha dei buchi veri e la pagina deve dire quale."""
    return (f"La tabella FIN {STAGIONE_TABELLA} non ha il tempo base per "
            f"{gara} · {ETICHETTE_SESSO.get(sesso, sesso)} · "
            f"{categoria} · vasca da {vasca} metri, quindi il punteggio non "
            "si puo' calcolare.")
