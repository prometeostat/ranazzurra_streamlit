# Report preliminare import PDF 2007

Quattro riepiloghi natatoria/Siteland della stagione 2007. Nessuna scrittura eseguita.

## 0. Una novita' di formato che avrebbe fatto danni

Il riepilogo di **Belluno 2007 e a cronometraggio automatico** (`Cron: A` invece di `Cron: M`) e
i tempi hanno **due decimali** invece di uno: `02:06.60`, `00:26.20`, `01:08.70`. Il parser usato
fino a ieri accettava un solo decimale e sul primo giro ha scartato **207 righe su un documento
solo**, tenendone 5 su 30 di Ranazzurra. Corretto: la regex del tempo ora accetta uno o due
decimali, e lo stesso vale per i parziali di staffetta fra parentesi.

Il controllo che ha fatto scattare l'allarme e sempre quello: numero di righe contenenti
"RANAZZURRA" nel testo grezzo contro righe ricostruite. Dopo la correzione i quattro documenti
tornano esatti, zero righe non interpretate.

## 1. Manifestazioni: una da creare, tre gia a DB

| PDF | data | sede | vasca | cron | fogli | gare | competition |
|---|---|---|---|---|---|---|---|
| sdona_2007 | 2007-01-20 | San Donà di Piave | 25 m | M | 8 | 6 | **1218** |
| belluno_2007 | 2007-05-20 | Belluno | 25 m | A | 9 | 8 | **1219** |
| spresiano_2007 | 2007-06-23 | Spresiano | 50 m | M | 10 | 10 | **da creare** |
| valdobbiadene_2007 | 2007-12-02 | Valdobbiadene | 25 m | M | 9 | 8 | **1221** |

Le tre esistenti sono di nuovo le competitions costruite dallo scraper FIN Veneto sulla carriera di
VEDOVELLI DANILA, stavolta con **due gare ciascuna**. Ho verificato tutti e sei i suoi tempi e
coincidono col PDF:

| competition | data | gara | a DB | nel PDF | pos |
|---|---|---|---|---|---|
| 1218 | 2007-01-20 | 50 SL | 00:45.7 | 00:45.7 | 42 |
| 1218 | 2007-01-20 | 100 Rana | 02:13.1 | 02:13.1 | 21 |
| 1219 | 2007-05-20 | 200 SL | 03:43.8 | 03:43.80 | 17 |
| 1219 | 2007-05-20 | 50 SL | 00:45.4 | 00:45.40 | 29 |
| 1221 | 2007-12-02 | 50 SL | 00:48.8 | 00:48.8 | 30 |
| 1221 | 2007-12-02 | 400 SL | 08:19.9 | 08:19.9 | 9 |

La 1219 ha gia `timing = AUTOMATICO`, coerente col `Cron: A` del PDF: non la tocco.

Sulle altre date ci sono manifestazioni diverse, controllate come sempre oltre la data: il
20/05/2007 c'e anche la competition 1020 (TONON SABRINA, web_id 1547 diverso) e il 02/12/2007 la
1027 (TONON SABRINA, web_id 1666). Entrambe altre gare, le lascio stare.

### Titoli proposti

| competition | titolo nel PDF | titolo proposto |
|---|---|---|
| 1218 | 2^ giornata circuito attività masters | 2ª Giornata Circuito Attività Masters - San Donà di Piave |
| 1219 | ASD NUOTO BELLUNO | Trofeo Master ASD Nuoto Belluno - Belluno |
| da creare | Finale Masters 2007 Circuito Sinistra Piave | Finale Masters 2007 Circuito Sinistra Piave - Spresiano |
| 1221 | 1^ Giornata Circuito Master | 1ª Giornata Circuito Master 2007/08 - Valdobbiadene |

Due cose su cui voglio il tuo parere.

