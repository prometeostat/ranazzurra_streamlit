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
│   ├── cerca.py        indice: atleta, classifiche, manifestazioni
│   ├── scheda.py       selettore atleta, riepilogo, ultime gare, elenco tempi
│   ├── confronto.py    due atleti testa a testa, gare in comune
│   ├── accessi.py      registro accessi, solo admin
│   ├── classifiche.py  top 5 per specialita', filtro categoria, M e F divisi
│   ├── risultati.py    una manifestazione, gara per gara, con gli iscritti
│   ├── profilo.py      account, preferiti, tema, installazione
│   ├── iscrizioni.py   indice: nuove iscrizioni e lista
│   ├── iscrizioni_nuove.py  l'atleta si iscrive alle gare
│   ├── iscrizioni_mie.py    le proprie iscrizioni, per manifestazione
│   ├── iscrizioni_admin.py  iscrizioni ricevute ed Excel (staff)
│   ├── gestione.py     indice dell'area riservata (staff e admin)
│   ├── anagrafica.py   anagrafica atleti (solo admin)
│   ├── manifestazioni.py  anagrafica manifestazioni e loro gare (solo admin)
│   └── tempi.py        inserimento tempi e punti FIN (solo admin)
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

Lo stesso messaggio, pero', esce anche quando `secrets.toml` c'e' ma **non
e' TOML valido**: Streamlit non legge mezzo file, o lo capisce tutto o
niente, quindi un errore di sintassi nella sezione `[app]` fa sparire anche
`[postgres]`. L'inciampo tipico e' una lista di stringhe senza virgolette,
`admin_emails = [mario@rossi.it]` invece di `["mario@rossi.it"]`: gli id e i
codici FIN sono numeri e vanno nudi, le email sono stringhe e vanno fra
virgolette. Per controllare al volo, dalla cartella del progetto:

```bash
python -c "import tomllib; tomllib.load(open('.streamlit/secrets.toml','rb')); print('ok')"
```

---

## Accesso

Si entra con **l'e-mail dell'anagrafica e una password scelta dall'atleta**.
Nessun provider esterno, nessun codice FIN: il nome utente e' l'indirizzo che
la societa' ha in `athletes.email`, e la password vive a database come hash.

### Primo accesso

Chi non ha ancora una password apre la scheda *Primo accesso*, si riconosce
con **e-mail e data di nascita** e sceglie la sua password. La data di
nascita e' a database per tutti i tesserati, il codice FIN no (sette attivi
non ce l'hanno), per questo la verifica passa di li'.

L'amministratore puo' anche generare una **password temporanea** dalla scheda
di un atleta in Anagrafica: si vede una volta sola, si consegna a voce, e al
primo ingresso l'app obbliga a sostituirla.

### Allenatori e staff

Chi allena ma non gareggia entra come tutti gli altri, perche' anche lui sta
in anagrafica: si crea la sua riga con nome, e-mail e data di nascita, si
lascia vuoto il codice FIN e si spunta **Allenatore o staff** togliendo la
spunta ad **Atleta**. Da quel momento fa il primo accesso con e-mail e data
di nascita come chiunque, ma non compare nei selettori atleta, nelle
classifiche e nei conteggi dei tesserati.

Chi fa tutti e due i ruoli tiene entrambe le spunte: e' un atleta a tutti gli
effetti, compare ovunque, e in piu' ha il ruolo di allenatore.

Il flag `is_staff` vale come ruolo *allenatore* senza bisogno di toccare i
secrets. L'amministratore invece resta una cosa dei secrets: e' un permesso
piu' pesante e non si da' con una spunta in anagrafica.

### Come sono tenute le password

Hash **scrypt** della libreria standard (`n=16384, r=8, p=1`, sale casuale da
16 byte), circa 45 millisecondi a verifica, salvato in un campo che si
descrive da solo:

```
scrypt$16384$8$1$<sale base64>$<hash base64>
```

In chiaro non esiste da nessuna parte: nemmeno l'amministratore puo'
rileggere la password di qualcuno. Se serve, si azzera e l'atleta ne sceglie
una nuova. Il confronto e' a tempo costante (`hmac.compare_digest`) e il
messaggio di errore e' sempre lo stesso, "e-mail o password non corrette",
per non far capire dall'esterno quali indirizzi esistono.

Dopo cinque tentativi sbagliati l'account si blocca per quindici minuti; il
contatore sta a database, quindi il blocco vale ovunque e non si aggira
cambiando browser. Ogni tentativo, riuscito o no, finisce nel registro
accessi.

### Cosa puo' fare l'amministratore

Dalla scheda di un atleta in **Anagrafica atleti**, riquadro *Accesso
all'app*: vede se la password esiste, quando e' stata impostata e quando c'e'
stato l'ultimo accesso, e ha tre bottoni. *Azzera password* toglie la
credenziale e l'atleta rifa' il primo accesso. *Password temporanea* ne
genera una da consegnare, con cambio obbligatorio al primo ingresso.
*Sospendi accesso* blocca l'ingresso senza toccare la password, per esempio
quando qualcuno lascia la squadra.

L'atleta cambia la sua password da **Profilo**, indicando quella attuale.

### Vedere l'app con gli occhi di un atleta

Sotto le azioni dell'anagrafica c'e' **Vedi l'app come …**, riservato
all'amministratore: da li' in poi pagine, menu e query lavorano con
l'identita' di quell'atleta, quindi si vede davvero quello che vede lui,
comprese le sezioni riservate che spariscono. Serve a capire perche' uno
"non trova" una gara o un'iscrizione, senza toccargli la password.

**E' in sola lettura.** Durante l'emulazione si spengono il bottone
Iscriviti in Agenda, la pagina Nuove iscrizioni, il cambio password e
l'uscita: una riga scritta cosi' sarebbe indistinguibile da una scritta
dall'atleta, perche' `creation_user_id` e' l'utente tecnico e non chi sta
usando l'app. Una fascia in cima a ogni pagina dice chi si sta guardando e
riporta indietro con un bottone.

Nel codice: `auth.emula()`, `auth.smetti_emulazione()`,
`auth.in_emulazione()` e `auth.sola_lettura()`, che e' quella che le pagine
chiedono prima di disegnare un bottone che scrive. L'identita' finta vive in
`st.session_state` sotto `auth.SESSION_AS`, non tocca il token "ricordami" e
sparisce al logout. `auth.current_user()` restituisce l'emulato,
`auth.utente_vero()` sempre quello collegato davvero: il permesso per
avviare un'emulazione si controlla sul secondo, se no dall'emulazione non si
potrebbe piu' cambiare atleta. Inizio e fine finiscono nel registro accessi
come `EMULAZIONE` e `FINE EMULAZIONE`, con nota su chi guardava chi.

