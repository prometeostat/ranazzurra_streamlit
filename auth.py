"""
auth.py — accesso riservato ai tesserati.

Quattro modalita', scelte da .streamlit/secrets.toml con [app] auth_mode:

  "password" (default) e-mail dell'anagrafica come nome utente e password
                       scelta dall'atleta, con l'hash su athlete_credentials.
                       Nessun provider esterno, nessuna mail da spedire: al
                       primo accesso ci si riconosce con e-mail e data di
                       nascita, che sono gia' a database per tutti.
  "code"               vecchio accesso con codice FIN e data di nascita.
                       Resta per compatibilita', ma sette tesserati attivi
                       il codice FIN non ce l'hanno.
  "oidc"               st.login() di Streamlit con un provider OpenID
                       Connect, l'utente si riconosce dall'e-mail.
  "open"               nessun login, solo per sviluppo: l'ospite e'
                       amministratore per definizione.

Le password non si possono rileggere, nemmeno dall'amministratore: si
azzerano, e l'atleta ne sceglie una nuova. Chi amministra puo' anche
generare una temporanea, che al primo ingresso va sostituita.

Ruoli: admin e allenatore vedono tutti gli atleti, l'atleta apre la propria
scheda ma puo' comunque consultare classifiche e confronti di squadra.
"""
from __future__ import annotations

import base64
import datetime as _dt
import hashlib
import hmac
import os
import secrets as _rnd
import time
from pathlib import Path

import streamlit as st

from db import execute, query_df
from queries import (ACCESS_LOG_INSERT_SQL, ATHLETE_BY_EMAIL_BIRTH_SQL,
                     AUTH_BY_EMAIL_SQL, AUTH_BY_FIN_SQL,
                     CREDENTIALS_DELETE_SQL, CREDENTIALS_ENABLE_SQL,
                     CREDENTIALS_FAIL_SQL, CREDENTIALS_OK_SQL,
                     CREDENTIALS_STATE_SQL, CREDENTIALS_UPSERT_SQL,
                     LOGIN_BY_EMAIL_SQL)

SESSION_KEY = "auth_user"
TOKEN_PARAM = "t"
TOKEN_TTL_DAYS = 30

# Password: scrypt della libreria standard, niente dipendenze in piu'.
# n=16384, r=8, p=1 sono i parametri consigliati per un login interattivo,
# circa 16 MB di memoria e qualche decina di millisecondi a verifica.
SCRYPT_N, SCRYPT_R, SCRYPT_P = 2 ** 14, 8, 1
SCRYPT_MAXMEM = 64 * 1024 * 1024
MIN_PASSWORD = 8
MAX_TENTATIVI = 5          # dopo quanti errori scatta il blocco
BLOCCO_MINUTI = 15         # e per quanto dura


# ══════════════════════════════════════════════════════════════════
# Configurazione
# ══════════════════════════════════════════════════════════════════

def _app_cfg() -> dict:
    try:
        return dict(st.secrets["app"])
    except Exception:
        return {}


def _mode() -> str:
    """
    "password" (default) e-mail dell'anagrafica piu' password scelta
                         dall'atleta, verificata su athlete_credentials
    "code"               vecchio accesso con codice FIN e data di nascita
    "oidc"               st.login() con un provider esterno
    "open"               nessun login, solo per sviluppo
    """
    return str(_app_cfg().get("auth_mode", "password")).lower()


def _secret_key() -> bytes:
    cfg = _app_cfg()
    raw = cfg.get("token_secret") or cfg.get("cookie_secret") or "master-conegliano-dev-key"
    return str(raw).encode()


def _ints(cfg: dict, key: str) -> set[int]:
    """Legge una lista di interi dai secrets, tollerando numeri fra virgolette."""
    out = set()
    for x in cfg.get(key, []) or []:
        try:
            out.add(int(str(x).strip()))
        except (TypeError, ValueError):
            continue
    return out


