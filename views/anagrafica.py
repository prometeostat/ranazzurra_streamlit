"""
views/anagrafica.py — Anagrafica atleti: elenco, nuovo, modifica, disattiva.

"Elimina" non cancella niente: mette is_deleted = TRUE, che nell'interfaccia
si legge come Attivo = No. Cosi' restano gare, risultati e storico attaccati
all'atleta. Chi e' gia' inattivo non si puo' eliminare di nuovo: gli si
propone Riattiva.
"""
from __future__ import annotations

import datetime as _dt

import pandas as pd
import streamlit as st

import auth
import crud
from views._common import page_header

STATI = ["Attivi", "Inattivi", "Tutti"]
RUOLI = ["Tutti", "Atleti", "Allenatori e staff"]
ORDINAMENTI = {
    "Cognome": "last_name",
    "Nome": "first_name",
    "Codice FIN": "fin_code",
    "E-Mail": "email",
}

page_header("Anagrafica atleti", "Gestione tesserati")

if not auth.is_admin():
    st.info("L'anagrafica e' riservata all'amministratore. "
            "I tempi restano visibili a tutti dalle altre pagine.")
    st.stop()

st.session_state.setdefault("anag_mode", "lista")   # lista | nuovo | modifica
st.session_state.setdefault("anag_id", None)
st.session_state.setdefault("anag_conferma", None)


def _torna_alla_lista() -> None:
    st.session_state["anag_mode"] = "lista"
    st.session_state["anag_id"] = None
    st.session_state["anag_conferma"] = None