### Le tabelle

```sql
CREATE TABLE athlete_credentials (
    athlete_id                      integer PRIMARY KEY REFERENCES athletes(id),
    creation_utc_date_time          timestamp NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
    creation_user_id                integer NOT NULL,
    last_modification_utc_date_time timestamp,
    last_modification_user_id       integer,
    password_hash                   varchar(300) NOT NULL,
    must_change                     boolean NOT NULL DEFAULT false,
    failed_attempts                 integer NOT NULL DEFAULT 0,
    locked_until_utc                timestamp,
    last_login_utc                  timestamp,
    is_enabled                      boolean NOT NULL DEFAULT true
);
CREATE UNIQUE INDEX ux_athletes_email_attivi ON athletes (lower(btrim(email)))
    WHERE is_deleted = FALSE AND email IS NOT NULL AND btrim(email) <> '';
```

L'e-mail resta una sola, quella di `athletes`: qui ci sono solo le
credenziali. L'indice unico parziale impedisce che due tesserati attivi
finiscano con lo stesso indirizzo, che con l'e-mail come nome utente sarebbe
un guaio.

**Da sistemare prima di aprire a tutti:** su 51 tesserati attivi solo 30
hanno un'e-mail in anagrafica. Gli altri 21 non possono entrare finche' non
gliela si aggiunge con Modifica.

### Le altre modalita'

Restano disponibili cambiando `auth_mode` in `[app]`: `code` per il vecchio
accesso con codice FIN e data di nascita, `oidc` per un provider OpenID
Connect (serve la sezione `[auth]` nei secrets e Authlib), `open` per
sviluppare senza login, dove l'ospite e' amministratore per definizione.

### Ruoli

L'amministratore si indica in `[app]` nei secrets, in tre modi alternativi, e
vale il primo che corrisponde. L'allenatore si puo' indicare allo stesso modo
oppure, molto piu' comodo, con la spunta *Allenatore o staff* in anagrafica
(`athletes.is_staff`), che non richiede di rimettere mano ai secrets:

```toml
admin_athlete_ids = [52]        # athletes.id, il piu' stabile
admin_fin_codes   = [281728]    # codice FIN
admin_emails      = ["..."]     # con auth_mode "password" oppure "oidc"
coach_athlete_ids = []
coach_fin_codes   = []
coach_emails      = []
```

Il ruolo si ricalcola dai secrets a ogni rerun, non viene congelato al
momento del login: se aggiungi un id alla lista degli amministratori la
modifica vale subito, senza uscire e rientrare.

**Se in locale vedi Gestione e online no**, il motivo e' quasi sempre questo:
in locale `secrets.toml` ha `auth_mode = "open"`, e l'ospite della modalita'
aperta e' amministratore per definizione, mentre online si entra davvero e il
ruolo dipende dalle liste. Se il blocco `[app]` non e' stato incollato nei
secrets dell'ambiente remoto (su Streamlit Cloud sta in App settings,
Secrets), non c'e' nessun amministratore e la voce Gestione sparisce. Va
incollato tutto il blocco, `token_secret` compreso, se no il token del "resta
connesso" viene firmato con la chiave di sviluppo.

Per capirlo senza indovinare c'e' l'espansore **Diagnostica accesso** nel
Profilo: dice la modalita' attiva, se il blocco `[app]` e' stato letto,
quanti amministratori sono configurati, il proprio id e codice FIN e il ruolo
calcolato in quel momento. Non mostra nessun valore segreto.

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

## Gare ufficiali FIN

`competitions.is_fin` dice se una manifestazione e' del calendario federale.
Serve perche' nel database convivono due mondi: le gare FIN, dove il tempo
vale per le graduatorie e c'e' il punteggio, e tutto il resto (il circuito
Aquasport, le traversate in acque libere, la gara sociale dello Stroppolo),
dove il tempo e' comunque un tempo ma non si puo' confrontare allo stesso
modo. Quanto pesa: su 2.085 combinazioni atleta/specialita'/vasca, 462
esistono **solo** grazie a gare non ufficiali e in altri 164 casi il
personale cambia se si contano le sole ufficiali.

La colonna e' `boolean NOT NULL DEFAULT TRUE`: in dubbio una manifestazione
nuova e' ufficiale, che e' il caso piu' frequente. Il primo riempimento ha
seguito questa regola, nell'ordine:

1. il nome contiene *aquasport* o *acquasport* → non ufficiale (63 righe,
   anche quando il link porta a finveneto, perche' il circuito usa comunque
   il portale regionale);
2. nessun link al sito → ufficiale: sono le manifestazioni future del
   calendario, il link arriva dopo (12 righe);
3. il link contiene *finveneto* o *federnuoto* → ufficiale;
4. tutto il resto → non ufficiale.

Poi due correzioni a mano: i Campionati Italiani Master di Riccione (link a
microplustiming) e il Circuito Regionale FVG Master Open (link a natatoria).
Risultato: 259 ufficiali e 72 no, fra cui le nove non-Aquasport che ci si
aspetta di trovare li' (Rovigno, Caorle, le traversate, lo Stroppolo,
SwimTeen).

Da qui in avanti il flag si gestisce dall'app: in Anagrafica manifestazioni
c'e' la spunta **Manifestazione ufficiale FIN** nel form e la colonna FIN
nell'elenco. Niente SQL a mano per correggere un caso.

In Agenda, Confronta, Scheda atleta, Classifiche e Manifestazioni c'e' il
radio **Manifestazioni**: Tutte (predefinito), Ufficiali FIN, Non ufficiali.
La scelta vive in `fin_filter` e la si legge con `fin_filter()`, che
restituisce `None`, `True` o `False`.

