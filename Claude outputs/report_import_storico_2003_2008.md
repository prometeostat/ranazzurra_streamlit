# Report preliminare import PDF storici (2003 e 2008)

Sette riepiloghi natatoria/Siteland, sei del 2003 e uno del 2008. Nessuna scrittura eseguita.

## 1. Manifestazioni

| PDF | data | sede | vasca | nome nel PDF | competition a DB |
|---|---|---|---|---|---|
| sdona_2003 | 2003-01-18 | S. Dona' di Piave | 25 m | I giornata circuito MASTER | **da creare** |
| oderzo_2003 | 2003-03-02 | Oderzo | 25 m | 2° Giornata Attivita' Master Sinistra Piave | 1447 |
| vittorio_2003 | 2003-04-05 | Vittorio Veneto | 25 m | Terza Giornata Attivita' Master Sinistra Piave | **da creare** |
| belluno_2003 | 2003-05-18 | Belluno | 25 m | 4° Trofeo Masters Citta' di Belluno | 1448 |
| lido_2003 | 2003-06-29 | Lido di Venezia | 25 m | 5a Giornata Circuito Master PLAVIS | 1449 |
| roncade_2003 | 2003-12-14 | Roncade | 25 m | 1a giornata circuito master | **da creare** |
| spresiano_2008 | 2008-06-14 | Spresiano (TV) | 50 m | Finale Circuito Masters Provincie BL-TV-VE | **da creare** |

Tre delle sette esistono gia, e sono quelle scoperte a suo tempo dallo scraper FIN Veneto
partendo dalla carriera di MASUTTI DENIS: ognuna contiene **un solo risultato**, il suo, con
`type` generico "Evento ufficiale/non ufficiale organizzato da Societa afferente al C.R.V.".
Le tre coincidono riga per riga col PDF:

| competition | data | gara | MASUTTI a DB | MASUTTI nel PDF | pos |
|---|---|---|---|---|---|
| 1447 | 2003-03-02 Oderzo | 100 Rana | 01:31.1 | 01:31.1 | 7 |
| 1448 | 2003-05-18 Belluno | 100 Misti | 01:25.4 | 01:25.4 | 23 |
| 1449 | 2003-06-29 Lido | 50 Rana | 00:41.0 | 00:41.0 | 7 |

Le altre quattro date non hanno nulla a DB. Attenzione a non confondere S. Dona' del
**18/01/2003** con la competition 1130 del **19/01/2003**: quella e un'altra gara, ha due
risultati di CARLET FEDERICA sui 200 misti e 200 farfalla, distanze che nel nostro PDF non ci sono.

Nel 2003-2008 il DB ha in tutto 10 atleti con almeno un risultato e nessuna manifestazione con
piu di 5 righe: lo storico e praticamente vuoto, questi PDF lo riempirebbero parecchio.

## 2. Societa: attenzione ai due Ranazzurra

Nei PDF compaiono **due societa diverse**: `RANAZZURRA S.S.D.` (in vittorio_2003 scritta solo
`RANAZZURRA`), che e la nostra, company 37, e `RANAZZURRA Lido`, che e la 57 RANAZZURRA LIDO SSD ARL,
un altro club. Ho escluso le righe del Lido: 11 a Roncade, 13 al Lido, 11 a Belluno, 18 a Vittorio,
15 a Oderzo, 68 in tutto. Se per qualche motivo ti servissero, dimmelo.

## 3. Anagrafica: 63 atleti storici, 59 da censire

Solo quattro dei 63 sono gia in `athletes`:

| PDF | anno | id a DB | nato a DB | gare nei PDF | nota |
|---|---|---|---|---|---|
| FILIPPI FRANCESCO | 1980 | 60 | 1980-01-01 | 12 | anno coerente; a DB ha 2 sole gare, entrambe del 2006 |
| MASUTTI DENIS | 1972 | 58 | 1972-11-03 | 3 | le sue 3 gare sono gia tutte a DB |
| VEDOVELLI DANILA | 1957 | 14 | 1957-01-01 | 1 | anno coerente |
| FONTANA NICO | 1979 | 61 | 1980-01-01 | 3 | **anno diverso**, vedi sotto |