**Belluno 2007**: il PDF non porta il nome della manifestazione, in testa a ogni foglio c'e solo
`ASD NUOTO BELLUNO`, cioe la societa organizzatrice. Nel 2006 la stessa gara a DB si chiama
"7° Trofeo Città di Belluno" (competition 29) e nel 2004 era il "5° Trofeo Master". Se la serie e
la stessa, questa sarebbe l'**8° Trofeo Città di Belluno**, ma il documento non lo dice e non me lo
invento: o confermi tu, o metto il titolo neutro proposto qui sopra.

**Valdobbiadene**: la giornata del 02/12/2007 apre la stagione 2007/08, esattamente come quella del
03/12/2006 apriva la 2006/07. Se le chiamo tutte e due "1ª Giornata Circuito Master - Valdobbiadene"
diventano indistinguibili nell'elenco. Propongo di mettere la stagione nel titolo della nuova, e se
vuoi allineo anche la 1217 del 2006 a "1ª Giornata Circuito Master 2006/07 - Valdobbiadene".

## 2. Anagrafica: 49 su 57 gia presenti

Nei quattro PDF ci sono **57 atleti Ranazzurra distinti**, 49 gia in anagrafica e 8 da censire. Zero ambigui, e il controllo di somiglianza sui nuovi contro tutta l'anagrafica non trova nessun caso sopra la soglia.

### Da censire (8)

| cognome nome | anno | sesso | gare | manifestazioni |
|---|---|---|---|---|
| ZANETTI LORENZO | 1982 | M | 3 | 2 |
| GHIRARDO VALENTINA | 1987 | F | 2 | 2 |
| GIRARDI GEMMA | 1949 | F | 2 | 1 |
| SILVESTRIN STEFANO | 1985 | M | 2 | 1 |
| DAL CIN WALTER | 1983 | M | 1 | 1 |
| DAVANZO WALTER | 1962 | M | 1 | 1 |
| TOPAN MAURO | 1982 | M | 1 | 1 |
| ZULIANI CRISTINA | 1974 | F | 1 | 1 |

Da tenere separati: GHIRARDO VALENTINA (1987) non e GHIRARDO LETIZIA (id 192, 1984), DAVANZO WALTER
(1962) non e DAVANZO GESSICA (id 188, 1985), GIRARDI GEMMA (1949) non e GIRARDI ERMES (id 134, 1961)
ne DOPPIERI GEMMA (id 125).

Segnalo una cosa che fa piacere: **TALAMINI PAOLO** (id 155), che era in anagrafica dal 2003 senza
nemmeno un risultato perche' nei PDF compariva solo come assente, qui finalmente gareggia. Ha un
RIT sui 200 stile a Belluno e tre gare regolari.

## 3. Le staffette di Belluno non portano risultati

Il riepilogo di Belluno ha due fogli di **staffetta 4x50 stile libero**, maschile e femminile, ed e
la prima volta che ne compaiono nello storico. Sono pero' **tutte quante marcate ASS**: cinque squadre
iscritte fra i maschi e quattro fra le femmine, nessun tempo e nessuna posizione. La gara e stata
annunciata ma non disputata. Non c'e niente da importare e non creo le due races.

## 4. Risultati

| manifestazione | righe | ASS | gia a DB | da inserire | gare da creare |
|---|---|---|---|---|---|
| sdona_2007 | 64 | 4 | 2 | 58 | 4 |
| belluno_2007 | 29 | 3 | 2 | 24 | 4 |
| spresiano_2007 | 25 | 0 | 0 | 25 | 8 |
| valdobbiadene_2007 | 47 | 0 | 2 | 45 | 6 |
| **totale** | **165** | **7** | **6** | **152** | **22** |

Due righe SQU (MENIS ALESSANDRO sui 50 stile a San Donà, BETTIOL GIULIA sui 50 dorso a
Valdobbiadene) e due RIT (TALAMINI PAOLO sui 200 stile a Belluno, GRANZIERA SERENA sui 400 stile a
Valdobbiadene): tutte e quattro gare disputate, da inserire con `final_time` NULL.

Nessun tempo anomalo: il piu lento per distanza e sempre plausibile, il caso limite e il 50 stile in
01:00.1 di GIRARDI GEMMA, che ha 58 anni.