Il punto tecnico: **il filtro sta nella SQL, non nel DataFrame**. Le query
dei tempi tengono gia' solo la riga migliore per atleta (`DISTINCT ON`,
`MIN`), quindi buttare via le righe non ufficiali dopo lascerebbe un buco
dove c'era un personale fatto in una gara non ufficiale, invece del miglior
tempo utile. Ogni query interessata ha il marcatore `/*FIN*/` attaccato alla
JOIN su `competitions` e `queries.con_fin(sql, solo_fin)` lo trasforma in
`AND co.is_fin = TRUE/FALSE`. Non e' un parametro `%s` perche' andrebbe
infilato nell'ordine giusto in dieci query con parametri posizionali, ed e'
il modo piu' comodo per sbagliare; il valore e' un booleano nostro, niente
che scriva l'utente finisce in quella stringa. Sull'agenda, dove la riga
*e'* la manifestazione, basta `apply_fin()` sul DataFrame.

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
con la categoria master di quell'anno e il badge PB sul personale di sempre.
Nessun grafico.

Sopra all'elenco c'e' l'interruttore **Solo il miglior tempo per stagione**,
spento di default: cosi' si vedono tutte le gare nuotate, anche la stessa
specialita' ripetuta piu' volte nella stessa stagione. Acceso resta una riga
sola per specialita', vasca e stagione, con il miglior tempo di quell'anno.
Il migliore e' sempre quello di *ogni* stagione e mai il migliore assoluto:
altrimenti con "Tutte le stagioni" resterebbe una riga per combinazione e il
badge PB si accenderebbe su tutte, confrontando un tempo con se stesso.

I tre riquadri contano la stagione selezionata e ignorano i filtri vasca e
gara, che valgono solo per l'elenco sotto; il filtro **Manifestazioni**
(ufficiali FIN o no) invece conta anche per loro, perche' lavora nella query
e non sul DataFrame gia' caricato. Quello del punteggio FIN dice anche quale
gara l'ha prodotto, con data e manifestazione, ed e' cliccabile: porta alla
scheda della manifestazione.

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

## Manifestazioni

Terza porta di Cerca, accanto ad Atleta e Classifiche, e pagina sua
(`views/risultati.py`, url `/manifestazioni`). Ha preso il posto del blocco
"Ultime manifestazioni", che mostrava quattro schede senza poterci entrare
dentro.

Si procede in tre passi: si sceglie il **Periodo** (e, volendo, se vedere
solo le ufficiali FIN), si sceglie la **Manifestazione**, si preme
**Visualizza** e sotto compare gara per gara
chi c'era, con tempo e punteggio FIN. Il bottone non e' un vezzo: con
"tutte le stagioni" nel menu ci sono centinaia di manifestazioni e ognuna
costa una query, quindi si scorre il menu senza che l'app parta a
interrogare a ogni passaggio. La manifestazione mostrata resta in
`mf_vista`; cambiando periodo o voce del menu la tabella sparisce, se no
resterebbe appesa a una scelta che non e' piu' quella a video.

Nel menu finiscono solo le manifestazioni **del periodo scelto in cui c'e'
qualcosa di nostro** (`nostre_gare > 0`), dalla piu' recente; il filtro
Periodo e' lo stesso delle altre pagine, quindi con "tutte le stagioni" c'e'
dentro tutto lo storico. La testata ripete data, organizzatore, vasca e
quante gare e quanti atleti nostri, con il nome che porta ai risultati
ufficiali (`pdf_link`, con `website_link` come riserva).

**Nel futuro si guarda fino a 75 giorni** (`ORIZZONTE` in
`views/risultati.py`, la stessa soglia dell'Agenda): le manifestazioni non
ancora nuotate ma con gente iscritta compaiono in elenco marcate *da
nuotare*, quelle piu' in la' no, perche' non avrebbero niente da mostrare.
Funziona perche' a database l'iscrizione e il risultato sono la stessa riga
di `athlete_races`, una con il tempo e l'altra ancora senza, quindi
`nostre_gare` conta gia' gli iscritti: su una manifestazione futura i tempi
sono quelli dichiarati in iscrizione e la didascalia lo dice.

La query e' `COMPETITION_RESULTS_SQL` e, a differenza del resto dell'app,
**non filtra niente**:

- ci sono **le staffette**, con il tempo della squadra ripetuto su ogni
  frazionista (a database e' cosi': una riga per frazionista, stesso tempo,
  punteggio FIN nullo). Le frazioni non si numerano, sarebbe una classifica
  finta;
- ci sono **gli iscritti senza tempo**: non partiti, ritirati o squalificati.
  Restano in fondo alla gara, senza posizione, con un trattino al posto del
  tempo. Sono 136 righe su 7.642, poche ma sono informazione.

L'ordine arriva tutto dalla query: prima il programma (giornata, fascia,
numero), poi le individuali e le staffette, dentro ogni gruppo per stile e
distanza e dentro la gara dal tempo migliore. La distanza va ordinata a
numero, ma le staffette si chiamano `4x50` e `8x25`: il `CASE` tiene
separati i due casi, cosi' il cast a intero non vede mai una stringa con
la x.

Dove il programma e' compilato le gare escono raggruppate per **giornata e
fascia oraria**, con un'intestazione per blocco (il giorno compare solo se
le giornate sono piu' di una). Dove non c'e', e nello storico non c'e' mai,
l'elenco resta piatto esattamente come prima: se ne occupa
`blocchi_programma()` in `views/_common.py`, la stessa funzione che usano le
iscrizioni.