`FONTANA NICO`: a DB ha `birth_date` 1980-01-01, che e chiaramente un segnaposto (lo condividono
FILIPPI, FONTANA e DA ROS, tutti e tre 1980-01-01). Il PDF dice 1979. Nei PDF FONTANA e FILIPPI
nuotano fianco a fianco nella stessa gara a Roncade (50 farfalla, 28.4 e 28.6), quindi sono due
persone distinte e non c'e confusione fra i due. Per me e lo stesso FONTANA NICO e il 1979 del PDF
e il dato buono, ma decidi tu se allinearlo.

### I 59 da censire

Tutti ex tesserati fra il 2003 e il 2008, nessuno dei quali risulta oggi in anagrafica. Il sesso
si ricava dall'intestazione del foglio, sempre univoco. Del PDF ho solo l'anno di nascita.

| cognome nome | anno | sesso | gare | manifestazioni |
|---|---|---|---|---|
| GATTI ANNA | 1954 | F | 11 | 6 |
| ISCARO DONATELLA | 1966 | F | 11 | 6 |
| BARRO PAOLO | 1980 | M | 10 | 6 |
| ZACCARIN ERMANNO | 1951 | M | 10 | 6 |
| ANDREON ALESSANDRO | 1970 | M | 9 | 5 |
| BARAZZA CLAUDIA | 1965 | F | 9 | 5 |
| GRANZIERA SERENA | 1982 | F | 9 | 6 |
| GEROMETTA LORETTA | 1951 | F | 8 | 5 |
| GUZZONATO DAVID | 1977 | M | 8 | 5 |
| GHIRARDI CLAUDIA | 1964 | F | 7 | 4 |
| GIRARDI ERMES | 1961 | M | 6 | 5 |
| MASO ALESSANDRO | 1977 | M | 6 | 6 |
| TONON SANTINA | 1952 | F | 6 | 4 |
| VENERANDO MANUELA | 1968 | F | 6 | 4 |
| PIOVESANA STEFANIA | 1961 | F | 5 | 4 |
| DONADEL LORIS | 1974 | M | 4 | 4 |
| PERINOT ALICE | 1978 | F | 4 | 4 |
| ZANET KETTY | 1977 | F | 4 | 3 |
| ZARAMELLA BRUNO | 1943 | M | 4 | 3 |
| DOPPIERI GEMMA | 1955 | F | 3 | 2 |
| FRARE MAURIZIO | 1966 | M | 3 | 3 |
| NAVE DANIELE | 1981 | M | 3 | 2 |
| DAMIAN CARLA | 1969 | F | 2 | 1 |
| DEL NEGRO ROSSELLA | 1968 | F | 2 | 1 |
| MARCON GELINDO | 1952 | M | 2 | 1 |
| MASCELLANI ANDREA | 1975 | M | 2 | 1 |
| POMPEO CARMEN | 1968 | F | 2 | 1 |
| ROSOLEN IRENE | 1984 | F | 2 | 1 |
| SANT MONICA | 1977 | F | 2 | 1 |
| TONON COSTANTINO | 1961 | M | 2 | 1 |
| ZAGO GIANNINO | 1974 | M | 2 | 1 |
| ANDREOLA ALESSANDRO | 1996 | M | 1 | 1 |
| ANZANELLO STEFANO | 1975 | M | 1 | 1 |
| ARDUINO DAVIDE | 1975 | M | 1 | 1 |
| BAZZO FABIO | 1981 | M | 1 | 1 |
| BELLAGAMBA UMBERTO | 1963 | M | 1 | 1 |
| BETTIOL GIULIA | 1985 | F | 1 | 1 |
| BUTTIGNOL DAVIDE | 1988 | M | 1 | 1 |
| CALDATO SIMONE | 1985 | M | 1 | 1 |
| CALESSO GIORGIO | 1983 | M | 1 | 1 |
| CAMERIN SEBASTIANO | 1978 | M | 1 | 1 |
| CHECCHIN MATTEO | 1986 | M | 1 | 1 |
| DALLE CRODE LISA | 1987 | F | 1 | 1 |
| FACCHINI STEFANO | 1959 | M | 1 | 1 |
| FELETTI MAURO | 1962 | M | 1 | 1 |
| FIORENTINI PABLO | 1985 | M | 1 | 1 |
| FURLAN CARLOTTA | 1988 | F | 1 | 1 |
| LAZZARIN CRISTINA | 1984 | F | 1 | 1 |
| MILANESE STEFANIA | 1986 | F | 1 | 1 |
| PERINO ALICE | 1978 | F | 1 | 1 |
| PINESE MASSIMO | 1977 | M | 1 | 1 |
| PRADELLA GIANPAOLO | 1961 | M | 1 | 1 |
| RONSIVALLE GUIDO | 1981 | M | 1 | 1 |
| SALVIATO ANDREA | 1988 | M | 1 | 1 |
| STOCCO MONICA | 1964 | F | 1 | 1 |
| TALAMINI PAOLO | 1962 | M | 1 | 1 |
| TORRESAN PAOLO | 1958 | M | 1 | 1 |
| TORRESIN DAVIDE | 1980 | M | 1 | 1 |
| VECCHIATO SIMONE | 1976 | M | 1 | 1 |