## 5. Dettaglio dei risultati da inserire


### sdona_2007 — 2007-01-20, San Donà di Piave, vasca 25

**50 Dorso — Assoluti Femmine Master** — race da creare, race_event 17

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 1 | LAZZARIN CRISTINA | 1984 | 00:36.2 | 138 |
| 9 | BARAZZA CLAUDIA | 1965 | 00:39.6 | 111 |
| 12 | BETTIOL GIULIA | 1985 | 00:42.2 | 115 |
| 19 | SALVALAGGIO CATIA | 1964 | 00:50.6 | 199 |
| 22 | SCHIEVENE FEDERICA | 1976 | 00:52.6 | 201 |
| 24 | DAVANZO GESSICA | 1985 | 00:53.2 | 188 |
| 31 | GIRARDI GEMMA | 1949 | 01:02.8 | nuovo |

**50 Dorso — Assoluti Maschi Master** — race da creare, race_event 17

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 1 | DA ROS GABRIELE | 1983 | 00:31.5 | 187 |
| 2 | BARRO PAOLO | 1980 | 00:31.6 | 112 |
| 3 | FONTANA NICO | 1979 | 00:31.8 | 61 |
| 4 | FILIPPI FRANCESCO | 1980 | 00:31.9 | 60 |
| 8 | MENIS ALESSANDRO | 1973 | 00:38.2 | 195 |
| 10 | ANZANELLO STEFANO | 1975 | 00:39.8 | 109 |
| 26 | ZACCARIN ERMANNO | 1951 | 00:44.4 | 162 |

**50 Stile Libero — Assoluti Femmine Master** — race 17447 (esistente)

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 7 | LAZZARIN CRISTINA | 1984 | 00:31.8 | 138 |
| 9 | MILANESE STEFANIA | 1986 | 00:32.2 | 142 |
| 10 | BARAZZA CLAUDIA | 1965 | 00:33.1 | 111 |
| 13 | BETTIOL GIULIA | 1985 | 00:33.8 | 115 |
| 15 | ROSOLEN IRENE | 1984 | 00:34.9 | 151 |
| 29 | GHIRARDO LETIZIA | 1984 | 00:40.8 | 192 |
| 29 | SALVALAGGIO CATIA | 1964 | 00:40.8 | 199 |
| 32 | SCHIEVENE FEDERICA | 1976 | 00:41.4 | 201 |
| 43 | GEROMETTA LORETTA | 1951 | 00:46.1 | 132 |
| 46 | GIRARDI GEMMA | 1949 | 01:00.1 | nuovo |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 2 | BARRO PAOLO | 1980 | 00:26.2 | 112 |
| 3 | FONTANA NICO | 1979 | 00:26.4 | 61 |
| 6 | DA ROS GABRIELE | 1983 | 00:27.2 | 187 |
| 17 | FILIPPI FRANCESCO | 1980 | 00:29.2 | 60 |
| 18 | BLASI STEFANO | 1983 | 00:29.7 | 184 |
| 21 | GERARDO SIMONE | 1979 | 00:30.0 | 191 |
| 23 | ANDREON ALESSANDRO | 1970 | 00:30.1 | 108 |
| 28 | CHECCHIN MATTEO | 1986 | 00:30.6 | 120 |
| 28 | PINESE MASSIMO | 1977 | 00:30.6 | 146 |
| 33 | PAPA IVAN | 1974 | 00:31.5 | 196 |
| 33 | ANZANELLO STEFANO | 1975 | 00:31.5 | 109 |
| 46 | SARTORI EROS | 1981 | 00:33.2 | 200 |
| 52 | CAMPODALL'ORTO ANDREA | 1980 | 00:33.7 | 172 |
| 65 | PRADELLA GIANPAOLO | 1961 | 00:36.1 | 149 |
| 66 | ZACCARIN ERMANNO | 1951 | 00:36.6 | 162 |
| 71 | DE STEFANI PAOLO | 1970 | 00:38.4 | 189 |
| 73 | ZARAMELLA BRUNO | 1943 | 00:38.9 | 165 |
| 77 | TALAMINI PAOLO | 1962 | 00:40.4 | 155 |
| 78 | MASO ALESSANDRO | 1977 | 00:42.3 | 141 |
| 80 | FRARE MAURIZIO | 1966 | 00:59.5 | 129 |
| - | MENIS ALESSANDRO | 1973 | SQU | 195 |

