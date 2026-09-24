# Master Conegliano — app tempi e statistiche

App Streamlit sui dati del database PostgreSQL su Aiven. Accesso riservato ai
tesserati, installabile sulla schermata home come una app.

---

## Struttura

```
ranazzurra_streamlit/
├── app.py              entrypoint: tema, login, sidebar, routing
├── auth.py             login e ruoli
├── db.py               connessione Aiven
├── season.py           stagioni agonistiche e categorie master FIN
├── queries.py          SQL
├── data.py             caricamento dati cachato e analisi dei parziali
├── crud.py             scritture e validazioni dell'anagrafica atleti
├── theme.py            CSS, palette, helper grafici
├── pwa.py              manifest e meta tag per l'installazione
├── requirements.txt
├── static/             manifest.json e icone (servite da /app/static/)
├── views/
│   ├── agenda.py       calendario manifestazioni, passate e future
│   ├── cerca.py        indice: scheda atleta e classifiche
│   ├── scheda.py       selettore atleta, riepilogo, ultime gare, elenco tempi
│   ├── confronto.py    due atleti testa a testa, gare in comune
│   ├── classifiche.py  top 5 per specialita', filtro categoria, M e F divisi
│   ├── profilo.py      account, preferiti, tema, installazione
│   ├── gestione.py     indice delle anagrafiche (solo admin)
│   ├── anagrafica.py   anagrafica atleti (solo admin)
│   └── manifestazioni.py  anagrafica manifestazioni (solo admin)
└── .streamlit/
    ├── config.toml     tema scuro + enableStaticServing
    ├── secrets.toml    credenziali (in .gitignore)
    └── secrets.toml.example
```

---

## Avvio in locale

```bash
cd ranazzurra_streamlit
python -m venv .venv
.venv\Scripts\activate          # su Windows
pip install -r requirements.txt

copy .streamlit\secrets.toml.example .streamlit\secrets.toml
# compila la password nella sezione [postgres]

streamlit run app.py
```

Se manca `secrets.toml` l'app non crasha piu': mostra un messaggio che dice
cosa creare. In alternativa ai secrets si possono usare le variabili
d'ambiente `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, oppure
`DATABASE_URL`.

---

## Accesso

Si configura in `[app]` dentro i secrets.

`auth_mode = "code"` (default): l'atleta entra con codice FIN e data di
nascita, verificati su `athletes`. Nessun provider esterno.

`auth_mode = "oidc"`: `st.login()` di Streamlit con un provider OpenID
Connect; l'email restituita viene cercata in `athletes.email`. Serve la
sezione `[auth]` nei secrets e il pacchetto Authlib.

`auth_mode = "open"`: nessun login, solo per sviluppo.

### Ruoli

Admin e allenatori scelgono qualsiasi atleta dalla barra laterale, tutti gli
altri aprono la propria scheda. Si indicano in `[app]` nei secrets, in tre
modi alternativi, e vale il primo che corrisponde:

```toml
admin_athlete_ids = [52]        # athletes.id, il piu' stabile
admin_fin_codes   = [281728]    # codice FIN
admin_emails      = ["..."]     # SOLO con auth_mode = "oidc"
coach_athlete_ids = []
coach_fin_codes   = []
coach_emails      = []
```

Attenzione alle email: in modalita' `code` l'app non chiede mai l'indirizzo,
quindi `admin_emails` non scatta. Li' servono id o codice FIN.

La spunta "resta connesso" salva un token firmato nella query string, non un
cookie: Streamlit i cookie li legge ma non li scrive.

---

## Installazione sul telefono