def _role_for(athlete_id: int | None, fin_code, email: str | None,
              staff: bool = False) -> str:
    """
    Ruolo dell'utente, deciso dai secrets. Tre chiavi possibili per ciascun
    ruolo, si puo' usare quella che torna piu' comoda:

        admin_athlete_ids = [52]        athletes.id, la piu' stabile
        admin_fin_codes   = [281728]    codice FIN
        admin_emails      = ["..."]     solo con auth_mode = "oidc",
                                        perche' in modalita' "code" l'email
                                        non viene mai chiesta

    Stesse chiavi con prefisso coach_ per gli allenatori. In piu', chi in
    anagrafica ha is_staff = TRUE e' allenatore senza bisogno dei secrets:
    quel flag lo mette l'amministratore dall'Anagrafica atleti.
    """
    cfg = _app_cfg()
    mail = (email or "").lower()

    admins_mail = {str(x).lower() for x in cfg.get("admin_emails", []) or []}
    coaches_mail = {str(x).lower() for x in cfg.get("coach_emails", []) or []}

    aid = int(athlete_id) if athlete_id is not None else None
    fin = int(fin_code) if fin_code is not None else None

    if (aid in _ints(cfg, "admin_athlete_ids")
            or (fin is not None and fin in _ints(cfg, "admin_fin_codes"))
            or (mail and mail in admins_mail)):
        return "admin"

    if (aid in _ints(cfg, "coach_athlete_ids")
            or (fin is not None and fin in _ints(cfg, "coach_fin_codes"))
            or (mail and mail in coaches_mail)
            or bool(staff)):
        return "allenatore"

    return "atleta"


# ══════════════════════════════════════════════════════════════════
# Registro accessi su file
# ══════════════════════════════════════════════════════════════════

def _file_log() -> Path | None:
    """
    Percorso del file di log, da [app] access_log_file nei secrets. Se non
    c'e' non si registra niente. Su Windows conviene scriverlo con le barre
    normali: "G:/Il mio Drive/Job/ranazzurra/accessi.txt".
    """
    raw = str(_app_cfg().get("access_log_file", "") or "").strip()
    return Path(raw) if raw else None


def _db_user_id() -> int:
    """Utente tecnico per i campi di audit, come in crud.py."""
    try:
        return int(_app_cfg().get("db_user_id", 1))
    except (TypeError, ValueError):
        return 1


def registra_accesso(esito: str, **dati) -> None:
    """
    Registra un evento di accesso: prima a database nella tabella
    access_log, che e' il registro vero e vive ovunque giri l'app, poi
    anche su file se nei secrets c'e' access_log_file.

    Non solleva mai: un log che non si scrive non deve impedire a nessuno
    di entrare.
    """
    try:
        execute(ACCESS_LOG_INSERT_SQL, (
            _db_user_id(),
            str(esito)[:20],
            int(dati["id"]) if str(dati.get("id", "")).strip().isdigit() else None,
            (str(dati["nome"])[:200] if dati.get("nome") else None),
            int(dati["fin"]) if str(dati.get("fin", "")).strip().isdigit() else None,
            (str(dati["ruolo"])[:20] if dati.get("ruolo") else None),
            (str(dati["via"])[:20] if dati.get("via") else None),
            (str(dati["nota"])[:300] if dati.get("nota") else None)
            or _nota_residua(dati),
        ))
    except Exception:
        # Database irraggiungibile o tabella non ancora creata: pazienza.
        pass

    percorso = _file_log()
    if percorso is None:
        return
    campi = " | ".join(f"{k}={v}" for k, v in dati.items() if v not in (None, ""))
    riga = f"{_dt.datetime.now().isoformat(timespec='seconds')} | {esito} | {campi}\n"
    try:
        percorso.parent.mkdir(parents=True, exist_ok=True)
        with percorso.open("a", encoding="utf-8") as f:
            f.write(riga)
    except Exception:
        # Disco pieno, cartella non scrivibile, Drive scollegato: pazienza.
        pass