**100 Rana — Assoluti Femmine Master** — race 17451 (esistente)

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 10 | ROSOLEN IRENE | 1984 | 01:40.0 | 151 |
| 13 | GHIRARDO LETIZIA | 1984 | 01:46.3 | 192 |
| 17 | GEROMETTA LORETTA | 1951 | 01:58.5 | 132 |

**100 Rana — Assoluti Maschi Master** — race da creare, race_event 21

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 3 | NAVE DANIELE | 1981 | 01:16.1 | 143 |
| 5 | CHECCHIN MATTEO | 1986 | 01:18.7 | 120 |
| 13 | BLASI STEFANO | 1983 | 01:28.2 | 184 |
| 14 | CALESSO GIORGIO | 1983 | 01:28.7 | 118 |
| 17 | PAPA IVAN | 1974 | 01:29.6 | 196 |
| 19 | CAMPODALL'ORTO ANDREA | 1980 | 01:31.3 | 172 |
| 24 | GERARDO SIMONE | 1979 | 01:33.0 | 191 |
| 25 | COZZUOL MATTEO | 1976 | 01:33.1 | 186 |
| 35 | RUI ALBERTO | 1982 | 01:37.4 | 198 |
| 56 | TALAMINI PAOLO | 1962 | 01:53.0 | 155 |


### belluno_2007 — 2007-05-20, Belluno, vasca 25

**50 Stile Libero — Assoluti Femmine Master** — race 17455 (esistente)

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 4 | MILANESE STEFANIA | 1986 | 00:32.10 | 142 |
| 19 | GHIRARDO LETIZIA | 1984 | 00:39.10 | 192 |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 12 | VECCHIATO SIMONE | 1976 | 00:28.80 | 160 |
| 17 | BAZZO FABIO | 1981 | 00:29.60 | 113 |
| 19 | MENIS ALESSANDRO | 1973 | 00:29.80 | 195 |
| 20 | ANDREON ALESSANDRO | 1970 | 00:29.90 | 108 |
| 42 | SEMENZATO DANIELE | 1978 | 00:36.50 | 202 |
| 47 | ZARAMELLA BRUNO | 1943 | 00:38.20 | 165 |
| 50 | TALAMINI PAOLO | 1962 | 00:40.60 | 155 |
| 52 | DAVANZO WALTER | 1962 | 00:40.80 | nuovo |

**100 Misti — Assoluti Femmine Master** — race da creare, race_event 1

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 2 | LAZZARIN CRISTINA | 1984 | 01:19.20 | 138 |
| 8 | MILANESE STEFANIA | 1986 | 01:26.20 | 142 |
| 21 | SALVALAGGIO CATIA | 1964 | 01:49.20 | 199 |

**100 Misti — Assoluti Maschi Master** — race da creare, race_event 1

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 3 | DA ROS GABRIELE | 1983 | 01:08.70 | 187 |
| 16 | BAZZO FABIO | 1981 | 01:17.90 | 113 |
| 19 | VECCHIATO SIMONE | 1976 | 01:19.90 | 160 |
| 23 | MENIS ALESSANDRO | 1973 | 01:23.60 | 195 |

**200 Stile Libero — Assoluti Femmine Master** — race 17453 (esistente)

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 2 | LAZZARIN CRISTINA | 1984 | 02:30.80 | 138 |
| 11 | GHIRARDO VALENTINA | 1987 | 03:16.00 | nuovo |
| 13 | SALVALAGGIO CATIA | 1964 | 03:25.80 | 199 |
| 15 | GHIRARDO LETIZIA | 1984 | 03:30.90 | 192 |

