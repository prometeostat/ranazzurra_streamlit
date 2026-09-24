"""
auth.py — accesso riservato ai tesserati.

Tre modalita', scelte da .streamlit/secrets.toml con [app] auth_mode:

  "code"  (default) codice FIN + data di nascita, verificati su athletes.
                    Non serve nessun provider esterno e funziona anche per
                    chi non ha un account Google.
  "oidc"            st.login() di Streamlit (>= 1.42) con un provider
                    OpenID Connect; l'utente viene riconosciuto mappando
                    l'email su athletes.email.
  "open"            nessun login, come la vecchia app. Utile in sviluppo.

Ruoli: admin e allenatore vedono tutti gli atleti, l'atleta apre la propria
scheda ma puo' comunque consultare classifiche e confronti di squadra.
"""
from __future__ import annotations

import base64
import datetime as _dt
import hashlib
import hmac
import time

import streamlit as st

from db import query_df
from queries import AUTH_BY_FIN_SQL, AUTH_BY_EMAIL_SQL

SESSION_KEY = "auth_user"
TOKEN_PARAM = "t"
TOKEN_TTL_DAYS = 30


# ══════════════════════════════════════════════════════════════════
# Configurazione
# ══════════════════════════════════════════════════════════════════

def _app_cfg() -> dict:
    try:
        return dict(st.secrets["app"])
    except Exception:
        return {}


def _mode() -> str:
    return str(_app_cfg().get("auth_mode", "code")).lower()


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


def _role_for(athlete_id: int | None, fin_code, email: str | None) -> str:
    """
    Ruolo dell'utente, deciso dai secrets. Tre chiavi possibili per ciascun
    ruolo, si puo' usare quella che torna piu' comoda:

        admin_athlete_ids = [52]        athletes.id, la piu' stabile
        admin_fin_codes   = [281728]    codice FIN
        admin_emails      = ["..."]     solo con auth_mode = "oidc",
                                        perche' in modalita' "code" l'email
                                        non viene mai chiesta

    Stesse chiavi con prefisso coach_ per gli allenatori.
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
            or (mail and mail in coaches_mail)):
        return "allenatore"

    return "atleta"


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
        "a.fin_code FROM athletes a WHERE a.id = %s AND a.is_deleted = FALSE",
        (athlete_id,),
    )
    if df.empty:
        return None
    return df.iloc[0].to_dict()


def _login_user(rec: dict, email: str | None = None, remember: bool = False) -> None:
    user = {
        "athlete_id": int(rec["athlete_id"]),
        "full_name": rec["full_name"],
        "fin_code": rec.get("fin_code"),
        "email": email,
        "role": _role_for(int(rec["athlete_id"]), rec.get("fin_code"), email),
    }
    st.session_state[SESSION_KEY] = user
    if remember:
        st.query_params[TOKEN_PARAM] = _make_token(user["athlete_id"])


# ══════════════════════════════════════════════════════════════════
# API pubblica
# ══════════════════════════════════════════════════════════════════

def current_user() -> dict | None:
    return st.session_state.get(SESSION_KEY)


def is_staff() -> bool:
    """Admin o allenatore."""
    u = current_user()
    return bool(u) and u["role"] in ("admin", "allenatore")


def is_admin() -> bool:
    """Solo amministratore: e' il permesso richiesto per scrivere in anagrafica."""
    u = current_user()
    return bool(u) and u["role"] == "admin"


def logout() -> None:
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
        return current_user()

    # Sessione ripristinata dal token in query string
    token = st.query_params.get(TOKEN_PARAM)
    if token:
        aid = _read_token(token)
        if aid:
            rec = _athlete_by_id(aid)
            if rec:
                _login_user(rec)
                return current_user()

    if mode == "oidc":
        _oidc_gate()
    else:
        _code_gate()

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
                st.error("Nessun tesserato con questi dati. Controlla codice e data.")
                return
            st.session_state["login_attempts"] = 0
            _login_user(rec, remember=remember)
            st.rerun()

        st.caption("Non riesci a entrare? Scrivi in segreteria e facciamo controllare "
                   "il codice FIN in anagrafica.")


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
                         "Chiedi alla segreteria di associarlo al tuo tesseramento.")
                if st.button("Esci"):
                    st.logout()
                return
            _login_user(rec, email=email)
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