def _nota_residua(dati: dict) -> str | None:
    """Tutto quello che non ha una colonna sua finisce in note."""
    noti = {"id", "nome", "fin", "ruolo", "via", "nota"}
    resto = " | ".join(f"{k}={v}" for k, v in dati.items()
                       if k not in noti and v not in (None, ""))
    return resto[:300] or None


def ultimi_accessi(n: int = 50) -> list[str]:
    """Ultime righe del registro, dalla piu' recente. Vuoto se non c'e'."""
    percorso = _file_log()
    if percorso is None:
        return []
    try:
        righe = percorso.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    return [r for r in righe if r.strip()][-n:][::-1]


def log_attivo() -> str | None:
    """Percorso del registro, per mostrarlo in Gestione. None se spento."""
    percorso = _file_log()
    return str(percorso) if percorso else None


# ══════════════════════════════════════════════════════════════════
# Password degli atleti
# ══════════════════════════════════════════════════════════════════
# A database finisce solo l'hash scrypt, in un campo che si descrive da
# solo: "scrypt$n$r$p$salt$hash", tutto in base64. Nessuno, amministratore
# compreso, puo' rileggere la password di qualcun altro: si azzera e se ne
# fa una nuova.

def _b64(b: bytes) -> str:
    return base64.b64encode(b).decode()


def _unb64(t: str) -> bytes:
    return base64.b64decode(t.encode())


def cifra_password(password: str) -> str:
    """Hash di una password nuova, con sale casuale da 16 byte."""
    salt = os.urandom(16)
    dk = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=SCRYPT_N,
                        r=SCRYPT_R, p=SCRYPT_P, dklen=32, maxmem=SCRYPT_MAXMEM)
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${_b64(salt)}${_b64(dk)}"


def verifica_password(password: str, memorizzato: str | None) -> bool:
    """Confronto a tempo costante. Qualsiasi cosa storta vale 'no'."""
    if not password or not memorizzato:
        return False
    try:
        algo, n, r, p, salt, atteso = str(memorizzato).split("$")
        if algo != "scrypt":
            return False
        atteso_b = _unb64(atteso)
        dk = hashlib.scrypt(password.encode("utf-8"), salt=_unb64(salt),
                            n=int(n), r=int(r), p=int(p),
                            dklen=len(atteso_b), maxmem=SCRYPT_MAXMEM)
        return hmac.compare_digest(dk, atteso_b)
    except Exception:
        return False


BANALI = {"password", "12345678", "123456789", "qwertyui", "ranazzurra",
          "masterconegliano", "nuoto1234", "abcd1234"}


def valida_password(password: str, email: str | None = None) -> list[str]:
    """Regole minime, poche e chiare: serve una password usabile, non un rebus."""
    errori = []
    pwd = password or ""
    if len(pwd) < MIN_PASSWORD:
        errori.append(f"La password deve avere almeno {MIN_PASSWORD} caratteri.")
    if pwd.strip() != pwd:
        errori.append("Niente spazi all'inizio o alla fine.")
    if pwd.lower() in BANALI:
        errori.append("Questa password e' troppo comune, scegline un'altra.")
    if email and pwd.lower() == str(email).lower():
        errori.append("La password non puo' essere uguale all'indirizzo e-mail.")
    if pwd and pwd.isdigit():
        errori.append("Solo numeri e' troppo poco: aggiungi qualche lettera.")
    return errori


def password_casuale(lunghezza: int = 10) -> str:
    """Password temporanea leggibile: niente caratteri che si confondono."""
    alfabeto = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(_rnd.choice(alfabeto) for _ in range(lunghezza))


def _normalizza(email: str | None) -> str:
    return str(email or "").strip().lower()


# ── Scritture sulle credenziali ───────────────────────────────────