### Tre casi da chiarire prima di inserire

**PERINO ALICE (1978) e PERINOT ALICE (1978)**: quasi certamente la stessa persona. `PERINOT`
compare in quattro manifestazioni (Oderzo, Vittorio, Belluno, Lido), `PERINO` solo a S. Dona'.
Propendo per PERINOT come forma giusta e PERINO come refuso del riepilogo di S. Dona'. Se confermi,
diventano un atleta solo e le sue gare salgono a 5.

**ANDREON ALESSANDRO (1970) e ANDREOLA ALESSANDRO (1996)**: compaiono entrambi nel PDF di Roncade,
quindi come righe sono distinti, ma il 1996 in una gara master significherebbe sette anni d'eta.
O e un refuso sull'anno (1966? 1986?) o e un refuso sul cognome. Io lo inserirei comunque come
persona a se, segnalando l'anno sospetto, ma dimmi tu.

**ANDREOLA a parte**, gli altri anni di nascita sono tutti plausibili per una gara master
(dal 1943 al 1988).

## 4. Gare da creare

Nelle tre manifestazioni esistenti la race c'e solo per la gara di MASUTTI; tutto il resto va creato.

| manifestazione | races esistenti | races da creare |
|---|---|---|
| sdona_2003 | 0 | 6 |
| oderzo_2003 | 1 | 5 |
| vittorio_2003 | 0 | 6 |
| belluno_2003 | 1 | 5 |
| lido_2003 | 1 | 7 |
| roncade_2003 | 0 | 6 |
| spresiano_2008 | 0 | 9 |
| **totale** | **3** | **44** |

Convenzione che userei per il nome, copiata dalle tre races gia esistenti di queste stesse
manifestazioni: `<distanza> <stile> Serie Cat.: <categoria del foglio>`, per esempio
`50 Stile Libero Serie Cat.: Assoluti Femmine Master`. `pool_length` 25 su tutte le sei del 2003,
50 su Spresiano 2008, letto dalla riga `Base v.` di ogni foglio.

## 5. Risultati

| manifestazione | righe Ranazzurra | ASS (scartate) | gia a DB | da inserire |
|---|---|---|---|---|
| sdona_2003 | 18 | 0 | 0 | 18 |
| oderzo_2003 | 32 | 5 | 1 | 26 |
| vittorio_2003 | 32 | 3 | 0 | 29 |
| belluno_2003 | 33 | 1 | 1 | 31 |
| lido_2003 | 26 | 0 | 1 | 25 |
| roncade_2003 | 40 | 0 | 0 | 40 |
| spresiano_2008 | 30 | 3 | 0 | 27 |
| **totale** | **211** | **12** | **3** | **196** |