La categoria accanto al nome e' quella **della stagione in cui si e' nuotato
quel tempo**, come nelle classifiche: la stagione si ricava dalla data della
manifestazione (da settembre in poi e' quella nuova). Sotto i vent'anni non
esistono fasce FIN e l'etichetta diventa *Giov. M* o *Giov. F*: in gare come
il circuito Aquasport maschi e femmine nuotano insieme, e senza il sesso non
si capirebbe chi e' chi.

Le righe non sono una tabella ma dei flex (`.mf-row` in `theme.py`): su un
telefono quattro colonne finivano fuori schermo, cosi' invece nome e
categoria stanno a sinistra, tempo e punti a destra. La riga di chi e'
collegato e' accesa, come nelle classifiche.


---

## Iscrizioni alle gare

L'atleta si iscrive da solo, dentro la finestra decisa dalla manifestazione.
**Cerca > Iscrizioni** e' l'indice (`views/iscrizioni.py`) con due porte:

- **Nuove iscrizioni** (`views/iscrizioni_nuove.py`, url
  `/nuove-iscrizioni`), dove ci si iscrive;
- **Lista iscrizioni** (`views/iscrizioni_mie.py`, url `/lista-iscrizioni`),
  dove si guarda quello che si e' gia' fatto.

Alla prima si arriva anche dal bottone **Iscriviti** in Agenda e dalla
scorciatoia in cima a Cerca > Manifestazioni.

### Lista iscrizioni

Un filtro solo, che parte **vuoto** e contiene solo le manifestazioni per
cui si e' davvero fatta un'iscrizione (le manifestazioni in programma piu'
quelle passate con `entry_time` valorizzato). Scelta la manifestazione, la
tabella mostra le sue gare con tipo, vasca, tempo d'iscrizione, **giornata,
fascia oraria e numero di programma**, e quando c'e' il tempo di gara. Le
righe seguono l'ordine in cui si nuota, con le gare senza programma in
fondo e i trattini al posto delle tre colonne. Se la finestra e' ancora
aperta, un bottone riporta a Nuove iscrizioni con quella manifestazione
gia' selezionata; se e' chiusa, lo dice.

### La finestra

Vale `competitions.open_registration_date` e `close_registration_date`, due
`date`, **piu' 30 giorni di anticipo**: si raccoglie dalle date di apertura
meno trenta fino alla chiusura, estremi compresi, perche' la squadra mette
insieme le adesioni prima di portarle sul portale federale. I giorni sono
in `crud.GIORNI_ANTICIPO` e la stessa regola sta nelle query
(`SIGNUP_MEETS_SQL`, `SIGNUP_WINDOW_SQL`, `MY_SIGNUPS_SQL`): se cambia il
numero, va cambiato in tutti e due i posti.

Fuori da li' non si scrive niente, e la verifica non sta nel bottone
disabilitato: `crud.salva_iscrizioni` rilegge le date a database prima di
toccare qualunque riga. Senza le due date la manifestazione non e'
iscrivibile.

In **Agenda > In programma** ogni manifestazione futura ha il bottone
quadrato **Iscriviti** di fianco alla scheda, non sotto (lo stile sta in
`theme.py`, agganciato alla chiave `isc_`). E' acceso quando si puo'
davvero, spento e tratteggiato quando le date mancano, quando mancano piu'
di trenta giorni all'apertura o quando la chiusura e' passata: il motivo
sta nel tooltip. Spento resta comunque li', cosi' si vede che quella gara
una iscrizione ce l'ha.

### Come e' fatta un'iscrizione

Non c'e' una tabella nuova: l'iscrizione e' la riga di `athlete_races` con
**`entry_time`** valorizzato e `final_time` ancora vuoto. Quando la gara e'
stata nuotata, Inserisci tempi scrive il risultato sulla riga che c'e' gia',
senza doppioni e senza travasi. La colonna `athlete_races.entry_time`
(`time`, nulla ammessa) e' stata aggiunta per questo; un indice unico
parziale `ux_athlete_races_attive` su `(race_id, athlete_id)` dove
`is_deleted = FALSE` impedisce a database la doppia iscrizione alla stessa
gara.

Il tempo d'iscrizione si scrive **mm:ss.dd** (`01:12.35`); sotto il minuto
basta `29.45` e la virgola al posto del punto e' accettata. Si puo' anche
lasciare vuoto. Il formato lo controlla `crud.tempo_da_testo`, lo stesso di
Inserisci tempi.

### Il personale, gia' nel campo

Il miglior tempo dell'atleta sulla stessa specialita' **e nella stessa
vasca** finisce dritto nel campo del tempo d'iscrizione, modificabile. Chi
non tocca niente si iscrive col suo personale; chi svuota il campo lo
stesso, perche' al salvataggio il personale torna come valore di ripiego
(lo fa `crud.salva_iscrizioni`, non solo l'interfaccia). Senza personale il
campo resta vuoto e l'iscrizione parte senza tempo.

Il personale e' solo delle prove individuali gia' nuotate, con la vasca
giusta: un 50 stile in vasca da 25 non dice niente su un 50 stile in vasca
da 50, e il `LEFT JOIN LATERAL` della query filtra su `r2.pool_length =
r.pool_length`. Accanto al nome della gara resta scritto come promemoria.

### Il limite di gare individuali

Arriva da `competitions.max_races_per_athlete`, niente numeri fissi nel
codice, ed e' **un blocco, non un avviso**: raggiunto il massimo, le gare
non ancora scelte si spengono e per cambiarne una bisogna prima toglierne
un'altra. Per questo l'elenco non e' una griglia editabile ma una casella
per gara: una cella di `st.data_editor` non si puo' disabilitare da sola.
La stessa regola e' ricontrollata lato server prima di scrivere.

**Le staffette non contano**: si riconoscono da `race_events.is_relay`, non
dal nome della gara. Se il limite e' nullo o zero vuol dire che non e'
stato dichiarato e non si limita niente, scritto in chiaro nella testata.

La data di chiusura sta in una pastiglia dorata sotto la testata, con i
giorni che mancano: e' l'unica data che fa perdere la gara.

### L'ordine delle gare individuali

Le gare individuali sono raggruppate per **giornata e fascia oraria**,
nell'ordine in cui si nuotano, con un'intestazione per blocco: *Mattino*,
*Pomeriggio*, *Sera*, e con il giorno davanti quando la manifestazione dura
piu' di una giornata. L'informazione viene dal programma della
manifestazione (vedi Anagrafica manifestazioni, Il programma); le gare per
cui non e' stato compilato finiscono in un blocco finale "Orario non
indicato", e se non e' compilato per nessuna l'elenco resta piatto come
prima. Le staffette hanno un elenco loro, raggruppato allo stesso modo: i
blocchi si calcolano sulle sole staffette, quindi le fasce sono le loro.

### Staffette

Sono gare a parte e stanno in un elenco loro: l'atleta da' solo la
**disponibilita'**, senza tempo d'iscrizione, perche' squadre e frazioni le
decide l'allenatore. Restano fuori dal limite delle individuali.

### Modifica, cancellazione e permessi

Finche' la finestra e' aperta l'atleta cambia i tempi, aggiunge e toglie
gare; la cancellazione e' la solita soft delete. Una gara che ha gia' il
**tempo di gara** non si puo' togliere da qui: l'app lo dice e manda
dall'amministratore. A finestra chiusa resta l'elenco **Le mie iscrizioni**,
in sola lettura.

Il salvataggio **rilegge lo stato a database un attimo prima di scrivere**,
senza passare dal cache: fra il momento in cui la pagina ha caricato le gare
e il momento in cui si conferma puo' essere entrata una riga da un'altra
scheda del browser, da un altro dispositivo o da Inserisci tempi. Su quella
rilettura si decide gara per gara: niente a database si inserisce, riga
attiva si aggiorna il tempo, riga tolta prima si rimette in piedi quella
invece di crearne una seconda. L'inserimento porta anche un `ON CONFLICT`
sull'indice unico, che fa da rete se la riga nasce proprio in quell'istante:
aggiorna il tempo invece di fallire. E se qualcosa va storto a database
l'atleta vede un messaggio, non un traceback.

L'id dell'atleta arriva da `auth.current_user()`, cioe' dalla sessione
creata al login, mai da un widget o dall'indirizzo; prima di modificare o
cancellare una riga, `crud` ricontrolla a database che sia davvero sua. Un
allenatore senza scheda atleta non vede la pagina: non ha gare da nuotare.

---

## Gestione > Iscrizioni gare

I numeri dei riquadri dell'indice Gestione arrivano da una query sola
(`GESTIONE_CONTEGGI_SQL`): prima erano quattro letture separate e le schede
comparivano a scaglioni, una per ogni risposta del database.

Primo widget di Gestione, aperto ad **allenatori e amministratore**
(`auth.is_staff()`), mentre anagrafiche, tempi e registro accessi restano
dell'amministratore. Nel menu ci sono **solo le manifestazioni dalla data
di oggi in avanti**: le iscrizioni di una gara passata non servono piu' a
organizzare niente, e per i risultati c'e' Inserisci tempi. Si sceglie la
manifestazione e si vede chi si e' iscritto. In cima tre numeri (atleti,
gare individuali, frazioni di staffetta), un avviso per chi ha superato il
limite di gare, filtro per tipo di gara e ricerca libera.

La tabella ha sei colonne, quelle che servono a bordo vasca: **Atleta,
Gara, Tempo iscrizione, Giornata, Fascia, N.** Le righe seguono **l'ordine
del programma** (giornata, fascia, numero) e dentro vanno per cognome: si
legge scorrendo le gare come si nuotano. Le gare per cui il programma non e'
stato compilato finiscono in fondo con i trattini. Il tipo di gara e la
vasca non ci sono piu' come colonne: il tipo e' nel filtro qui sopra e la
vasca e' della manifestazione, non della singola riga.

Il bottone **Scarica le iscrizioni in Excel** produce un `.xlsx` con le
righe mostrate, filtri compresi, e le stesse colonne della tabella piu' il
nome della manifestazione davanti: **Manifestazione, Atleta, Gara, Tempo
iscrizione, Giornata, Fascia, N.** I tempi nel foglio sono tutti in
`mm:ss.dd` e la giornata e' testo `gg/mm/aaaa`, cosi' le colonne si ordinano
senza dipendere dalle impostazioni locali di Excel; il numero di programma
invece e' un intero vero. La prima riga e' bloccata e le larghezze sono
calcolate sul contenuto. Il file si costruisce in memoria con
`pandas.ExcelWriter` e `openpyxl` (unica dipendenza aggiunta,
`openpyxl==3.1.5` in `requirements.txt`).

Qui dentro non si scrive niente: le correzioni passano da Inserisci tempi o
dall'atleta, finche' la finestra e' aperta.

---

## Registro accessi

Ogni accesso, uscita e tentativo fallito finisce nella tabella `access_log`
a database. Funziona ovunque giri l'app, in locale come su Streamlit Cloud,
e si interroga con una SELECT come tutto il resto.

```sql
CREATE TABLE access_log (
    id                     serial PRIMARY KEY,
    creation_utc_date_time timestamp NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
    creation_user_id       integer NOT NULL,
    event_type             varchar(20) NOT NULL,   -- ACCESSO, USCITA, FALLITO, SVUOTATO
    athlete_id             integer,
    full_name              varchar(200),
    fin_code               integer,
    user_role              varchar(20),
    via                    varchar(20),            -- code, oidc, token
    note                   varchar(300)
);
CREATE INDEX ix_access_log_when ON access_log (creation_utc_date_time DESC);
```

Segue le convenzioni dello schema (id seriale, ora in UTC, `creation_user_id`
per l'audit) con due scelte diverse dal resto: niente `is_deleted`, perche'
un registro si svuota e non si disattiva, e nessuna foreign key su
`athlete_id`, perche' un log deve sopravvivere anche a una riga di anagrafica
che sparisce. Le date si scrivono in UTC e si rileggono in ora italiana
direttamente in SQL, con `AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Rome'`.

`via` dice come si e' entrati: `code` col codice FIN, `oidc` col provider,
`token` quando la sessione e' stata ripresa dal "resta connesso". Dei
tentativi falliti si registra il codice FIN provato, mai la data di nascita.
La scrittura non solleva mai eccezioni: se il database non risponde, o la
tabella non c'e' ancora, si entra lo stesso e semplicemente non si registra.

La pagina **Registro accessi** in Gestione, riservata all'amministratore,
mostra le ultime 500 righe con filtro per tipo di evento e ricerca libera su
nome, codice FIN e note, piu' tre contatori in cima. Due bottoni: *Scarica
LOG* esporta in txt quello che e' a video, con intestazione e data di
esportazione, e *Cancella* svuota la tabella dopo una conferma esplicita.
Quella cancellazione e' fisica, non una disattivazione: l'unica riga che
resta e' quella che registra lo svuotamento, con chi l'ha fatto e quante
righe ha tolto.

Le letture del registro non passano dal cache: chi apre quella pagina vuole
vedere l'ultimo accesso, non quello di un'ora fa.

### In alternativa, un file di testo

Resta possibile scrivere le stesse righe anche su file, mettendo il percorso
in `[app]`:

```toml
access_log_file = "G:/Il mio Drive/Job/ranazzurra/accessi.txt"
```

Le due cose convivono: il database sempre, il file in piu' quando c'e' la
chiave. Attenzione pero' a dove gira l'app, perche' il file lo scrive il
processo Python: su Drive ci arriva solo se l'app gira su un computer dove
Drive e' montato. Su Streamlit Cloud il filesystem e' quello di un container
effimero, il file riparte da zero a ogni riavvio e sul Drive non arriva mai.
Per quello c'e' la tabella.

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

Cerca e Gestione sono pagine-indice: la prima porta ad Atleta, Classifiche e
Manifestazioni, la seconda alle due anagrafiche e al registro accessi. La
voce della barra resta accesa anche quando sei in una sottopagina.

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

Lo stesso trucco del `flex-wrap: nowrap` serve in **Agenda**, dove la
scheda della manifestazione e il bottone Iscriviti devono restare affiancati
anche sul telefono: le due colonne stanno dentro `st.container(key="riga_…")`
e il CSS lascia alla scheda lo spazio che avanza mentre il bottone tiene i
suoi 104px. Senza, sotto i 640px il bottone finisce sotto la scheda.

---

## Versione e novità

Il numero di versione sta in **`version.py`** (`VERSIONE` e
`DATA_RILASCIO`): e' codice, viaggia con il commit, quindi quello che si
legge a video e' sempre quello che gira davvero. Le novita' stanno in
**`CHANGELOG.md`** accanto, scritte a mano a ogni rilascio e in italiano
corrente, perche' le leggono gli atleti e non gli sviluppatori. Tre numeri:
il primo cambia quando cambia il modo di usare l'app, il secondo per una
funzione nuova, il terzo per le correzioni.

La pagina **Novita'** (`views/novita.py`, url `/novita`) e' aperta a tutti e
mostra il changelog cosi' com'e'. Ci si arriva da un collegamento fisso in
fondo al **Profilo**, sopra la riga con la versione in uso: niente avvisi a
comparsa dopo un rilascio, chi vuole sapere cosa e' cambiato sa dove
guardare. Il numero di versione in chiaro serve anche a noi, perche' quando
un atleta segnala un problema si sa subito con che versione.

`version.novita()` ritaglia dal changelog il blocco di una sola versione, se
serve mostrare solo le ultime novita' invece di tutta la storia.

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

Delle concluse si mostrano le ultime cinque, le altre si trovano
restringendo il periodo o con la ricerca.

**In programma guarda 75 giorni avanti** (`ORIZZONTE` in `views/agenda.py`).
Oltre quella soglia le manifestazioni restano a database ma non affollano la
lista: a sei mesi di distanza non c'e' niente da decidere. La soglia e' 75 e
non meno perche' deve coprire l'apertura delle iscrizioni, che sulle gare a
calendario parte fra i 50 e i 65 giorni prima della gara (30 giorni di
anticipo sull'apertura ufficiale): piu' stretta, e il bottone Iscriviti
sparirebbe proprio nei giorni in cui serve.

Due eccezioni. La ricerca per nome scavalca la finestra, perche' chi scrive
"Belluno" vuole trovare quella gara, non sentirsi dire che non c'e'. E una
manifestazione gia' aperta alle iscrizioni resta in elenco anche se e' piu'
in la': con 75 giorni oggi non capita mai, ma e' la rete che tiene se un
domani una gara apre le adesioni con piu' anticipo. Il controllo e' lo
stesso di `_stato_iscrizioni`, quello che decide se il bottone e'
cliccabile, cosi' le due cose non possono divergere.

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
nome, cognome, sesso, data di nascita, e-mail, i due ruoli, la **scadenza
del certificato medico** e lo stato **Attivo**.

### La tabella si modifica direttamente

L'elenco e' un `st.data_editor`: si scrive nelle celle e si preme **Salva le
modifiche**. Tutto e' modificabile tranne ID e numero di gare; per
aggiungere qualcuno resta ＋ Nuovo atleta, e il form Modifica resta per chi
preferisce un atleta per volta. Il ruolo, che prima era una colonna sola
calcolata, e' tornato alle sue due spunte, **Atleta** e **Staff**, perche'
in griglia si devono poter cambiare separatamente.

**O passa tutto o non passa niente.** `crud.salva_anagrafica` valida prima
l'intero lotto e solo dopo comincia a scrivere: su 270 righe, salvarne meta'
e fermarsi su un errore lascerebbe l'anagrafica in uno stato che nessuno sa
piu' ricostruire. I controlli sono quelli del form (nome e cognome
obbligatori, e-mail formalmente valida, data di nascita non nel futuro,
almeno un ruolo, chi e' solo staff deve avere l'e-mail), piu' uno che il
form non puo' avere: **il codice FIN duplicato dentro la griglia stessa**.
`crud.valida` cerca i doppioni a database e non vede le altre righe in
modifica, quindi due atleti a cui si da' lo stesso numero nello stesso
salvataggio passerebbero il controllo. Gli errori escono con nome e cognome
davanti, non con il numero di riga.

Vengono riscritte solo le righe davvero cambiate, confrontate campo per
campo con quelle a database: un salvataggio a vuoto non tocca niente e lo
dice. Lo stato Attivo non passa da `aggiorna_atleta` ma dalle sue funzioni
di soft delete, come nel form.

Una cosa da sapere e' scritta anche sopra la tabella: **salvare prima di
cambiare filtro o ordinamento**. `st.data_editor` tiene le celle toccate per
posizione di riga, non per contenuto, quindi la chiave del widget porta
dentro l'impronta degli id mostrati: cambiando le righe cambia la chiave e
le modifiche in sospeso si perdono invece di finire sulla persona sbagliata.

### Atleta, allenatore o tutti e due

Nel form ci sono due spunte che decidono cosa e' quella persona. **Atleta**
la fa comparire nei selettori, nelle classifiche e nei conteggi, ed e'
spuntata di default. **Allenatore o staff** le da' il ruolo di allenatore e
le permette di entrare nell'app. Le combinazioni valide sono tre: solo
atleta, il caso normale; solo allenatore, e allora l'e-mail diventa
obbligatoria perche' e' l'unico modo che ha per entrare; tutti e due, per
l'allenatore che gareggia anche lui, che resta visibile ovunque come
qualsiasi altro atleta. Nessuna delle due spuntate non si salva.

A database sono due colonne aggiunte ad `athletes`, `is_athlete` con default
`true` e `is_staff` con default `false`, quindi le 268 righe gia' presenti
continuano a comportarsi esattamente come prima. L'elenco ha un filtro per
ruolo e una colonna che dice chi e' cosa.

### Attivo, nel form

La spunta **Attivo** si cambia direttamente nel form, in creazione e in
modifica, e non solo con i pulsanti dell'elenco. Un atleta nuovo nasce
attivo; togliendo la spunta nasce gia' inattivo, utile per caricare qualcuno
che per questa stagione non c'e'. In modifica, se la spunta cambia, il
salvataggio chiama le stesse funzioni di sempre
(`crud.imposta_stato_atleta`, che gira su `disattiva_atleta` e
`riattiva_atleta`) cosi' i campi di cancellazione restano scritti come si
deve, e il messaggio dice cosa e' successo.

Disattivare non cancella niente: gare, tempi, iscrizioni e storico restano
a database. L'atleta sparisce dagli elenchi correnti e dai selettori, ma le
classifiche storiche continuano a mostrarlo, e **l'import dei risultati non
guarda lo stato**: un risultato vecchio di chi ha smesso si carica lo
stesso.

### Certificato medico

`athletes.medical_certificate_expiry` (`date`, nulla ammessa) tiene la
scadenza. Nel form e' un campo data facoltativo in formato `gg/mm/aaaa`:
svuotandolo torna non registrata (`NULL`), e nell'elenco c'e' la colonna
**Certificato**. L'atleta la vede nel suo **Profilo** e non puo' cambiarla:
la legge una query mirata sul suo solo id. Il giorno della scadenza vale
ancora. Nessun blocco automatico sulle iscrizioni: il certificato si
registra e si guarda, non impedisce niente finche' non lo si chiede
esplicitamente.

**Il semaforo.** Nell'elenco la prima colonna porta un pallino: 🔴 se il
certificato e' scaduto, 🟡 se scade entro 60 giorni (`GIORNI_PREAVVISO`),
🟢 se e' in regola; accanto al bottone di salvataggio una riga dice quanti
sono i primi due. Vale solo per chi e' in una categoria master, cioe'
**M20/F20 e oltre**: sotto i venti anni la FIN non assegna categoria e il
certificato lo segue la societa' con regole sue, quindi segnalare quelle
righe sarebbe un falso allarme. Chi non ha la data registrata resta senza
pallino: non e' una scadenza vicina, e' un dato che manca, e si vede dalla
cella vuota.

Era la riga intera colorata, con uno Styler. E' diventato un pallino quando
la tabella e' passata a `st.data_editor`, che uno Styler non lo accetta: o
si colora o si scrive, e poter correggere venti scadenze in griglia vale piu'
del fondo colorato.

Nel **Profilo** la stessa scala a tre colori sul riquadro del certificato:
verde in corso di validita', giallo da 60 giorni alla scadenza (con i giorni
che mancano, "Scade oggi", "Scade domani"), rosso scaduto con da quanto, e
grigio quando la data non c'e'.

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

Sotto alle azioni c'e' il riquadro **Accesso all'app**: stato della password
dell'atleta selezionato, data dell'ultimo accesso e i tre bottoni per
azzerare la password, generare una temporanea o sospendere l'accesso. Chi non
ha un'e-mail in anagrafica non puo' entrare, e il riquadro lo dice.

## Anagrafica manifestazioni

Stesso schema dell'anagrafica atleti, riservata all'amministratore. Campi:
nome (`competitions.type`), date di inizio e fine, apertura e chiusura
iscrizioni, cronometraggio (tendina con i valori gia' presenti a database),
massimo gare per atleta, **organizzatore**, link al sito e al PDF, spunta
**Manifestazione ufficiale FIN** (vedi la sezione Gare ufficiali FIN). Filtri
per stato, per passato/futuro e ricerca sul nome; nell'elenco la colonna FIN
dice a colpo d'occhio quali sono le ufficiali. Accanto a **Nuova** c'e'
**Clona**, che riparte da un'edizione passata portandosi dietro il programma
gare.

Anche qui "Elimina" e' una soft delete: `is_deleted = TRUE`. La
manifestazione sparisce da agenda, schede e classifiche, ma le gare e i
risultati collegati restano a database e tornano appena la riattivi. Il form
controlla che la fine non preceda l'inizio, che le iscrizioni non chiudano
dopo la partenza e che i link comincino per http.

### Le gare dentro la manifestazione

Aprendo **Modifica** di una manifestazione, sotto al form compare la sezione
**Gare**: elenco con nome, specialita', vasca, iscritti e quanti hanno un
tempo, piu' i bottoni per crearne una, modificarla, eliminarla e saltare
dritti a Inserisci tempi con la gara gia' scelta. Sta fuori dal `st.form`
apposta: dentro un form i bottoni non fanno rerun finche' non si invia, e
qui invece ogni azione deve rispondere subito.

Una gara (`races`) e' una specialita' nuotata in una manifestazione in una
certa vasca: `race_event_id` (stile + distanza + staffetta), `pool_length`,
`competition_id` e un `name` libero. Il form propone **solo le 32
combinazioni gia' a database** e non ne crea di nuove, cosi' non nascono
doppioni e le query che raggruppano per specialita' restano pulite. Il nome
segue il formato delle 2.876 gare gia' presenti, "50 Dorso - Assoluti
Maschi": lasciandolo vuoto prende quello della specialita'. La stessa
specialita' puo' ripetersi nella stessa manifestazione, ed e' normale:
maschi e femmine sono due gare distinte, oggi sono 628 le combinazioni che
si ripetono.

Una cosa dello schema da ricordare: `races` non ha le colonne di ultima
modifica (ci sono solo `creation_*` e `deletion_user_id`), quindi chi
rinomina o sposta una gara non viene tracciato. Metterci
`last_modification_user_id` sarebbe una modifica di schema a parte.

**Eliminare una gara con dei tempi dentro non si puo'.** L'app dice quanti
sono e manda a Inserisci tempi: cancellare la gara porterebbe via dieci
risultati in un colpo solo senza che si veda. Sulla gara vuota la soft
delete e' quella di sempre.

### Il programma: giornate, fasce e ordine

Le gare di una manifestazione si susseguono per giornata e per fascia
oraria. In una giornata ci possono essere solo il mattino, solo il
pomeriggio, mattino e pomeriggio oppure pomeriggio e sera, e la
manifestazione puo' durare un giorno solo (`start_date = end_date`) o
diversi. A database sono tre colonne su `races`, tutte nullable:
`race_date` (la giornata), `session` (1 mattino, 2 pomeriggio, 3 sera, con
un CHECK che lo tiene fra 1 e 3) e `race_order` (il numero di programma
dentro la fascia, CHECK maggiore di zero).

Si compilano dal riquadro **Programma: giornate, fasce e ordine**, dentro
Modifica manifestazione sotto l'elenco delle gare: una griglia con tutte le
gare e tre colonne editabili, si sistema il programma e si salva in un colpo
solo. Il salvataggio tocca solo quelle tre colonne, quindi non puo' rovinare
nome, vasca o specialita'; le giornate fuori dalle date della manifestazione
vengono rifiutate prima di scrivere, e il controllo sta nell'app perche' un
CHECK su due tabelle vorrebbe un trigger. Il form della singola gara non li
mostra ma se li ricopia: salvando il nome di una gara il suo posto nel
programma resta dov'era.

**Lo storico resta vuoto e va benissimo cosi'.** Tutte le 2.964 gare gia' a
database hanno le tre colonne nulle: negli elenchi finiscono in fondo, sotto
l'intestazione "Orario non indicato", e se nessuna gara della manifestazione
ha il programma non compare nessuna intestazione, l'elenco e' identico a
prima. Non sono state dedotte da niente: a database non c'era nessun orario,
l'unica traccia sarebbe stato l'id di inserimento, e sarebbe stata
un'invenzione presentata come dato.

Dove si vede: nelle **Nuove iscrizioni**, dove le gare individuali sono
raggruppate per giornata e fascia nell'ordine in cui si nuotano, e in
**Cerca > Manifestazioni**. La data compare nell'intestazione solo se le
giornate sono piu' di una. Clonando una manifestazione fascia e ordine si
copiano, la giornata no: le date cambiano e si rimettono dal Programma.

### Clona

Il bottone **⧉ Clona**, accanto a Nuova, ricopia un'edizione passata con il
suo programma gare: quasi sempre e' quella dell'anno scorso, per cui la
manifestazione da cui partire si sceglie dentro la pagina di clonazione e non
dall'elenco, che con i filtri attivi potrebbe non averla nemmeno a video.

Dalla sorgente arrivano nome, cronometraggio, massimo gare per atleta,
organizzatore e la spunta FIN; le quattro date arrivano **spostate di un
anno** (il 29 febbraio diventa il 28) e sono tutte correggibili prima di
salvare. I due link restano vuoti apposta: quelli dell'edizione vecchia
puntano a un programma che non vale piu'.

Il programma gare e' una tabella editabile con quattro colonne: **Copia**,
che si toglie alle gare che quest'anno non si fanno, **Gara**, **Vasca** e
**Specialita'**. Le gare senza nome proprio arrivano con il nome della
specialita'. Se una riga spuntata resta senza nome, senza specialita' o con
una vasca diversa da 25 e 50, l'app lo dice e non salva niente: meglio
fermarsi che creare una manifestazione mezza vuota.

**Si copia solo la struttura, mai i risultati.** I tempi restano attaccati
all'edizione in cui sono stati nuotati: la copia nasce con le sue gare e
zero iscritti. Alla fine il messaggio dice da dove si e' partiti, qual e'
l'ID nuovo e quante gare sono state create.

### Organizzatore

`competitions.organizer_company_id` punta a `companies` ed e' nullable: buona
parte dello storico ce l'ha davvero vuoto, quindi la tendina ha lo zero che
fa da "—", non indicato. Se la societa' agganciata non e' piu' nell'elenco,
perche' disattivata o senza nome, resta comunque in tendina marcata **fuori
elenco**, cosi' salvando la manifestazione non si perde un riferimento buono.
Il nome finisce nell'elenco dell'anagrafica, in Agenda sotto il nome della
manifestazione e nella testata dei risultati.

---

## Inserisci tempi

Terza voce di Gestione, fra Anagrafica manifestazioni e Registro accessi
(`views/tempi.py`, url `/inserisci-tempi`), riservata all'amministratore. Si
sceglie la manifestazione, poi la gara, e sotto compare una griglia con gli
iscritti: atleta, tempo, punti FIN e categoria. Si modifica come un foglio
di calcolo, si aggiungono righe in fondo, si tolgono con il cestino, e un
bottone solo scrive tutto. Arrivando dal bottone della sezione Gare la
manifestazione e la gara sono gia' selezionate.

Perche' una griglia e non un form riga per riga: una gara sono dieci o
quindici atleti presi da un PDF, e fare dieci salvataggi separati sarebbe
una pena. La chiave del `data_editor` porta dentro il `race_id`, cosi'
cambiando gara Streamlit riparte da zero invece di applicare alla gara
sbagliata le modifiche rimaste in sospeso.

**Il formato del tempo** e' quello che si scrive di getto: `29.45`,
`1:02.35`, `1:01:02.35`, con la virgola al posto del punto se capita.
Lasciarlo vuoto e' una scelta legittima e vuol dire iscritto senza tempo,
non partito, ritirato o squalificato: a database esistono gia' 136 righe
cosi'. I punti FIN si scrivono a mano, non li calcola nessuno: sono quelli
dei risultati ufficiali. La categoria e' il campo `"group"`, libero e quasi
sempre vuoto (7.441 righe su 7.642); nei dati vecchi contiene la societa' e
il gruppo di batteria, non la categoria master, quindi l'app non ci mette
niente di suo.

**Prima si controlla tutto, poi si scrive.** Se una riga e' sbagliata (tempo
illeggibile, atleta mancante, stesso atleta due volte nella stessa gara) non
parte nessuna query e la griglia resta come l'hai lasciata: meglio zero
scritture che restare a meta' strada. Il salvataggio confronta la griglia
con quello che c'era prima e fa solo il necessario: `INSERT` per le righe
nuove, `UPDATE` per quelle cambiate davvero, `is_deleted = TRUE` per quelle
tolte. Le righe identiche non vengono riscritte.

Nel menu atleti ci sono i tesserati attivi, piu' quelli gia' iscritti a
quella gara anche se nel frattempo sono stati disattivati: se no la loro
riga resterebbe senza etichetta e il salvataggio li butterebbe fuori. Per le
staffette serve una riga per frazionista, tutte con il tempo della squadra,
che e' esattamente come stanno a database le 873 righe di staffetta gia'
presenti.

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

Il calendario del `date_input` e' l'angolo piu' ostico del tema chiaro.
BaseWeb lo disegna con i colori scuri di `config.toml` e alcuni pezzi non si
raggiungono con i selettori normali: le caselle vuote della prima settimana
restavano un rettangolo nero anche forzando il fondo bianco sulle celle,
perche' il nero arrivava da uno pseudo-elemento. La cura e' brutale ma
funziona: bianco su tutto il calendario, `*::before` e `*::after` compresi, e
poi il giorno scelto ridisegnato a mano (e' l'unico con `tabindex="0"`).

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