def imposta_password(athlete_id: int, password: str,
                     da_cambiare: bool = False) -> None:
    """Crea o sostituisce la password di un atleta."""
    uid = _db_user_id()
    execute(CREDENTIALS_UPSERT_SQL, (int(athlete_id), uid,
                                     cifra_password(password),
                                     bool(da_cambiare), uid))


def azzera_password(athlete_id: int) -> None:
    """
    Toglie la password: l'atleta torna come nuovo e puo' rifare il primo
    accesso con e-mail e data di nascita, scegliendone una sua.
    """
    execute(CREDENTIALS_DELETE_SQL, (int(athlete_id),))


def abilita_accesso(athlete_id: int, abilitato: bool) -> None:
    """Sospende o riattiva l'accesso senza toccare la password."""
    execute(CREDENTIALS_ENABLE_SQL, (bool(abilitato), _db_user_id(),
                                     int(athlete_id)))


def stato_credenziali(athlete_id: int) -> dict:
    """Stato per l'anagrafica: vuoto se l'atleta non ha ancora una password."""
    df = query_df(CREDENTIALS_STATE_SQL, (int(athlete_id),))
    return {} if df.empty else df.iloc[0].to_dict()


def cambia_password(athlete_id: int, vecchia: str, nuova: str,
                    email: str | None = None) -> list[str]:
    """
    Cambio password fatto dall'atleta. Restituisce la lista degli errori,
    vuota se e' andata.
    """
    attuale = query_df(
        "SELECT password_hash FROM athlete_credentials WHERE athlete_id = %s",
        (int(athlete_id),))
    if attuale.empty:
        return ["Non risulta nessuna password impostata per questo account."]
    if not verifica_password(vecchia, attuale.iloc[0]["password_hash"]):
        return ["La password attuale non e' corretta."]
    errori = valida_password(nuova, email)
    if nuova == vecchia:
        errori.append("La nuova password deve essere diversa da quella attuale.")
    if errori:
        return errori
    imposta_password(athlete_id, nuova, da_cambiare=False)
    registra_accesso("PASSWORD", id=athlete_id, nota="cambiata dall'atleta")
    return []


# ══════════════════════════════════════════════════════════════════
# Token "resta connesso" (firmato, nella query string)
# ══════════════════════════════════════════════════════════════════

def _sign(payload: str) -> str:
    return hmac.new(_secret_key(), payload.encode(), hashlib.sha256).hexdigest()[:32]


def _make_token(athlete_id: int) -> str:
    exp = int(time.time()) + TOKEN_TTL_DAYS * 86400
    payload = f"{athlete_id}.{exp}"
    raw = f"{payload}.{_sign(payload)}"
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def _read_token(token: str) -> int | None:
    try:
        pad = "=" * (-len(token) % 4)
        raw = base64.urlsafe_b64decode(token + pad).decode()
        athlete_id, exp, sig = raw.split(".")
        if not hmac.compare_digest(sig, _sign(f"{athlete_id}.{exp}")):
            return None
        if int(exp) < time.time():
            return None
        return int(athlete_id)
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════
# Lookup atleta
# ══════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600, show_spinner=False)
def _athlete_by_fin(fin_code: int, birth_date: _dt.date) -> dict | None:
    df = query_df(AUTH_BY_FIN_SQL, (fin_code, birth_date))
    if df.empty:
        return None
    return df.iloc[0].to_dict()


@st.cache_data(ttl=600, show_spinner=False)
def _athlete_by_email(email: str) -> dict | None:
    df = query_df(AUTH_BY_EMAIL_SQL, (email.strip().lower(),))
    if df.empty:
        return None
    return df.iloc[0].to_dict()


@st.cache_data(ttl=600, show_spinner=False)
def _athlete_by_id(athlete_id: int) -> dict | None:
    df = query_df(
        "SELECT a.id AS athlete_id, btrim(a.last_name)||' '||btrim(a.first_name) AS full_name, "
        "a.fin_code, a.is_staff FROM athletes a WHERE a.id = %s AND a.is_deleted = FALSE",
        (athlete_id,),
    )
    if df.empty:
        return None
    return df.iloc[0].to_dict()


