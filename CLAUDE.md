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
- L'iscrizione a una gara e' la stessa riga del risultato: `athlete_races`
  con `entry_time` valorizzato e `final_time` ancora vuoto. Indice unico
  parziale `ux_athlete_races_attive` su `(race_id, athlete_id)` dove
  `is_deleted = FALSE`: niente doppia iscrizione.
- Le staffette sono gare a parte (`race_events.is_relay`): fuori dal limite
  `competitions.max_races_per_athlete`, e nelle iscrizioni senza tempo.
- Il programma di gara sta su `races`: `race_date` (giornata), `session`
  (1 mattino, 2 pomeriggio, 3 sera, con CHECK) e `race_order` (numero dentro
  la fascia, CHECK > 0). Tutte e tre nullable e vuote su tutto lo storico.
  L'ordinamento va fatto con il frammento `queries.ORDINE_PROGRAMMA`, che
  mette i NULL in fondo e lascia ricadere le gare senza programma
  sull'ordine di sempre; a video i blocchi li costruisce
  `views/_common.blocchi_programma()`, usata sia dalle iscrizioni sia dai
  risultati di manifestazione.
- `athletes.medical_certificate_expiry` (`date`, nulla ammessa) e' la
  scadenza del certificato medico: la scrive solo l'anagrafica, il Profilo
  la legge con una query sul solo id della sessione.
- **Le colonne di audit non ci sono su tutte le tabelle.** `races` ha solo
  `creation_*` e `deletion_user_id`: niente `last_modification_*`.
  `athlete_races` e `competitions` hanno `last_modification_user_id` ma non
  la data. Complete solo `athletes`, `split_times` e
  `athlete_credentials`. In `information_schema` le posizioni mancanti
  restano vuote, quindi una lettura parziale inganna: prima di scrivere una
  UPDATE va guardato l'elenco completo delle colonne di quella tabella.
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
- `st.data_editor` **non accetta uno Styler**: una tabella o si colora o si
  edita. Dove servono tutti e due, il colore diventa una colonna (il pallino
  del certificato in `views/anagrafica.py`).
- `st.data_editor` tiene le celle toccate **per posizione di riga**: se le
  righe cambiano (filtro, ordinamento, ricerca) le modifiche in sospeso
  finiscono su altri. La chiave del widget deve portare dentro un'impronta
  delle righe mostrate, cosi' cambia con loro.
- I salvataggi in blocco validano tutto il lotto e poi scrivono, mai riga
  per riga: `crud.salva_anagrafica` e `crud.salva_programma`. Un controllo
  che la validazione della singola riga non puo' fare e' il duplicato dentro
  il lotto stesso (codice FIN).
- `crud._pulisci_manifestazione()` restituisce 11 valori (gli ultimi due sono
  `is_fin` e `organizer_company_id`); insert usa 12 placeholder e update 13.
  Toccando la tupla vanno ricontati tutti e tre.
  Stessa attenzione per gli atleti: insert 12 placeholder, update 11.
- `crud.crea_gara()` svuota la cache, `crud._inserisci_gara()` no: la
  clonazione ne crea molte di fila e la svuota una volta alla fine.
- `RACE_UPDATE_SQL` riscrive anche giornata, fascia e ordine: il form della
  singola gara deve ricopiarli dalla riga che sta modificando, se no
  salvando il nome si azzera il programma. Per la sola griglia del programma
  c'e' `RACE_PROGRAM_UPDATE_SQL`, che tocca quelle tre colonne e basta.
- La soglia dei 60 giorni per il certificato medico e i colori del semaforo
  stanno in `views/anagrafica.py` e `views/profilo.py` (`GIORNI_PREAVVISO`).
  Nella tabella sono tinte rgba esplicite, non `var(--…)`: lo Styler finisce
  nel grid, che le variabili CSS del tema non le risolve.