Le 12 righe ASS sono assenze e non vanno inserite. C'e una sola riga SQU, GATTI ANNA sui 50 stile
a Belluno: gara disputata, va inserita con `final_time` NULL.

Il riepilogo di Spresiano 2008 ha la colonna Pti valorizzata coi punti di circuito (9.00, 7.00,
6.00...). Non e il punteggio FIN e `athlete_races.fin_score` e un intero pensato per quello,
quindi lascerei perdere. Nemmeno la posizione e memorizzabile: la tabella non ha il campo.

## 6. Dettaglio dei risultati da inserire


### sdona_2003 — 2003-01-18, S. Dona' di Piave — I giornata circuito MASTER

**100 Dorso — Assoluti Femmine Master** — race da creare, race_event 18, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | BARAZZA CLAUDIA | 1965 | 01:24.4 |
| 9 | GATTI ANNA | 1954 | 01:57.2 |

**100 Dorso — Assoluti Maschi Master** — race da creare, race_event 18, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | BARRO PAOLO | 1980 | 01:08.4 |
| 2 | FILIPPI FRANCESCO | 1980 | 01:10.7 |
| 9 | ZACCARIN ERMANNO | 1951 | 01:34.3 |

**50 Farfalla — Assoluti Femmine Master** — race da creare, race_event 23, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | GRANZIERA SERENA | 1982 | 00:35.8 |
| 6 | PIOVESANA STEFANIA | 1961 | 00:44.8 |
| 7 | ISCARO DONATELLA | 1966 | 00:45.8 |
| 9 | PERINO ALICE | 1978 | 00:47.6 |

**50 Farfalla — Assoluti Maschi Master** — race da creare, race_event 23, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 3 | FILIPPI FRANCESCO | 1980 | 00:29.5 |
| 6 | ANDREON ALESSANDRO | 1970 | 00:34.7 |

**50 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 7, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | GRANZIERA SERENA | 1982 | 00:31.7 |
| 5 | BARAZZA CLAUDIA | 1965 | 00:35.0 |
| 12 | GATTI ANNA | 1954 | 00:40.5 |
| 16 | ISCARO DONATELLA | 1966 | 00:43.2 |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 2 | BARRO PAOLO | 1980 | 00:26.5 |
| 10 | ANDREON ALESSANDRO | 1970 | 00:30.2 |
| 26 | ZACCARIN ERMANNO | 1951 | 00:34.1 |


### oderzo_2003 — 2003-03-02, Oderzo — 2° Giornata Attivita' Master Sinistra Piave

**100 Rana — Assoluti Femmine Master** — race da creare, race_event 21, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 11 | PERINOT ALICE | 1978 | 01:44.0 |
| 17 | ZANET KETTY | 1977 | 01:49.5 |
| 19 | VENERANDO MANUELA | 1968 | 01:55.8 |
| 21 | GEROMETTA LORETTA | 1951 | 01:56.6 |

**100 Rana — Assoluti Maschi Master** — race 22150 (esistente), race_event 21, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 23 | DONADEL LORIS | 1974 | 01:39.5 |
| 36 | GIRARDI ERMES | 1961 | 02:05.0 |

**50 Dorso — Assoluti Femmine Master** — race da creare, race_event 17, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 9 | ISCARO DONATELLA | 1966 | 00:45.3 |
| 9 | GHIRARDI CLAUDIA | 1964 | 00:45.3 |
| 15 | GATTI ANNA | 1954 | 00:54.3 |
| 16 | PIOVESANA STEFANIA | 1961 | 00:57.2 |
| 18 | TONON SANTINA | 1952 | 01:03.6 |

**50 Dorso — Assoluti Maschi Master** — race da creare, race_event 17, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | BARRO PAOLO | 1980 | 00:31.6 |
| 3 | FILIPPI FRANCESCO | 1980 | 00:32.3 |
| 12 | ANDREON ALESSANDRO | 1970 | 00:40.7 |
| 18 | ZACCARIN ERMANNO | 1951 | 00:41.9 |

