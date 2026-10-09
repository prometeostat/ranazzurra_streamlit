# CLAUDE.md — Master Conegliano (ranazzurra_streamlit)

App Streamlit della squadra master Ranazzurra Conegliano: tempi, personali,
confronti, classifiche interne e anagrafiche, sul database PostgreSQL su Aiven.
Accesso riservato ai tesserati, installabile sulla home come PWA.
Il `README.md` e' la documentazione completa per funzionalita'; questo file
raccoglie solo quello che serve per lavorarci sopra senza rompere niente.

## Ambiente e deploy

- Python 3.12, **Streamlit 1.42.0** fissato. Le versioni in `requirements.txt`
  sono pinnate apposta (numpy<2, pyarrow<18): con combinazioni piu' nuove
  l'app va in segfault ABI. Non aggiornare senza un motivo e una prova.
- Driver DB: `psycopg[binary]` 3. Niente asyncpg qui.
- Repo GitHub `prometeostat/ranazzurra_streamlit`, branch `main`, deploy su
  Streamlit Community Cloud: https://masterconegliano.streamlit.app
- Credenziali in `.streamlit/secrets.toml` (in `.gitignore`), oppure variabili
  `PG*` / `DATABASE_URL`. **Mai leggere, copiare o stampare `secrets.toml`**;
  per la struttura c'e' `secrets.toml.example`.
- `Claude outputs/` e' in `.gitignore`: e' il posto per bozze, report e
  screenshot, non per codice dell'app.

## Struttura

`app.py` (entrypoint, `st.navigation` in modalita' hidden con barra fissa in
basso), `auth.py`, `db.py`, `season.py`, `queries.py` (tutto l'SQL),
`data.py` (loader cachati), `crud.py` (scritture), `theme.py` (CSS e helper
Plotly), `pwa.py`, `static/`, `views/` (una pagina per file, pezzi condivisi
in `views/_common.py`). Le pagine admin si registrano solo se
`auth.is_admin()`. `views/gare.py` non e' piu' in navigazione.

## Database

- Schema `public` su Aiven (progetto `swim-project`, servizio `swim`,
  db `defaultdb`). Interrogabile dal connettore Aiven MCP: `aiven_pg_read` per
  le verifiche, `aiven_pg_write` **solo su richiesta esplicita**.
- Soft delete ovunque: filtrare `is_deleted = FALSE` su `athletes`,
  `athlete_races`, `races`, `competitions`.
- `competitions."type"` e' il nome della manifestazione.
- `competitions.is_fin` distingue gare ufficiali FIN dal resto (Aquasport,
  acque libere, Stroppolo). Il filtro va **nella SQL**, non nel DataFrame,
  perche' le query tengono gia' solo il miglior tempo: si usa il marcatore
  `/*FIN*/` sulla JOIN e `queries.con_fin(sql, solo_fin)`.
- `athletes.last_name` ha spazi in coda: ogni match testuale passa da `btrim`.
- `split_times` sono frazioni, non cumulati, ordinate per `id`, quasi sempre
  ogni 50 m anche in vasca da 25. Dal 2024/25 non ci sono parziali.
- `fin_score` si prende com'e' dai risultati ufficiali, non va ricalcolato
  ne' "corretto".
- Il DB contiene solo tesserati Ranazzurra e niente posizione in gara: le
  classifiche sono interne.
- Le sigle `RANAZZURRA CONEGLIANO` e `RANAZZURRA` sono la stessa squadra.
- Niente modifiche di schema per gli import: le chiavi di riconciliazione le
  gestisce il loader. La DDL di riferimento sta nei documenti del progetto.

## Regole di codice

- SQL sempre parametrizzato (`%s`), stagioni dal 1/9 al 31/8 calcolate da
  `season.py`, mai date fisse.
- Cache dati `ttl=3600`. Cast dei tipi **dentro** le funzioni cachate e
  `.copy()` prima di mutare un DataFrame che esce dal cache (segfault pyarrow).
- Ogni scrittura passa da `db.execute()` e poi svuota la cache.
- Valori da `st.data_editor` con colonne `Int64` arrivano come `pd.NA`:
  controllare con `pd.isna()` prima di `or` / `in`. Ci sono gia' gli helper
  `crud._intero`, `crud._testo` e quelli in `views/manifestazioni.py`.
- `crud._pulisci_manifestazione()` restituisce 10 valori; insert usa 11
  placeholder e update 12. Toccando la tupla vanno ricontati tutti e tre.
- Plotly: niente colori `#rrggbbaa`, usare `rgba()`; attenzione ai kwargs
  duplicati negli helper di layout.
- CSS iniettato con `st.html()`: nel testo **nessuna parentesi angolare**,
  nemmeno nei commenti, o il sanitizer butta via tutto lo stile.
- Colori solo tramite variabili CSS in `theme.py`, una terna per tema (scuro
  e chiaro). Ogni ritocco grafico va controllato in tutti e due i temi.

## PWA e Community Cloud

Su Community Cloud l'app gira dentro un iframe (`/~/+/`) del guscio di
Streamlit. Icone, manifest e meta tag vanno iniettati in `window.top.document`
(lo fa `pwa.py`), e i file di `static/` dal documento in cima stanno sotto
`/~/+/app/static/`. In locale la cornice non esiste: tutto quello che tocca
head, icone o manifest si verifica **sulla pagina pubblica**, non solo in
locale. Offline e push non sono ottenibili con Streamlit.

## Lingua e stile

- Testi a video, commenti e docstring in italiano. Per il nuoto: "delfino" a
  video, "Farfalla" a DB (mappa in `views/_common.py`).
- Nei testi per l'utente il referente e' sempre "l'amministratore", mai la
  segreteria.
- Stile visivo: glassmorphism, palette blu/aqua/teal, Bebas Neue e Barlow
  Condensed.
- Quando una funzionalita' cambia, aggiornare la sezione del `README.md`.

## Verifica prima di consegnare

`python -m py_compile` sui file toccati; le query nuove provate sul DB vero
in sola lettura; per l'interfaccia una prova headless con Playwright su
`streamlit==1.42.0`; per PWA e layout anche il controllo sul deploy pubblico.

## Lavorare sui file

La cartella vive su Google Drive (`G:\Il mio Drive\Job\ranazzurra\
ranazzurra_streamlit`). Da sessione cloud la shell sul PC non la monta: si
lavora con stage e commit dei file. Commit e push su git li fa Mirko.