Serve `enableStaticServing = true` in `config.toml` (gia' impostato), che
pubblica `static/` sotto `/app/static/`. `pwa.py` inietta manifest e meta tag
Apple nella pagina.

Su iPhone: aprire in Safari, Condividi, "Aggiungi a Home".
Su Android: menu di Chrome, "Aggiungi a schermata Home".

L'app si apre a schermo intero. **Non funziona offline** e non manda
notifiche: servirebbe un service worker servito dalla radice del dominio, che
Streamlit non permette di pubblicare. Per averli davvero serve un frontend
separato che legge un'API.

---

## Scheda atleta

Due schermate. La prima e' il selettore: casella di ricerca, la propria
scheda in cima, i preferiti e poi tutti gli atleti, una riga ciascuno con
cognome e nome, categoria con anno di nascita e societa'. La stella a
sinistra mette e toglie dai preferiti, il bottone a destra apre la scheda.

La seconda e' la scheda vera, in quest'ordine: intestazione con nome,
societa', categoria e codice FIN; tre riquadri di riepilogo del periodo
scelto (gare, manifestazioni, miglior punteggio FIN); le ultime tre
manifestazioni come blocchetti cliccabili per intero, che portano ai
risultati ufficiali (la freccia in alto segnala il link);
filtro periodo e vasca; elenco dei tempi raggruppato per specialita' e vasca,
una riga per stagione, con la categoria master di quell'anno e il badge PB
sul personale di sempre. Nessun grafico.

I tre riquadri contano la stagione selezionata e ignorano i filtri vasca e
gara, che valgono solo per l'elenco sotto. Quello del punteggio FIN dice
anche quale gara l'ha prodotto, con data e manifestazione, ed e' cliccabile:
porta alla scheda della manifestazione.

Il periodo parte da *Tutte le stagioni*, cosi' la scheda si apre sullo
storico completo e i personali sono quelli veri. Sotto al periodo c'e' il
filtro **Gara**: Tutte le gare (predefinito), Stile Libero, Dorso, Rana,
Delfino, Misti. In vasca lo chiamano delfino, a database la tabella
`strokes` lo chiama Farfalla: la traduzione sta in `STILI_UI` dentro
`views/_common.py`.

La categoria porta il prefisso del sesso, M45 per un maschio e F45 per una
femmina, e viene ricalcolata stagione per stagione: nell'elenco si vede
l'atleta cambiare fascia col passare degli anni. Sotto i 20 anni non esistono
categorie e l'etichetta diventa "Giovanile".

I preferiti vivono in `st.session_state`, quindi durano quanto la sessione.
Per renderli permanenti serve una tabella a database (`athlete_id` +
`user_id`): non l'ho creata perche' tocca lo schema.

Le gare di fondo a DB hanno `pool_length` uguale alla distanza (3000, 3300,
5000): `theme.pool_label()` le etichetta "acque libere" invece di scrivere
"vasca 5000m". Per questo il filtro vasca ha tre voci, 25m, 50m e Tutte:
con le prime due il fondo sparisce, ed e' corretto ma non ovvio.

---

## Confronta

Due atleti alla volta, testa a testa, e solo le gare nuotate da tutti e due:
un confronto su specialita' che uno dei due non ha mai fatto non vuol dire
niente. Il selettore *Gara* elenca appunto le sole gare in comune, e si puo'
stringere a una sola.

Una riga per gara: il miglior tempo di ciascuno, il distacco al centro e il
piu' veloce dentro una pastiglia accesa. Sotto a ogni tempo ci sono la data,
il punteggio FIN di quella gara e il nome della manifestazione, che porta al
PDF dei risultati (`pdf_link`, con il sito come riserva per le quattro
manifestazioni che il PDF non ce l'hanno).

Per questo `COMPARE_PB_SQL` usa `DISTINCT ON` invece di `MIN`: serve sapere
*dove* e' stato fatto quel tempo, non solo quanto vale. A parita' di tempo
vince la manifestazione piu' vecchia, come per il badge PB della scheda.

Niente grafici e nessun riepilogo: su due atleti e una decina di gare i
numeri si leggono meglio delle barre.

---

## Classifiche

Una schermata sola: si sceglie la specialita' (stile, distanza e vasca) e,
volendo, la categoria. Senza filtro escono i migliori cinque tempi assoluti,
con il filtro i migliori cinque di quella categoria. Maschi e femmine sono
due classifiche separate, come in gara, e un atleta compare una volta sola
col suo tempo migliore fra quelli che restano dopo il filtro.

Il filtro categoria e' la fascia (20, 25, 30...), non l'etichetta con il
sesso: vale per M45 e F45 insieme, cosi' una scelta sola serve tutte e due
le tabelle. Chi ha meno di vent'anni finisce in *Giovanile*.

Il punto delicato e' che **il tempo appartiene alla data della manifestazione
e la categoria alla stagione di quella data**. Le fasce FIN si spostano ogni
anno: un 25"17 del dicembre 2019 e' un tempo M20, lo stesso atleta oggi e'
M25. Per questo `CLUB_RANKING_SQL` tiene il miglior tempo di ogni atleta
*per stagione* e non un solo personale: la stagione si ricava dalla data
della manifestazione (da settembre in poi e' quella che apre) e da li' esce
la categoria di allora. Filtrando M20 escono i tempi nuotati da M20, non i
tempi di chi oggi e' M20.

Nella tabella ci sono posizione, atleta, categoria di quel tempo, tempo e
distacco dal primo; sotto a ogni riga, a tutta larghezza, la data e il nome
della manifestazione che porta ai risultati (`pdf_link`, con il sito come
riserva). Il punteggio FIN e il numero di gare sono stati tolti: in una
classifica per specialita' non aggiungevano niente.

Dentro ci sono anche **gli atleti non piu' attivi**: un tempo fatto con la
squadra resta un tempo della squadra, e chi ha smesso non sparisce dagli
archivi. Nessun rischio di doppioni, in anagrafica non ci sono omonimi fra
attivi e disattivati (verificato: 45 disattivati, nessuno con un omonimo
attivo). La query porta comunque su il flag `atleta_inattivo`, se un giorno
si vuole marcarli nell'elenco.

---

## Chi vede cosa

Tutti i tesserati vedono i tempi di tutti: la scelta dell'atleta e' libera e
si fa dal selettore della Scheda. I ruoli admin e allenatore restano nei
secrets per gli usi futuri, ma non limitano piu' la lettura.

---

## Navigazione

Niente barra laterale: e' nascosta via CSS e `st.navigation` gira con
`position="hidden"`, cosi' le pagine restano registrate (servono a
`st.switch_page` e agli URL) ma il menu lo disegna l'app. Al suo posto c'e'
una **barra fissa in basso**, come in un'app: Agenda, Confronta, Cerca,
Profilo e, solo per l'amministratore, Gestione.

Cerca e Gestione sono pagine-indice: la prima porta ad Atleta e Classifiche,
la seconda alle due anagrafiche. La voce della barra resta accesa anche
quando sei in una sottopagina.

Le voci sono schede cliccabili per intero, senza un bottone "Apri" a parte:
sono `st.button` con etichetta "icona, riga vuota, titolo, riga vuota,
sottotitolo", cioe' tre paragrafi che una griglia CSS impagina come una
card. La chiave del bottone inizia per `hub_`, Streamlit la riporta come
classe `st-key-hub_...` sul contenitore ed e' li' che si aggancia il CSS.

Come e' fatta, in breve: `st.container(key="bottombar")` mette la classe
`st-key-bottombar` sul blocco, che il CSS fissa in basso con
`position: fixed` e `env(safe-area-inset-bottom)` per la tacca dell'iPhone.
Le colonne di Streamlit si impilano sotto i 640px, quindi dentro la barra
sono forzate a restare affiancate con `flex-wrap: nowrap`. L'etichetta di
ogni bottone e' "icona, riga vuota, testo": i due paragrafi che ne escono
vengono impilati e dimensionati dal CSS.

La barra si disegna **prima** del contenuto della pagina, non dopo: molte
pagine chiudono con `st.stop()` quando non hanno niente da mostrare, e tutto
quello che viene dopo non verrebbe mai disegnato. Essendo in
`position: fixed`, dove sta nel DOM non cambia niente.

Il filtro periodo sta dentro le pagine, tema e account nel Profilo. Il tema
scelto sta in `ui_theme`, che non e' la chiave di nessun widget: Streamlit
ripulisce lo stato dei widget che non ridisegna, quindi il radio del Profilo
usa una chiave sua e ricopia la scelta in `ui_theme` con `on_change`. Senza
questo giro, al primo cambio pagina si tornava al tema scuro.

---

## Agenda

Manifestazioni divise in **In programma** e **Concluse**, con nome cliccabile
sul `website_link`, organizzatore, vasche, cronometraggio, quante nostre gare
e quanti nostri atleti c'erano, e il link al programma PDF quando c'e'.

Attenzione a come sono fatti i dati: a database arrivano solo le
manifestazioni dove abbiamo gia' gareggiato, perche' le porta lo scraper dei
risultati. Oggi sono 524 e **nessuna e' futura**: l'ultima e' del 12/09/2026.
Il calendario del futuro si riempie a mano dall'Anagrafica manifestazioni,
oppure insegnando allo scraper a leggere i calendari FIN.

---

## Anagrafica atleti

Pagina riservata all'amministratore, compare nel menu solo per lui: gli
allenatori leggono tutto ma non scrivono in anagrafica.
Elenco con filtro **Stato** (Attivi di default, Inattivi, Tutti), ricerca su
cognome, nome, codice FIN ed e-mail, ordinamento sugli stessi campi piu'
quello nativo della tabella cliccando le intestazioni.

Campi gestiti: ID (assegnato dal database, non modificabile), codice FIN,
nome, cognome, sesso, data di nascita, e-mail e lo stato **Attivo**.

**Elimina non cancella.** La soft delete mette `is_deleted = TRUE` e riempie
`deletion_user_id` e `deletion_utc_date_time`; gare, risultati e storico
restano attaccati all'atleta. In anagrafica ci sono gia' casi cosi': Babuin
risulta inattivo e ha 41 gare a database. Prima di procedere l'app chiede
conferma e dice quante gare sono coinvolte. Su un atleta gia' inattivo il
pulsante diventa **Riattiva**, che rimette `is_deleted = FALSE` e ripulisce i
campi di cancellazione.

Note sullo schema, verificate sul DB prima di scrivere il codice:

- `creation_user_id` e' NOT NULL con foreign key su `users`: gli inserimenti
  usano l'utente tecnico 1 (`system`), cambiabile con `db_user_id` in `[app]`
  nei secrets. A DB gli atleti esistenti hanno 1 oppure 2 (`devsupport`).
- `sex` e' un booleano NOT NULL, TRUE = maschile.
- `fin_code` non ha vincolo di unicita': il controllo dei duplicati lo fa
  l'app e blocca il salvataggio indicando chi occupa gia' quel codice.
- `company_id` non e' fra i campi editabili: i nuovi atleti ereditano la
  societa' piu' diffusa in anagrafica, che oggi e' Ranazzurra Conegliano.

## Anagrafica manifestazioni

Stesso schema dell'anagrafica atleti, riservata all'amministratore. Campi:
nome (`competitions.type`), date di inizio e fine, apertura e chiusura
iscrizioni, cronometraggio (tendina con i valori gia' presenti a database),
massimo gare per atleta, link al sito e al PDF. Filtri per stato, per
passato/futuro e ricerca sul nome.

Anche qui "Elimina" e' una soft delete: `is_deleted = TRUE`. La
manifestazione sparisce da agenda, schede e classifiche, ma le gare e i
risultati collegati restano a database e tornano appena la riattivi. Il form
controlla che la fine non preceda l'inizio, che le iscrizioni non chiudano
dopo la partenza e che i link comincino per http.

---

La pagina "Gare e passaggi" e' stata tolta dal menu. Il file `views/gare.py`
resta sul disco ma non viene piu' eseguito da `st.navigation`: si puo'
cancellare. Con lui sparisce la vista sui parziali, che comunque erano
importati solo fino alla stagione 2023/24.

Le scritture passano da `db.execute()`, stesso stile parametrizzato delle
letture, e dopo ogni salvataggio svuotano il cache dei dati: senza quello le
altre pagine continuerebbero a mostrare la fotografia vecchia fino a un'ora.

---

## Deploy su Streamlit Cloud

Repository su GitHub, poi share.streamlit.io, New app, file `app.py`. Il
contenuto di `secrets.toml` va incollato in App settings, Secrets. Con
`auth_mode = "oidc"` il `redirect_uri` deve puntare all'URL pubblico
dell'app, non a localhost.

---

## Note tecniche

Cache dati un'ora (`ttl=3600`). Il cast dei tipi si fa dentro le funzioni
cachate, perche' mutare un DataFrame dopo il cache manda in segfault il
serializzatore pyarrow.

I colori stanno tutti in variabili CSS, una terna per tema. Il testo
secondario (`--muted`) e' stato schiarito e i titoli hanno una variabile
loro, `--sky`, un azzurro chiaro sul tema scuro e un blu profondo su quello
chiaro: prima erano ciano acceso e su telefono al sole si leggevano male.
Il teal resta il colore delle azioni e degli accenti.

Il CSS viene iniettato con `st.html()`, che passa da un sanitizer HTML: dentro
quel testo **non devono comparire parentesi angolari**, nemmeno in un commento
CSS. Un innocuo `/* e' un <a>, non un <button> */` viene letto come tag e fa
buttare via l'intero blocco di stile, lasciando l'app senza grafica in tutti e
due i temi. Successo, sistemato, e vale la pena ricordarselo.

In modalita' chiara servono ritocchi mirati perche' i widget nascono scuri dal
tema di `config.toml`: bottoni, link-bottoni (che sono ancore, non bottoni),
pallini dei radio (il cerchio precede l'input nel DOM, quindi lo stato
selezionato si prende con `:has()`) e la barra in alto.

I cognomi in `athletes.last_name` hanno spazi in coda su meta' anagrafica:
ogni match testuale passa da `btrim`.

I parziali in `split_times` sono tempi di frazione e non cumulati, ordinati
per `id`, e la granularita' e' quasi sempre ogni 50 m anche in vasca da 25.
**Punteggi FIN, una nota per non sbagliarsi.** Il `fin_score` arriva dai
risultati ufficiali e si prende cosi' com'e': non va ricalcolato ne'
"corretto" sulla base di controlli di coerenza interna.

Il punteggio FIN e' lineare nell'inverso del tempo, quindi verrebbe naturale
pretendere che dentro la stessa gara il prodotto `punti x tempo` cambi da una
categoria all'altra. Non sempre succede: ai Campionati Italiani Invernali
UNIPOL del 06/12/2024, per dire, nei 50 rana e nei 50 stile quel prodotto e'
identico per atleti di eta' e sesso diversi. Sembra un errore di import e non
lo e', quei punteggi sono stati verificati sui risultati ufficiali e sono
giusti. Manifestazioni diverse possono usare basi diverse, e il database
riporta quello che ha pubblicato il cronometraggio.

`data.split_table()` deduce i metri per frazione e avvisa quando i parziali
sono irregolari invece di inventare le distanze. Dalla stagione 2024/25 in poi
non ne e' stato importato nessuno: va sistemato lo scraper FIN Veneto.

Il database contiene solo i nostri tesserati e `athlete_races` non ha la
posizione in gara, quindi le classifiche sono interne alla squadra. Il
confronto con gli avversari passa dal punteggio FIN.
#   r a n a z z u r r a _ s t r e a m l i t  
 