**50 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 7, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 14 | GHIRARDI CLAUDIA | 1964 | 00:36.8 |
| 21 | GATTI ANNA | 1954 | 00:40.6 |
| 22 | ISCARO DONATELLA | 1966 | 00:41.1 |
| 26 | VENERANDO MANUELA | 1968 | 00:43.2 |
| 27 | TONON SANTINA | 1952 | 00:45.7 |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 2 | BARRO PAOLO | 1980 | 00:25.8 |
| 4 | FILIPPI FRANCESCO | 1980 | 00:27.0 |
| 12 | ANDREON ALESSANDRO | 1970 | 00:30.0 |
| 37 | ZACCARIN ERMANNO | 1951 | 00:33.2 |
| 49 | GIRARDI ERMES | 1961 | 00:36.0 |
| 60 | MASO ALESSANDRO | 1977 | 00:40.5 |


### vittorio_2003 — 2003-04-05, Vittorio Veneto — Terza Giornata Attivita' Master Sinistra Piave

**100 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 8, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 8 | GHIRARDI CLAUDIA | 1964 | 01:24.9 |
| 9 | ISCARO DONATELLA | 1966 | 01:30.7 |
| 10 | GATTI ANNA | 1954 | 01:31.0 |
| 11 | VENERANDO MANUELA | 1968 | 01:37.1 |
| 15 | GEROMETTA LORETTA | 1951 | 01:43.4 |
| 16 | TONON SANTINA | 1952 | 01:49.7 |

**100 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 8, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | BARRO PAOLO | 1980 | 00:58.0 |
| 3 | FILIPPI FRANCESCO | 1980 | 01:00.3 |
| 29 | ZACCARIN ERMANNO | 1951 | 01:18.0 |

**50 Rana — Assoluti Femmine Master** — race da creare, race_event 20, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 3 | GRANZIERA SERENA | 1982 | 00:43.3 |
| 5 | PERINOT ALICE | 1978 | 00:44.7 |
| 6 | BARAZZA CLAUDIA | 1965 | 00:45.5 |
| 16 | GEROMETTA LORETTA | 1951 | 00:51.2 |
| 17 | VENERANDO MANUELA | 1968 | 00:52.5 |

**50 Rana — Assoluti Maschi Master** — race da creare, race_event 20, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 2 | GUZZONATO DAVID | 1977 | 00:32.2 |
| 5 | FILIPPI FRANCESCO | 1980 | 00:38.0 |
| 20 | DONADEL LORIS | 1974 | 00:43.1 |

**50 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 7, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 2 | GRANZIERA SERENA | 1982 | 00:31.1 |
| 4 | BARAZZA CLAUDIA | 1965 | 00:33.8 |
| 9 | GHIRARDI CLAUDIA | 1964 | 00:36.8 |
| 18 | ISCARO DONATELLA | 1966 | 00:39.7 |
| 19 | STOCCO MONICA | 1964 | 00:40.0 |
| 20 | GATTI ANNA | 1954 | 00:40.3 |
| 26 | TONON SANTINA | 1952 | 00:46.5 |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 2 | GUZZONATO DAVID | 1977 | 00:25.5 |
| 3 | BARRO PAOLO | 1980 | 00:25.9 |
| 32 | ZACCARIN ERMANNO | 1951 | 00:34.4 |
| 38 | GIRARDI ERMES | 1961 | 00:36.7 |
| 42 | MASO ALESSANDRO | 1977 | 00:39.7 |


### belluno_2003 — 2003-05-18, Belluno — 4° Trofeo Masters Citta' di Belluno

**100 Misti — Assoluti Femmine Master** — race da creare, race_event 1, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 5 | GRANZIERA SERENA | 1982 | 01:23.0 |
| 11 | PERINOT ALICE | 1978 | 01:33.6 |
| 14 | ISCARO DONATELLA | 1966 | 01:41.1 |
| 16 | PIOVESANA STEFANIA | 1961 | 01:46.1 |
| 19 | DOPPIERI GEMMA | 1955 | 01:47.7 |
| 20 | GEROMETTA LORETTA | 1951 | 01:49.1 |
| 22 | ZANET KETTY | 1977 | 02:03.8 |