def _login_user(rec: dict, email: str | None = None, remember: bool = False,
                via: str = "code") -> None:
    staff = bool(rec.get("is_staff") or False)
    user = {
        "athlete_id": int(rec["athlete_id"]),
        "full_name": rec["full_name"],
        "fin_code": rec.get("fin_code"),
        "email": email,
        "is_staff": staff,
        "role": _role_for(int(rec["athlete_id"]), rec.get("fin_code"), email,
                          staff),
    }
    st.session_state[SESSION_KEY] = user
    if remember:
        st.query_params[TOKEN_PARAM] = _make_token(user["athlete_id"])
    registra_accesso("ACCESSO", id=user["athlete_id"], nome=user["full_name"],
                     fin=user["fin_code"], ruolo=user["role"], via=via)


# ══════════════════════════════════════════════════════════════════
# API pubblica
# ══════════════════════════════════════════════════════════════════

def current_user() -> dict | None:
    u = st.session_state.get(SESSION_KEY)
    if not u:
        return None
    # Il ruolo si rilegge dai secrets a ogni giro invece di restare congelato
    # al momento del login: se cambia la lista degli amministratori la nuova
    # regola vale subito, senza dover uscire e rientrare. In modalita' "open"
    # l'ospite e' amministratore per definizione e resta com'e'.
    if _mode() != "open":
        u["role"] = _role_for(u.get("athlete_id"), u.get("fin_code"),
                              u.get("email"), u.get("is_staff", False))
    return u


def diagnostica() -> dict:
    """
    Cosa vede l'app di chi e' collegato, per capire al volo perche' una
    sezione riservata non compare. Niente valori segreti: solo conteggi e
    si/no, si puo' mostrare in pagina senza pensieri.
    """
    cfg = _app_cfg()
    u = st.session_state.get(SESSION_KEY) or {}
    aid = u.get("athlete_id")
    fin = u.get("fin_code")
    return {
        "modalita": _mode(),
        "secrets_app": bool(cfg),
        "athlete_id": aid,
        "fin_code": fin,
        "ruolo": u.get("role"),
        "admin_configurati": (len(_ints(cfg, "admin_athlete_ids"))
                              + len(_ints(cfg, "admin_fin_codes"))
                              + len(cfg.get("admin_emails", []) or [])),
        "io_sono_admin_per_id": aid is not None and int(aid) in _ints(cfg, "admin_athlete_ids"),
        "io_sono_admin_per_fin": fin is not None and int(fin) in _ints(cfg, "admin_fin_codes"),
    }


def modalita() -> str:
    """Modalita' di accesso attiva, per le pagine che devono adattarsi."""
    return _mode()


def is_staff() -> bool:
    """Admin o allenatore."""
    u = current_user()
    return bool(u) and u["role"] in ("admin", "allenatore")


def is_admin() -> bool:
    """Solo amministratore: e' il permesso richiesto per scrivere in anagrafica."""
    u = current_user()
    return bool(u) and u["role"] == "admin"


def logout() -> None:
    u = st.session_state.get(SESSION_KEY) or {}
    registra_accesso("USCITA", id=u.get("athlete_id"), nome=u.get("full_name"))
    st.session_state.pop(SESSION_KEY, None)
    if TOKEN_PARAM in st.query_params:
        del st.query_params[TOKEN_PARAM]
    if _mode() == "oidc" and hasattr(st, "logout"):
        st.logout()
    st.rerun()