**200 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 9

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 14 | ANDREON ALESSANDRO | 1970 | 02:38.00 | 108 |
| 39 | ZARAMELLA BRUNO | 1943 | 03:39.50 | 165 |
| - | TALAMINI PAOLO | 1962 | RIT | 155 |


### spresiano_2007 — 2007-06-23, Spresiano, vasca 50

**50 Dorso — Assoluti Femmine Master** — race da creare, race_event 17

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 1 | LAZZARIN CRISTINA | 1984 | 00:34.6 | 138 |
| 4 | GHIRARDO VALENTINA | 1987 | 00:45.9 | nuovo |
| 8 | DAVANZO GESSICA | 1985 | 00:55.6 | 188 |

**50 Dorso — Assoluti Maschi Master** — race da creare, race_event 17

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 1 | FONTANA NICO | 1979 | 00:31.9 | 61 |

**50 Farfalla — Assoluti Maschi Master** — race da creare, race_event 23

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 1 | DA ROS GABRIELE | 1983 | 00:30.1 | 187 |
| 8 | BAZZO FABIO | 1981 | 00:34.5 | 113 |
| 13 | ZANETTI LORENZO | 1982 | 00:36.7 | nuovo |

**50 Rana — Assoluti Femmine Master** — race da creare, race_event 20

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 5 | ROSOLEN IRENE | 1984 | 00:46.2 | 151 |
| 6 | GHIRARDO LETIZIA | 1984 | 00:49.9 | 192 |

**50 Rana — Assoluti Maschi Master** — race da creare, race_event 20

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 1 | NAVE DANIELE | 1981 | 00:35.1 | 143 |
| 4 | CHECCHIN MATTEO | 1986 | 00:37.1 | 120 |
| 7 | BELLAGAMBA UMBERTO | 1963 | 00:40.8 | 114 |
| 10 | PINESE MASSIMO | 1977 | 00:42.7 | 146 |

**50 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 1 | BETTIOL GIULIA | 1985 | 00:32.1 | 115 |
| 1 | MILANESE STEFANIA | 1986 | 00:32.1 | 142 |
| 8 | ZULIANI CRISTINA | 1974 | 00:40.6 | nuovo |
| 11 | VEDOVELLI DANILA | 1957 | 00:46.5 | 14 |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 2 | BARRO PAOLO | 1980 | 00:26.3 | 112 |
| 4 | VECCHIATO SIMONE | 1976 | 00:27.5 | 160 |
| 8 | MENIS ALESSANDRO | 1973 | 00:30.1 | 195 |
| 11 | DAL CIN WALTER | 1983 | 00:32.0 | nuovo |
| 19 | SEMENZATO DANIELE | 1978 | 00:34.8 | 202 |
| 20 | TOPAN MAURO | 1982 | 00:34.9 | nuovo |
| 23 | ZARAMELLA BRUNO | 1943 | 00:38.3 | 165 |

**200 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 9

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 3 | FILIPPI FRANCESCO | 1980 | 02:22.6 | 60 |


### valdobbiadene_2007 — 2007-12-02, Valdobbiadene, vasca 25

**50 Dorso — Assoluti Femmine Master** — race da creare, race_event 17

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 12 | SALVALAGGIO CATIA | 1964 | 00:50.9 | 199 |
| - | BETTIOL GIULIA | 1985 | SQU | 115 |

**50 Dorso — Assoluti Maschi Master** — race da creare, race_event 17

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 1 | CALDATO SIMONE | 1985 | 00:30.6 | 117 |
| 2 | BARRO PAOLO | 1980 | 00:31.9 | 112 |
| 5 | ARDUINO DAVIDE | 1975 | 00:33.5 | 110 |
| 7 | RONSIVALLE GUIDO | 1981 | 00:35.2 | 150 |
| 10 | ANZANELLO STEFANO | 1975 | 00:37.6 | 109 |
| 15 | SALVIATO ANDREA | 1988 | 00:39.7 | 152 |
| 37 | FACCHINI STEFANO | 1959 | 00:57.5 | 126 |