**100 Misti — Assoluti Maschi Master** — race 22156 (esistente), race_event 1, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | GUZZONATO DAVID | 1977 | 01:03.7 |
| 3 | NAVE DANIELE | 1981 | 01:07.9 |
| 4 | BARRO PAOLO | 1980 | 01:09.1 |
| 34 | DONADEL LORIS | 1974 | 01:35.7 |

**200 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 9, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 8 | GHIRARDI CLAUDIA | 1964 | 03:12.9 |
| 11 | GATTI ANNA | 1954 | 03:26.0 |
| 16 | ZANET KETTY | 1977 | 04:00.0 |

**200 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 9, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | FILIPPI FRANCESCO | 1980 | 02:10.0 |
| 4 | NAVE DANIELE | 1981 | 02:22.0 |
| 13 | ANDREON ALESSANDRO | 1970 | 02:39.0 |
| 22 | ZACCARIN ERMANNO | 1951 | 02:58.0 |

**50 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 7, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 2 | GRANZIERA SERENA | 1982 | 00:31.3 |
| 9 | GHIRARDI CLAUDIA | 1964 | 00:36.8 |
| 12 | ISCARO DONATELLA | 1966 | 00:39.8 |
| 18 | DOPPIERI GEMMA | 1955 | 00:43.4 |
| 19 | GEROMETTA LORETTA | 1951 | 00:45.2 |
| 23 | TONON SANTINA | 1952 | 00:49.1 |
| - | GATTI ANNA | 1954 | SQU |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 3 | BARRO PAOLO | 1980 | 00:26.8 |
| 4 | FILIPPI FRANCESCO | 1980 | 00:26.9 |
| 6 | GUZZONATO DAVID | 1977 | 00:27.2 |
| 15 | ANDREON ALESSANDRO | 1970 | 00:30.2 |
| 31 | ZACCARIN ERMANNO | 1951 | 00:33.4 |
| 40 | GIRARDI ERMES | 1961 | 00:36.3 |


### lido_2003 — 2003-06-29, Lido di Venezia — 5a Giornata Circuito Master PLAVIS

**50 Dorso — Assoluti Femmine Master** — race da creare, race_event 17, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | BARAZZA CLAUDIA | 1965 | 00:38.4 |

**50 Dorso — Assoluti Maschi Master** — race da creare, race_event 17, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | FONTANA NICO | 1979 | 00:30.5 |
| 6 | ZACCARIN ERMANNO | 1951 | 00:41.9 |
| 9 | FELETTI MAURO | 1962 | 00:53.1 |

**50 Farfalla — Assoluti Femmine Master** — race da creare, race_event 23, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | GRANZIERA SERENA | 1982 | 00:36.3 |
| 3 | ISCARO DONATELLA | 1966 | 00:42.8 |
| 4 | PIOVESANA STEFANIA | 1961 | 00:43.2 |
| 5 | VENERANDO MANUELA | 1968 | 00:47.8 |
| 7 | GEROMETTA LORETTA | 1951 | 00:55.7 |

**50 Farfalla — Assoluti Maschi Master** — race da creare, race_event 23, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 2 | GUZZONATO DAVID | 1977 | 00:29.0 |
| 3 | FILIPPI FRANCESCO | 1980 | 00:29.0 |

**50 Rana — Assoluti Femmine Master** — race da creare, race_event 20, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 3 | PERINOT ALICE | 1978 | 00:45.3 |
| 6 | DOPPIERI GEMMA | 1955 | 00:50.2 |
| 7 | ZANET KETTY | 1977 | 00:50.7 |

**50 Rana — Assoluti Maschi Master** — race 22160 (esistente), race_event 20, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | NAVE DANIELE | 1981 | 00:34.9 |
| 2 | TORRESIN DAVIDE | 1980 | 00:36.0 |
| 12 | DONADEL LORIS | 1974 | 00:43.8 |