- Le regole delle iscrizioni (finestra aperta, limite individuali,
  proprieta' della riga) stanno in `crud.salva_iscrizioni` e rileggono il
  database: l'interfaccia disabilita i bottoni, non autorizza.
- **Emulazione**: `auth.current_user()` puo' restituire un atleta emulato
  dall'amministratore, `auth.utente_vero()` restituisce sempre chi e'
  collegato davvero. I permessi per avviare o chiudere un'emulazione si
  controllano sul secondo (dentro l'emulazione `is_admin()` risponde per
  l'emulato). Ogni pagina che scrive chiede prima `auth.sola_lettura()`.
- **Una lettura cachata non e' una rilettura.** Prima di scrivere, lo stato
  va preso da una query senza cache: `crud._stato_a_database` per le
  iscrizioni. Decidere insert/update sull'`entry_id` che arriva dalla pagina
  (fotografia vecchia fino a 60 s) faceva sbattere l'INSERT contro
  `ux_athlete_races_attive` quando la riga nasceva altrove nel frattempo.
  `SIGNUP_INSERT_SQL` ha anche un `ON CONFLICT … DO UPDATE` sull'indice
  parziale come rete, e un'iscrizione tolta prima si riattiva con
  `ENTRY_REACTIVATE_SQL` invece di crearne una nuova.
- Plotly: niente colori `#rrggbbaa`, usare `rgba()`; attenzione ai kwargs
  duplicati negli helper di layout.
- CSS iniettato con `st.html()`: nel testo **nessuna parentesi angolare**,
  nemmeno nei commenti, o il sanitizer butta via tutto lo stile.
- Colori solo tramite variabili CSS in `theme.py`, una terna per tema (scuro
  e chiaro). Ogni ritocco grafico va controllato in tutti e due i temi.

## Script standalone (fuori da Streamlit)

- `db.py` dipende da `st.secrets` e `st.cache_resource`: gli script lanciati
  a mano **non lo importano**. Leggono `.streamlit/secrets.toml` con
  `tomllib` (sezione `[postgres]`, poi `[app] db_user_id` per
  `creation_user_id`, default 1) e usano psycopg direttamente; fallback sulle
  variabili `PG*`, come `db.py`.
- **Trappola psycopg3**: la connessione parte con `autocommit=False`, quindi
  gia' le SELECT aprono una transazione implicita. Un `conn.transaction()`
  successivo diventa un savepoint annidato: il commit chiude solo il
  savepoint e la `conn.close()` finale fa rollback di tutto **senza errori**
  (gli id di RETURNING esistono solo dentro la transazione: il programma
  stampa "scritto" e il DB resta vuoto — successo sull'import Aquasport
  10/11/2013). Regola: `conn.autocommit = True` subito dopo la connect, poi
  `with conn.transaction():` per le scritture, e dopo il commit rileggere i
  conteggi dal DB come verifica.
- Ogni script di scrittura ha `--dry-run` (solo lettura, stampa il piano) e
  chiede conferma prima di scrivere.

## Import risultati da PDF

`import_risultati.py <file.pdf>` importa i "riepilogo risultati" FIN Veneto
(intestazione RISULTATI RIEPILOGATIVI). Generico: niente dati embedded,
parsa il PDF e riconcilia tutto a runtime. Uso tipico:

1. la manifestazione si crea prima dall'app (Anagrafica manifestazioni):
   lo script la riconosce dalla data nel PDF (o con `--competition-id`);
2. `python import_risultati.py file.pdf --dry-run` stampa il piano;
3. `python import_risultati.py file.pdf` scrive dopo conferma.

Regole del loader (tutte gia' validate su manifestazioni reali):

- tengono solo le righe delle societa' Ranazzurra; atleti matchati su
  "COGNOME NOME" + anno di nascita (`btrim`): chi non e' in anagrafica
  blocca tutto l'import e va creato prima in Anagrafica atleti;
- le gare si riconciliano per **evento + vasca + sesso**: il sesso sta nel
  NOME della gara ("... Maschi" / "... Femmine" / "MX"), non nel
  race_event — maschi e femmine condividono lo stesso evento, e uno stesso
  evento puo' comparire piu' volte nella stessa manifestazione. Gara dello
  stesso sesso con nome diverso = stop e verifica a mano (import storici
  con nomi brevi tipo "50 Dorso");
- una gara puo' continuare sulla pagina successiva senza ripetere il
  titolo (pagina di continuazione: la riga dopo RISULTATI RIEPILOGATIVI e'
  gia' un risultato, si eredita la gara precedente);
- staffette: nel PDF i frazionisti sono le 2 righe atleta sopra e le 2
  sotto la riga squadra (layout a meta' altezza), possono avere il
  parziale fra parentesi che **non** si importa; la riga squadra puo'
  avere il suffisso FG (fuori gara): si importa comunque col suo tempo;
- `fin_score` si legge dalla colonna Pti quando c'e', altrimenti NULL
  (i PDF Aquasport non la compilano);
- idempotente: righe identiche gia' presenti vengono saltate, rieseguire
  non crea doppioni.

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
- **A ogni rilascio**: alzare `VERSIONE` e `DATA_RILASCIO` in `version.py` e
  aggiungere il blocco in `CHANGELOG.md`. Quello e' il file che leggono gli
  atleti dalla pagina Novita', quindi si scrive in italiano corrente e per
  funzione, non per commit: niente nomi di file, di colonne o di query.

## Verifica prima di consegnare

`python -m py_compile` sui file toccati; le query nuove provate sul DB vero
in sola lettura; per l'interfaccia una prova headless con Playwright su
`streamlit==1.42.0`; per PWA e layout anche il controllo sul deploy pubblico.

## Lavorare sui file

La cartella vive su Google Drive (`G:\Il mio Drive\Job\ranazzurra\
ranazzurra_streamlit`). Da sessione cloud la shell sul PC non la monta: si
lavora con stage e commit dei file. Commit e push su git li fa Mirko.

**Prima di riscrivere un file sul Drive va sempre riletto da li'.** Piu'
sessioni lavorano sullo stesso progetto: una copia in cache vecchia di due
giorni, ricommittata intera, cancella in silenzio quello che ha scritto
qualcun altro nel frattempo. E' gia' successo con Clona, l'organizzatore
delle manifestazioni e l'interruttore della scheda atleta, recuperati poi dal
commit `b7611ba`. Si confrontano le dimensioni e si fa un diff, non si
sovrascrive a scatola chiusa.

## Funzioni da non perdere

Elenco di controllo per chi riscrive questi file, perche' sono arrivate da
sessioni diverse: **Clona manifestazione + gare** e **tendina Organizzatore**
in `views/manifestazioni.py` (con `clona_manifestazione` in `crud.py` e
`organizer_company_id` nelle tre query delle manifestazioni),
**interruttore "Solo il miglior tempo per stagione"** in `views/scheda.py`,
**sezione Gare** dentro Modifica manifestazione, **flag FIN**, e tutta la
parte **iscrizioni** (`views/iscrizioni*.py`).