**50 Farfalla — Assoluti Femmine Master** — race da creare, race_event 23

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 4 | MILANESE STEFANIA | 1986 | 00:38.7 | 142 |

**50 Farfalla — Assoluti Maschi Master** — race da creare, race_event 23

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 2 | FIORENTINI PABLO | 1985 | 00:28.3 | 128 |
| 6 | BUTTIGNOL DAVIDE | 1988 | 00:28.8 | 116 |
| 7 | FILIPPI FRANCESCO | 1980 | 00:29.4 | 60 |
| 9 | VECCHIATO SIMONE | 1976 | 00:31.6 | 160 |
| 10 | BAZZO FABIO | 1981 | 00:31.9 | 113 |
| 15 | ANZANELLO STEFANO | 1975 | 00:33.8 | 109 |
| 16 | MENIS ALESSANDRO | 1973 | 00:34.6 | 195 |
| 19 | PAPA IVAN | 1974 | 00:35.4 | 196 |
| 22 | ZANETTI LORENZO | 1982 | 00:35.8 | nuovo |
| 28 | SILVESTRIN STEFANO | 1985 | 00:37.9 | nuovo |

**50 Stile Libero — Assoluti Femmine Master** — race 17471 (esistente)

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 2 | GRANZIERA SERENA | 1982 | 00:31.9 | 135 |
| 3 | MILANESE STEFANIA | 1986 | 00:32.2 | 142 |
| 4 | BETTIOL GIULIA | 1985 | 00:33.7 | 115 |
| 19 | SALVALAGGIO CATIA | 1964 | 00:40.3 | 199 |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 1 | CALDATO SIMONE | 1985 | 00:24.5 | 117 |
| 3 | FIORENTINI PABLO | 1985 | 00:25.6 | 128 |
| 5 | BARRO PAOLO | 1980 | 00:26.0 | 112 |
| 6 | VECCHIATO SIMONE | 1976 | 00:26.6 | 160 |
| 10 | NAVE DANIELE | 1981 | 00:27.0 | 143 |
| 13 | ARDUINO DAVIDE | 1975 | 00:28.0 | 110 |
| 14 | CALESSO GIORGIO | 1983 | 00:28.4 | 118 |
| 15 | SILVESTRIN STEFANO | 1985 | 00:28.5 | nuovo |
| 19 | RONSIVALLE GUIDO | 1981 | 00:28.8 | 150 |
| 20 | MENIS ALESSANDRO | 1973 | 00:29.3 | 195 |
| 22 | ZANETTI LORENZO | 1982 | 00:29.9 | nuovo |
| 25 | SALVIATO ANDREA | 1988 | 00:30.3 | 152 |
| 28 | PINESE MASSIMO | 1977 | 00:30.5 | 146 |
| 32 | PAPA IVAN | 1974 | 00:31.3 | 196 |
| 52 | FACCHINI STEFANO | 1959 | 00:33.7 | 126 |
| 71 | ZARAMELLA BRUNO | 1943 | 00:38.9 | 165 |

**400 Stile Libero — Assoluti Femmine Master** — race 17477 (esistente)

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 2 | LAZZARIN CRISTINA | 1984 | 05:26.8 | 138 |
| - | GRANZIERA SERENA | 1982 | RIT | 135 |

**400 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 10

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 3 | FILIPPI FRANCESCO | 1980 | 04:50.4 | 60 |
| 5 | NAVE DANIELE | 1981 | 05:10.2 | 143 |
| 7 | BAZZO FABIO | 1981 | 05:22.9 | 113 |


## 6. Cosa mi serve da te

1. Via libera all'import: 1 manifestazione, 22 gare, 8 atleti, 152 risultati.
2. **Belluno 2007**: titolo neutro "Trofeo Master ASD Nuoto Belluno" oppure "8° Trofeo Città di
   Belluno" se sai che la serie e la stessa del 2006?
3. **Valdobbiadene**: metto la stagione nel titolo della nuova, e allineo anche la 1217 del 2006?