**50 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 7, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 4 | GHIRARDI CLAUDIA | 1964 | 00:36.6 |
| 7 | GATTI ANNA | 1954 | 00:40.8 |
| 10 | TONON SANTINA | 1952 | 00:47.8 |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | BARRO PAOLO | 1980 | 00:25.7 |
| 13 | GIRARDI ERMES | 1961 | 00:34.6 |
| 19 | ZARAMELLA BRUNO | 1943 | 00:39.1 |
| 20 | MASO ALESSANDRO | 1977 | 00:39.8 |
| 22 | FRARE MAURIZIO | 1966 | 00:58.4 |


### roncade_2003 — 2003-12-14, Roncade — 1a giornata circuito master

**100 Dorso — Assoluti Femmine Master** — race da creare, race_event 18, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | BARAZZA CLAUDIA | 1965 | 01:24.2 |
| 6 | DEL NEGRO ROSSELLA | 1968 | 01:47.2 |
| 7 | GATTI ANNA | 1954 | 01:55.2 |
| 10 | DAMIAN CARLA | 1969 | 02:03.1 |
| 13 | POMPEO CARMEN | 1968 | 02:39.1 |

**100 Dorso — Assoluti Maschi Master** — race da creare, race_event 18, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | FONTANA NICO | 1979 | 01:05.6 |
| 3 | FILIPPI FRANCESCO | 1980 | 01:09.2 |
| 4 | MASCELLANI ANDREA | 1975 | 01:11.2 |
| 18 | ZARAMELLA BRUNO | 1943 | 02:20.2 |
| 21 | MARCON GELINDO | 1952 | 02:36.6 |

**50 Farfalla — Assoluti Femmine Master** — race da creare, race_event 23, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 7 | ROSOLEN IRENE | 1984 | 00:40.8 |
| 10 | DEL NEGRO ROSSELLA | 1968 | 00:45.0 |
| 11 | ISCARO DONATELLA | 1966 | 00:45.4 |
| 12 | SANT MONICA | 1977 | 00:47.2 |
| 13 | GEROMETTA LORETTA | 1951 | 00:51.9 |

**50 Farfalla — Assoluti Maschi Master** — race da creare, race_event 23, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 3 | FONTANA NICO | 1979 | 00:28.4 |
| 4 | GUZZONATO DAVID | 1977 | 00:28.5 |
| 5 | FILIPPI FRANCESCO | 1980 | 00:28.6 |
| 10 | ANDREON ALESSANDRO | 1970 | 00:32.9 |
| 34 | TONON COSTANTINO | 1961 | 00:42.1 |
| 36 | ZAGO GIANNINO | 1974 | 00:44.0 |
| 46 | FRARE MAURIZIO | 1966 | 01:13.0 |

**50 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 7, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 2 | GRANZIERA SERENA | 1982 | 00:31.8 |
| 5 | BARAZZA CLAUDIA | 1965 | 00:34.0 |
| 8 | ROSOLEN IRENE | 1984 | 00:35.4 |
| 15 | ISCARO DONATELLA | 1966 | 00:40.1 |
| 16 | SANT MONICA | 1977 | 00:41.4 |
| 17 | GATTI ANNA | 1954 | 00:41.6 |
| 20 | GEROMETTA LORETTA | 1951 | 00:42.6 |
| 21 | DAMIAN CARLA | 1969 | 00:43.5 |
| 22 | POMPEO CARMEN | 1968 | 00:45.4 |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7, vasca 25

| pos | atleta | anno | tempo |
|---|---|---|---|
| 2 | GUZZONATO DAVID | 1977 | 00:25.3 |
| 5 | MASCELLANI ANDREA | 1975 | 00:27.2 |
| 13 | ANDREOLA ALESSANDRO | 1996 | 00:29.3 |
| 52 | GIRARDI ERMES | 1961 | 00:35.0 |
| 54 | TONON COSTANTINO | 1961 | 00:35.9 |
| 58 | ZAGO GIANNINO | 1974 | 00:37.5 |
| 59 | ZARAMELLA BRUNO | 1943 | 00:37.8 |
| 62 | MARCON GELINDO | 1952 | 00:40.0 |
| 63 | MASO ALESSANDRO | 1977 | 00:40.4 |