def require_login() -> dict:
    """
    Gate d'ingresso. Se l'utente non e' autenticato disegna la pagina di
    login e ferma l'esecuzione. Restituisce l'utente corrente.
    """
    mode = _mode()

    if mode == "open":
        user = st.session_state.setdefault(
            SESSION_KEY, {"athlete_id": None, "full_name": "Ospite",
                          "fin_code": None, "email": None, "role": "admin"},
        )
        return user

    if current_user():
        if st.session_state.get("pwd_da_cambiare"):
            _schermata_cambio(current_user())
            st.stop()
        return current_user()

    # Sessione ripristinata dal token in query string
    token = st.query_params.get(TOKEN_PARAM)
    if token:
        aid = _read_token(token)
        if aid:
            rec = _athlete_by_id(aid)
            if rec:
                _login_user(rec, via="token")
                return current_user()

    if mode == "oidc":
        _oidc_gate()
    elif mode == "code":
        _code_gate()
    else:
        _password_gate()

    st.stop()


# ══════════════════════════════════════════════════════════════════
# Schermate di login
# ══════════════════════════════════════════════════════════════════

def _login_header() -> None:
    st.markdown(
        """
        <div class="glass-card" style="max-width:460px;margin:8vh auto 20px;text-align:center;
             border-left:4px solid var(--teal);">
          <div style="font-family:'Bebas Neue',sans-serif;font-size:34px;letter-spacing:5px;
               color:var(--teal)">MASTER CONEGLIANO</div>
          <div style="font-family:'Barlow Condensed',sans-serif;font-size:12px;letter-spacing:2px;
               color:var(--muted);text-transform:uppercase">Area riservata ai tesserati</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _code_gate() -> None:
    _login_header()
    col = st.columns([1, 2, 1])[1]
    with col:
        with st.form("login_form"):
            fin = st.text_input("Codice FIN", placeholder="es. 418871",
                                help="Lo trovi sul tesserino o sulla scheda atleta di FIN Veneto.")
            birth = st.date_input(
                "Data di nascita",
                value=None, format="DD/MM/YYYY",
                min_value=_dt.date(1930, 1, 1), max_value=_dt.date.today(),
            )
            remember = st.checkbox("Resta connesso su questo dispositivo", value=True)
            ok = st.form_submit_button("Entra", use_container_width=True, type="primary")

        if ok:
            attempts = st.session_state.get("login_attempts", 0)
            if attempts >= 8:
                st.error("Troppi tentativi. Riprova fra qualche minuto.")
                return
            if not fin.strip().isdigit() or birth is None:
                st.warning("Servono il codice FIN (solo cifre) e la data di nascita.")
                return
            rec = _athlete_by_fin(int(fin.strip()), birth)
            if rec is None or rec.get("is_deleted"):
                st.session_state["login_attempts"] = attempts + 1
                registra_accesso("FALLITO", fin=fin.strip(),
                                 motivo="disattivato" if rec else "non trovato",
                                 tentativi=attempts + 1)
                st.error("Nessun tesserato con questi dati. Controlla codice e data.")
                return
            st.session_state["login_attempts"] = 0
            _login_user(rec, remember=remember)
            st.rerun()

        st.caption("Non riesci a entrare? Contatta l'amministratore e facciamo "
                   "controllare il codice FIN in anagrafica.")


def _ora(v) -> str:
    """Orario leggibile da un timestamp che puo' essere None o gia' stringa."""
    if v is None:
        return ""
    if hasattr(v, "strftime"):
        return v.strftime("%H:%M")
    return str(v)[11:16]


def _password_gate() -> None:
    """Accesso con l'e-mail dell'anagrafica e una password scelta dall'atleta."""
    _login_header()
    col = st.columns([1, 2, 1])[1]
    with col:
        t_entra, t_primo = st.tabs(["Entra", "Primo accesso"])

        with t_entra:
            with st.form("login_password"):
                email = st.text_input("E-mail", placeholder="nome@esempio.it",
                                      help="L'indirizzo che risulta in anagrafica.")
                pwd = st.text_input("Password", type="password")
                remember = st.checkbox("Resta connesso su questo dispositivo",
                                       value=True)
                ok = st.form_submit_button("Entra", use_container_width=True,
                                           type="primary")
            if ok:
                _tenta_accesso(email, pwd, remember)

        with t_primo:
            st.caption("La prima volta ti riconosci con l'indirizzo che hai "
                       "dato alla societa' e la tua data di nascita, poi "
                       "scegli la password che vuoi.")
            with st.form("primo_accesso"):
                email2 = st.text_input("E-mail", key="pa_email")
                nato = st.date_input("Data di nascita", value=None,
                                     format="DD/MM/YYYY",
                                     min_value=_dt.date(1930, 1, 1),
                                     max_value=_dt.date.today())
                p1 = st.text_input("Scegli una password", type="password",
                                   help=f"Almeno {MIN_PASSWORD} caratteri.")
                p2 = st.text_input("Ripeti la password", type="password")
                ok2 = st.form_submit_button("Attiva l'accesso",
                                            use_container_width=True,
                                            type="primary")
            if ok2:
                _attiva_accesso(email2, nato, p1, p2)

        st.caption("Password dimenticata, oppure e-mail non riconosciuta? "
                   "Contatta l'amministratore che azzererà la password e "
                   "potrai rifare il primo accesso.")


def _tenta_accesso(email: str, password: str, remember: bool) -> None:
    mail = _normalizza(email)
    if not mail or not password:
        st.warning("Servono l'e-mail e la password.")
        return

    tentativi = st.session_state.get("login_attempts", 0)
    if tentativi >= 10:
        st.error("Troppi tentativi da questa sessione. Riprova fra qualche minuto.")
        return

    df = query_df(LOGIN_BY_EMAIL_SQL, (mail,))
    if df.empty:
        st.session_state["login_attempts"] = tentativi + 1
        registra_accesso("FALLITO", nota=f"email sconosciuta: {mail[:120]}")
        # Messaggio unico: non si dice mai se e' l'indirizzo o la password.
        st.error("E-mail o password non corrette.")
        return

    r = df.iloc[0].to_dict()
    aid = int(r["athlete_id"])

    if r.get("password_hash") is None:
        st.warning("Questo indirizzo e' in anagrafica ma non ha ancora una "
                   "password: aprila dalla scheda **Primo accesso**.")
        return
    if not bool(r.get("is_enabled", True)):
        registra_accesso("FALLITO", id=aid, nome=r.get("full_name"),
                         nota="accesso sospeso")
        st.error("L'accesso di questo account e' sospeso. Contatta "
                 "l'amministratore.")
        return
    if bool(r.get("bloccato")):
        registra_accesso("FALLITO", id=aid, nome=r.get("full_name"),
                         nota="account bloccato")
        st.error(f"Troppi tentativi sbagliati: riprova dopo le "
                 f"{_ora(r.get('bloccato_fino'))}.")
        return

    if not verifica_password(password, r["password_hash"]):
        st.session_state["login_attempts"] = tentativi + 1
        esito = execute(CREDENTIALS_FAIL_SQL,
                        (MAX_TENTATIVI, BLOCCO_MINUTI, aid), returning=True) or {}
        fatti = int(esito.get("failed_attempts") or 0)
        rimasti = max(0, MAX_TENTATIVI - fatti)
        registra_accesso("FALLITO", id=aid, nome=r.get("full_name"),
                         nota=f"password errata | tentativi={fatti}")
        if rimasti:
            st.error(f"E-mail o password non corrette. Ancora {rimasti} "
                     f"tentativ{'o' if rimasti == 1 else 'i'} prima del blocco.")
        else:
            st.error(f"Troppi tentativi: accesso bloccato per {BLOCCO_MINUTI} "
                     "minuti.")
        return

    execute(CREDENTIALS_OK_SQL, (aid,))
    st.session_state["login_attempts"] = 0
    _login_user(r, email=r.get("email"), remember=remember, via="password")
    if bool(r.get("must_change")):
        st.session_state["pwd_da_cambiare"] = True
    st.rerun()


def _attiva_accesso(email: str, nato, p1: str, p2: str) -> None:
    mail = _normalizza(email)
    if not mail or nato is None:
        st.warning("Servono l'e-mail e la data di nascita.")
        return
    if p1 != p2:
        st.error("Le due password non coincidono.")
        return
    errori = valida_password(p1, mail)
    if errori:
        for e in errori:
            st.error(e)
        return

    df = query_df(ATHLETE_BY_EMAIL_BIRTH_SQL, (mail, nato))
    if df.empty:
        registra_accesso("FALLITO", nota=f"attivazione fallita: {mail[:120]}")
        st.error("Questi dati non corrispondono a nessun tesserato. Controlla "
                 "l'indirizzo e la data, oppure chiedi all'amministratore di "
                 "sistemare l'anagrafica.")
        return

    r = df.iloc[0].to_dict()
    if bool(r.get("ha_password")):
        st.warning("Questo account ha gia' una password. Se non la ricordi, "
                   "chiedi all'amministratore di azzerarla.")
        return

    aid = int(r["athlete_id"])
    imposta_password(aid, p1, da_cambiare=False)
    registra_accesso("ATTIVAZIONE", id=aid, nome=r.get("full_name"),
                     nota="password scelta al primo accesso")
    _login_user(r, email=mail, remember=True, via="password")
    st.rerun()


def _schermata_cambio(user: dict) -> None:
    """Cambio obbligatorio: succede solo dopo una password temporanea."""
    _login_header()
    col = st.columns([1, 2, 1])[1]
    with col:
        st.info("La password che hai usato e' temporanea. Scegline una tua "
                "per continuare.")
        with st.form("cambio_obbligatorio"):
            vecchia = st.text_input("Password temporanea", type="password")
            n1 = st.text_input("Nuova password", type="password")
            n2 = st.text_input("Ripeti la nuova password", type="password")
            ok = st.form_submit_button("Salva e continua", type="primary",
                                       use_container_width=True)
        if ok:
            if n1 != n2:
                st.error("Le due password non coincidono.")
                return
            errori = cambia_password(int(user["athlete_id"]), vecchia, n1,
                                     user.get("email"))
            if errori:
                for e in errori:
                    st.error(e)
                return
            st.session_state["pwd_da_cambiare"] = False
            st.rerun()


def _oidc_gate() -> None:
    _login_header()
    col = st.columns([1, 2, 1])[1]
    with col:
        if not hasattr(st, "login"):
            st.error("Questa versione di Streamlit non supporta il login OIDC. "
                     "Passa ad auth_mode = \"code\" nei secrets.")
            return

        user = getattr(st, "user", None)
        if user is not None and getattr(user, "is_logged_in", False):
            email = (getattr(user, "email", "") or "").lower()
            rec = _athlete_by_email(email)
            if rec is None:
                st.error(f"L'indirizzo {email} non risulta in anagrafica atleti. "
                         "Chiedi all'amministratore di associarlo al tuo "
                         "tesseramento.")
                if st.button("Esci"):
                    st.logout()
                return
            _login_user(rec, email=email, via="oidc")
            st.rerun()
        else:
            st.button("Accedi con il tuo account", use_container_width=True,
                      type="primary", on_click=st.login)


def sidebar_account() -> None:
    """Blocchetto account in fondo alla sidebar."""
    user = current_user()
    if not user:
        return
    role_label = {"admin": "Amministratore", "allenatore": "Allenatore"}.get(
        user["role"], "Atleta")
    st.markdown(
        f"""<div style="font-family:'Barlow Condensed',sans-serif;font-size:12px;
             color:var(--muted);letter-spacing:1px;margin-top:8px">
             {user['full_name']}<br>
             <span style="color:var(--teal)">{role_label}</span></div>""",
        unsafe_allow_html=True,
    )
    if st.button("Esci", use_container_width=True):
        logout()