def _data(v):
    """Normalizza a datetime.date: psycopg da' date, pandas a volte Timestamp."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, pd.Timestamp):
        return None if pd.isna(v) else v.date()
    return v


def _societa_predefinita(df: pd.DataFrame):
    """La societa' piu' usata in anagrafica: il default per i nuovi atleti."""
    if df.empty or "company_id" not in df.columns:
        return None
    valori = df["company_id"].dropna()
    return int(valori.mode().iloc[0]) if not valori.empty else None


# ══════════════════════════════════════════════════════════════════
# Form di inserimento e modifica
# ══════════════════════════════════════════════════════════════════

def _form(atleta: dict | None) -> None:
    nuovo = atleta is None
    titolo = "Nuovo atleta" if nuovo else f"Modifica · {atleta['last_name']} {atleta['first_name']}"
    st.markdown(f'<div class="section-title">{titolo}</div>', unsafe_allow_html=True)

    if not nuovo:
        st.caption(f"ID {int(atleta['athlete_id'])} · assegnato dal database, "
                   "non modificabile.")

    with st.form("form_atleta", clear_on_submit=False):
        c1, c2 = st.columns(2)
        cognome = c1.text_input("Cognome *", value="" if nuovo else (atleta["last_name"] or ""),
                                max_chars=crud.MAX_NOME)
        nome = c2.text_input("Nome *", value="" if nuovo else (atleta["first_name"] or ""),
                             max_chars=crud.MAX_NOME)

        c3, c4 = st.columns(2)
        fin_attuale = "" if nuovo or pd.isna(atleta.get("fin_code")) \
            else str(int(atleta["fin_code"]))
        fin = c3.text_input("Codice FIN", value=fin_attuale, max_chars=10,
                            help="Solo cifre. Serve anche per il login dell'atleta.")
        sesso_attuale = "Maschile" if nuovo or atleta.get("sex") else "Femminile"
        sesso = c4.radio("Sesso *", ["Maschile", "Femminile"], horizontal=True,
                         index=0 if sesso_attuale == "Maschile" else 1)

        c5, c6 = st.columns(2)
        nascita = c5.date_input(
            "Data di nascita",
            value=None if nuovo else _data(atleta.get("birth_date")),
            format="DD/MM/YYYY",
            min_value=_dt.date(1920, 1, 1), max_value=_dt.date.today(),
            help="Serve per la categoria master e per il login.",
        )
        email = c6.text_input("E-Mail", value="" if nuovo else (atleta.get("email") or ""),
                              max_chars=crud.MAX_NOME)

        c7, c8 = st.columns(2)
        e_atleta = c7.checkbox(
            "Atleta", value=True if nuovo else bool(atleta.get("is_athlete", True)),
            help="Gareggia per la squadra: compare nei selettori, nelle "
                 "classifiche e nei conteggi.")
        e_staff = c8.checkbox(
            "Allenatore o staff", value=False if nuovo else bool(atleta.get("is_staff", False)),
            help="Puo' entrare nell'app con la sua e-mail. Chi allena e basta "
                 "resta fuori dagli elenchi atleti; chi fa tutti e due i ruoli "
                 "compare come tutti gli altri.")

        st.checkbox("Attivo", value=True if nuovo else (not atleta["is_deleted"]),
                    disabled=True,
                    help="Si cambia con i pulsanti Disattiva e Riattiva nell'elenco.")

        b1, b2 = st.columns([1, 1])
        salva = b1.form_submit_button("Salva", type="primary", use_container_width=True)
        annulla = b2.form_submit_button("Annulla", use_container_width=True)

    if annulla:
        _torna_alla_lista()
        st.rerun()

    if not salva:
        return

    if fin.strip() and not fin.strip().isdigit():
        st.error("Il codice FIN deve contenere solo cifre.")
        return

    dati = {
        "first_name": nome,
        "last_name": cognome,
        "fin_code": int(fin.strip()) if fin.strip() else None,
        "sex": sesso == "Maschile",
        "birth_date": nascita,
        "email": email,
        "is_athlete": bool(e_atleta),
        "is_staff": bool(e_staff),
    }
    errori = crud.valida(dati, -1 if nuovo else int(atleta["athlete_id"]))
    if errori:
        for e in errori:
            st.error(e)
        return

    if nuovo:
        dati["company_id"] = _societa_predefinita(crud.elenco_atleti())
        nuovo_id = crud.crea_atleta(dati)
        st.session_state["anag_msg"] = (
            f"Atleta creato con ID {nuovo_id}: {cognome} {nome}.")
    else:
        crud.aggiorna_atleta(int(atleta["athlete_id"]), dati)
        st.session_state["anag_msg"] = f"Anagrafica aggiornata: {cognome} {nome}."

    _torna_alla_lista()
    st.rerun()


# ══════════════════════════════════════════════════════════════════
# Elenco
# ══════════════════════════════════════════════════════════════════

atleti = crud.elenco_atleti()
if atleti.empty:
    st.warning("Nessun atleta in anagrafica.")
    st.stop()

_msg = st.session_state.pop("anag_msg", None)
if _msg:
    st.success(_msg)

modo = st.session_state["anag_mode"]
if modo == "nuovo":
    _form(None)
    st.stop()
if modo == "modifica":
    riga = atleti[atleti["athlete_id"] == st.session_state["anag_id"]]
    if riga.empty:
        _torna_alla_lista()
        st.rerun()
    _form(riga.iloc[0].to_dict())
    st.stop()

# ── Barra comandi ─────────────────────────────────────────────────
c_new, c_stato, c_cerca = st.columns([1.2, 2, 3], vertical_alignment="bottom")
if c_new.button("＋  Nuovo atleta", type="primary", use_container_width=True):
    st.session_state["anag_mode"] = "nuovo"
    st.rerun()
stato = c_stato.radio("Stato", STATI, horizontal=True, index=0, key="anag_stato")
cerca = c_cerca.text_input("Cerca", placeholder="Cognome, nome, codice FIN o e-mail…",
                           key="anag_cerca")

c_ord, c_verso = st.columns([2, 2])
ordina = c_ord.selectbox("Ordina per", list(ORDINAMENTI), key="anag_ordina")
verso = c_verso.radio("Verso", ["Crescente", "Decrescente"], horizontal=True,
                      key="anag_verso")
ruolo = st.radio("Ruolo", RUOLI, horizontal=True, key="anag_ruolo")

# ── Filtri ────────────────────────────────────────────────────────
vista = atleti.copy()
if stato == "Attivi":
    vista = vista[vista["is_deleted"] == False]      # noqa: E712
elif stato == "Inattivi":
    vista = vista[vista["is_deleted"] == True]       # noqa: E712

if ruolo == "Atleti":
    vista = vista[vista["is_athlete"].astype(bool)]
elif ruolo == "Allenatori e staff":
    vista = vista[vista["is_staff"].astype(bool)]

if cerca.strip():
    k = cerca.strip().lower()
    testo = (vista["last_name"].fillna("") + " " + vista["first_name"].fillna("")
             + " " + vista["email"].fillna("")
             + " " + vista["fin_code"].astype("Int64").astype(str)
                                      .replace("<NA>", "", regex=False))
    vista = vista[testo.str.lower().str.contains(k, na=False)]

vista = vista.sort_values(ORDINAMENTI[ordina], ascending=(verso == "Crescente"),
                          na_position="last")

_attivi = atleti[atleti["is_deleted"] == False]                       # noqa: E712
st.caption(
    f"{len(vista)} righe su {len(atleti)} in anagrafica · "
    f"{int(_attivi['is_athlete'].astype(bool).sum())} atleti attivi · "
    f"{int(_attivi['is_staff'].astype(bool).sum())} fra allenatori e staff.")

if vista.empty:
    st.info("Nessun atleta con questi filtri.")
    st.stop()

tabella = pd.DataFrame({
    "ID": vista["athlete_id"].astype(int),
    "Codice FIN": vista["fin_code"].astype("Int64"),
    "Cognome": vista["last_name"],
    "Nome": vista["first_name"],
    "Sesso": vista["sex"].map({True: "M", False: "F"}),
    "Data di nascita": vista["birth_date"],
    "E-Mail": vista["email"],
    "Ruolo": [("Atleta e allenatore" if a and s_ else
               "Allenatore" if s_ else "Atleta")
              for a, s_ in zip(vista["is_athlete"].astype(bool),
                               vista["is_staff"].astype(bool))],
    "Attivo": ~vista["is_deleted"].astype(bool),
    "Gare": vista["n_gare"].astype("Int64"),
})
st.dataframe(
    tabella, use_container_width=True, hide_index=True,
    column_config={
        "Attivo": st.column_config.CheckboxColumn("Attivo", disabled=True),
        "Data di nascita": st.column_config.DateColumn("Data di nascita",
                                                       format="DD/MM/YYYY"),
        "Codice FIN": st.column_config.NumberColumn("Codice FIN", format="%d"),
        "Gare": st.column_config.NumberColumn("Gare", help="Gare individuali a DB"),
    },
)

# ── Azioni sulla riga ─────────────────────────────────────────────
st.markdown('<div class="section-title">Azioni</div>', unsafe_allow_html=True)

ids = vista["athlete_id"].astype(int).tolist()
etichette = {
    int(r["athlete_id"]): (f'{r["last_name"]} {r["first_name"]}'
                           f'{"" if not r["is_deleted"] else "  ·  inattivo"}')
    for _, r in vista.iterrows()
}
c_sel, c_mod, c_del = st.columns([4, 1.2, 1.4], vertical_alignment="bottom")
scelto = c_sel.selectbox("Atleta", options=ids, key="anag_sel",
                         format_func=lambda i: etichette.get(i, str(i)))
riga = atleti[atleti["athlete_id"] == scelto].iloc[0]
inattivo = bool(riga["is_deleted"])

if c_mod.button("Modifica", use_container_width=True):
    st.session_state["anag_mode"] = "modifica"
    st.session_state["anag_id"] = int(scelto)
    st.rerun()

if inattivo:
    if c_del.button("Riattiva", use_container_width=True, type="primary"):
        crud.riattiva_atleta(int(scelto))
        st.session_state["anag_msg"] = (
            f"{riga['last_name']} {riga['first_name']} e' di nuovo attivo.")
        st.rerun()
else:
    if c_del.button("Elimina", use_container_width=True):
        st.session_state["anag_conferma"] = int(scelto)
        st.rerun()

# ══════════════════════════════════════════════════════════════════
# Credenziali dell'atleta selezionato
# ══════════════════════════════════════════════════════════════════
# La password non si puo' rileggere, nemmeno da qui: si azzera, e l'atleta
# rifa' il primo accesso con e-mail e data di nascita, oppure se ne genera
# una temporanea da consegnargli, che al primo ingresso deve cambiare.

def _quando(v) -> str:
    q = pd.to_datetime(v, errors="coerce")
    return "mai" if pd.isna(q) else q.strftime("%d/%m/%Y %H:%M")


st.markdown('<div class="section-title">Accesso all\'app</div>',
            unsafe_allow_html=True)

mail_atleta = str(riga.get("email") or "").strip()
stato = auth.stato_credenziali(int(scelto))

if inattivo:
    st.warning("Questa persona e' disattivata in anagrafica, quindi non puo' "
               "entrare ne' fare il primo accesso: il login cerca solo fra gli "
               "attivi. Se deve usare l'app, riattivala con il pulsante qui "
               "sopra.")
elif not mail_atleta:
    st.warning("Questo tesserato non ha un'e-mail in anagrafica, quindi non "
               "puo' entrare: l'indirizzo e' il nome utente. Aggiungilo con "
               "Modifica.")
elif riga.get("birth_date") is None or pd.isna(riga.get("birth_date")):
    st.warning("Manca la data di nascita: serve per il primo accesso, senza "
               "quella non riesce ad attivarsi.")
elif not stato:
    st.info(f"Nessuna password impostata. {riga['first_name']} puo' attivarsi "
            f"da solo dalla scheda **Primo accesso**, con {mail_atleta} e la "
            "sua data di nascita.")
else:
    sospeso = not bool(stato.get("is_enabled", True))
    bloccato = bool(stato.get("bloccato"))
    voci = [f"password impostata il {_quando(stato.get('creata_il'))}",
            f"ultimo accesso {_quando(stato.get('ultimo_accesso'))}"]
    if bool(stato.get("must_change")):
        voci.append("deve ancora cambiare la temporanea")
    if bloccato:
        voci.append(f"bloccato fino alle {_quando(stato.get('bloccato_fino'))}")
    if sospeso:
        voci.append("accesso sospeso")
    st.caption(f"{mail_atleta} · " + " · ".join(voci))

if mail_atleta:
    a1, a2, a3 = st.columns(3)

    if a1.button("Azzera password", use_container_width=True,
                 disabled=not stato,
                 help="Toglie la password: l'atleta rifa' il primo accesso e "
                      "ne sceglie una nuova."):
        auth.azzera_password(int(scelto))
        auth.registra_accesso("PASSWORD", id=int(scelto),
                              nome=f"{riga['last_name']} {riga['first_name']}",
                              nota="azzerata dall'amministratore")
        st.session_state["anag_msg"] = (
            f"Password azzerata: {riga['first_name']} puo' rifare il primo "
            "accesso con la sua e-mail e la data di nascita.")
        st.rerun()

    if a2.button("Password temporanea", use_container_width=True,
                 help="Ne genera una da consegnare a voce: al primo ingresso "
                      "l'app obbliga a cambiarla."):
        temporanea = auth.password_casuale()
        auth.imposta_password(int(scelto), temporanea, da_cambiare=True)
        auth.registra_accesso("PASSWORD", id=int(scelto),
                              nome=f"{riga['last_name']} {riga['first_name']}",
                              nota="temporanea generata dall'amministratore")
        st.session_state["anag_temporanea"] = temporanea
        st.rerun()

    etichetta = "Riattiva accesso" if (stato and not stato.get("is_enabled", True)) \
        else "Sospendi accesso"
    if a3.button(etichetta, use_container_width=True, disabled=not stato):
        nuovo = not bool(stato.get("is_enabled", True))
        auth.abilita_accesso(int(scelto), nuovo)
        auth.registra_accesso("PASSWORD", id=int(scelto),
                              nome=f"{riga['last_name']} {riga['first_name']}",
                              nota="accesso riattivato" if nuovo else "accesso sospeso")
        st.session_state["anag_msg"] = ("Accesso riattivato." if nuovo
                                        else "Accesso sospeso.")
        st.rerun()

_temp = st.session_state.pop("anag_temporanea", None)
if _temp:
    st.success("Password temporanea generata. Si vede una volta sola, "
               "copiala adesso e consegnala a voce o di persona.")
    st.code(_temp, language=None)
    st.caption("Al primo ingresso l'app chiede di sostituirla.")

# ── Conferma disattivazione ───────────────────────────────────────
if st.session_state.get("anag_conferma") is not None:
    aid = int(st.session_state["anag_conferma"])
    r = atleti[atleti["athlete_id"] == aid]
    if r.empty:
        st.session_state["anag_conferma"] = None
    else:
        r = r.iloc[0]
        gare = int(r["n_gare"]) if pd.notna(r["n_gare"]) else 0
        st.warning(
            f"Confermi l'eliminazione di **{r['last_name']} {r['first_name']}**?  \n"
            f"L'atleta viene messo a non attivo, non cancellato: le sue "
            f"{gare} gare a database restano al loro posto e lo puoi riattivare "
            "quando vuoi."
        )
        c_ok, c_no = st.columns([1, 1])
        if c_ok.button("Sì, elimina", type="primary", use_container_width=True):
            crud.disattiva_atleta(aid)
            st.session_state["anag_conferma"] = None
            st.session_state["anag_msg"] = (
                f"{r['last_name']} {r['first_name']} e' ora inattivo.")
            st.rerun()
        if c_no.button("Annulla", use_container_width=True):
            st.session_state["anag_conferma"] = None
            st.rerun()