### spresiano_2008 — 2008-06-14, Spresiano (TV) — Finale Circuito Masters Provincie BL-TV-VE

**200 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 9, vasca 50

| pos | atleta | anno | tempo |
|---|---|---|---|
| 5 | DALLE CRODE LISA | 1987 | 02:48.2 |
| 6 | BETTIOL GIULIA | 1985 | 02:49.6 |
| 9 | VEDOVELLI DANILA | 1957 | 03:55.3 |

**200 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 9, vasca 50

| pos | atleta | anno | tempo |
|---|---|---|---|
| 3 | VECCHIATO SIMONE | 1976 | 02:13.7 |
| 5 | BAZZO FABIO | 1981 | 02:22.7 |

**50 Dorso — Assoluti Femmine Master** — race da creare, race_event 17, vasca 50

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | LAZZARIN CRISTINA | 1984 | 00:35.0 |

**50 Dorso — Assoluti Maschi Master** — race da creare, race_event 17, vasca 50

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | BARRO PAOLO | 1980 | 00:30.0 |
| 2 | ARDUINO DAVIDE | 1975 | 00:30.4 |
| 5 | PINESE MASSIMO | 1977 | 00:39.1 |
| 6 | SALVIATO ANDREA | 1988 | 00:39.5 |
| 10 | ZACCARIN ERMANNO | 1951 | 00:49.5 |

**50 Farfalla — Assoluti Femmine Master** — race da creare, race_event 23, vasca 50

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | MILANESE STEFANIA | 1986 | 00:37.2 |

**50 Farfalla — Assoluti Maschi Master** — race da creare, race_event 23, vasca 50

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | BUTTIGNOL DAVIDE | 1988 | 00:29.0 |
| 2 | FILIPPI FRANCESCO | 1980 | 00:29.1 |
| 4 | CAMERIN SEBASTIANO | 1978 | 00:32.9 |
| 5 | ANZANELLO STEFANO | 1975 | 00:33.2 |

**50 Rana — Assoluti Maschi Master** — race da creare, race_event 20, vasca 50

| pos | atleta | anno | tempo |
|---|---|---|---|
| 2 | FIORENTINI PABLO | 1985 | 00:33.6 |
| 3 | CHECCHIN MATTEO | 1986 | 00:35.7 |
| 8 | CALESSO GIORGIO | 1983 | 00:39.0 |
| 10 | BELLAGAMBA UMBERTO | 1963 | 00:40.3 |

**50 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 7, vasca 50

| pos | atleta | anno | tempo |
|---|---|---|---|
| 2 | FURLAN CARLOTTA | 1988 | 00:33.1 |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7, vasca 50

| pos | atleta | anno | tempo |
|---|---|---|---|
| 1 | CALDATO SIMONE | 1985 | 00:25.5 |
| 6 | RONSIVALLE GUIDO | 1981 | 00:28.3 |
| 12 | FACCHINI STEFANO | 1959 | 00:32.1 |
| 18 | TORRESAN PAOLO | 1958 | 00:35.5 |
| 22 | ZARAMELLA BRUNO | 1943 | 00:39.3 |
| 23 | MASO ALESSANDRO | 1977 | 00:43.1 |


## 7. Cosa mi serve da te

1. **Censisco tutti i 59 atleti storici** o mi fermo ai quattro gia in anagrafica? Con tutti si
   caricano 196 risultati e l'archivio storico della squadra diventa vero; coi soli quattro noti
   si caricano 16 righe e il resto dei PDF resta fuori.
2. **PERINO / PERINOT ALICE**: stessa persona?
3. **ANDREOLA ALESSANDRO 1996**: lo inserisco cosi com'e o conosci l'anno giusto?
4. **FONTANA NICO**: allineo la sua `birth_date` da 1980-01-01 a 1979-01-01?
5. **Le tre competitions esistenti** (1447, 1448, 1449) hanno `type` generico da FIN Veneto. Le
   lascio come sono o le rinomino col nome vero del meeting letto dal PDF?
