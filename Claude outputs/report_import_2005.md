# Report preliminare import PDF 2005

Quattro riepiloghi natatoria/Siteland della stagione 2005. Nessuna scrittura eseguita per questi.

## 0. Fatto prima, come da tua indicazione

OMETTO GIULIA censita come **femmina** (id 183, nata 1992-01-01, `is_deleted = true`) e caricati i suoi 3 risultati 2004: 50 stile a Oderzo 00:36.8 (race 22355), 50 rana a Oderzo 00:44.4 (race 22353), 50 rana alla finale di Vittorio 00:43.5 (race 22369). `athlete_races` id 7609-7611. La competition 1483 passa a 73 risultati e la 1485 a 33.

## 1. Manifestazioni: tutte e quattro da creare

| PDF | data | sede | vasca | fogli | gare | titolo nel PDF |
|---|---|---|---|---|---|---|
| sdona_2005 | 2005-01-16 | San Donà di Piave | 25 m | 8 | 6 | 1a giornata circuito MASTER |
| roncade_2005 | 2005-02-27 | Roncade | 25 m | 9 | 6 | 2° giornata circuito master |
| vittorio_2005 | 2005-03-20 | Vittorio Veneto | 25 m | 9 | 6 | Terza Giornata Circuito Master |
| sdona_2005_2 | 2005-06-25 | San Donà di Piave | 50 m | 8 | 8 | 5°GIORNATA CIRCUITO MASTERS |

Nessuna delle quattro date ha una manifestazione corrispondente a DB. **Una coincidenza da guardare
bene c'e**: il 27/02/2005, stesso giorno di Roncade, esistono le competitions 1165 e 1166. Le ho
aperte: sono gare `Assoluti Femmine Agonisti` di CARLET FEDERICA, cronometraggio AUTOMATICO, prese da
finveneto (id_manifestazione 852 e 866). Sono un'altra manifestazione, quella domenica se ne sono
corse due. Nessun rischio di duplicato.

Titoli che userei per il campo `type`:

| data | titolo proposto |
|---|---|
| 2005-01-16 | 1ª Giornata Circuito Master - San Donà di Piave |
| 2005-02-27 | 2ª Giornata Circuito Master - Roncade |
| 2005-03-20 | 3ª Giornata Circuito Master - Vittorio Veneto |
| 2005-06-25 | 5ª Giornata Circuito Master - San Donà di Piave |

La 5ª giornata del 25/06/2005 a San Donà e **in vasca da 50**, le altre tre in vasca corta. Nel PDF di
Roncade la sede è scritta "piscina comunale di Roncade", cioè l'impianto.

Con queste quattro il circuito Master sarebbe coperto per tre stagioni di fila: 2003, 2004 e 2005
(giornate 1, 2, 3 e 5, manca la 4ª come già nel 2003).

## 2. Anagrafica: non serve censire nessuno

Nei quattro PDF ci sono **17 atleti Ranazzurra Conegliano distinti e sono tutti gia in anagrafica**. Zero da censire, zero ambigui, zero match dubbi. È la prima volta che succede su questo storico.

| cognome nome | anno | id | gare 2005 |
|---|---|---|---|
| BARRO PAOLO | 1980 | 112 | 7 |
| GIRARDI ERMES | 1961 | 134 | 7 |
| CAMPODALL'ORTO ANDREA | 1980 | 172 | 6 |
| ZARAMELLA BRUNO | 1943 | 165 | 5 |
| GRANZIERA SERENA | 1982 | 135 | 5 |
| NAVE DANIELE | 1981 | 143 | 5 |
| TONON ALESSANDRO | 1977 | 181 | 5 |
| FONTANA NICO | 1979 | 61 | 4 |
| DAMIAN CARLA | 1969 | 122 | 4 |
| MASO ALESSANDRO | 1977 | 141 | 3 |
| FRARE MAURIZIO | 1966 | 129 | 3 |
| GEROMETTA LORETTA | 1951 | 132 | 3 |
| DA ROS SIMONE | 1980 | 81 | 2 |
| DE ROSA MARCO | 1972 | 175 | 2 |
| MARCON MICHELE | 1983 | 178 | 2 |
| TONON COSTANTINO | 1961 | 156 | 2 |
| DEL SIGNORE ENRICA | 1981 | 176 | 1 |

## 3. Attenzione: nel 2005 la squadra si dimezza e il Lido cresce

Vale la pena segnalartelo perché cambia la lettura dei numeri. Il confronto delle righe per società:

| stagione | RANAZZURRA S.S.D. (nostra, company 37) | RANAZZURRA Lido (company 57) |
|---|---|---|
| 2003 (6 giornate) | 211 righe, 63 atleti | 68 righe |
| 2004 (4 giornate) | 236 righe, 50 atleti | 28 righe |
| 2005 (4 giornate) | **66 righe, 17 atleti** | **67 righe, 14 atleti** |

Ho verificato la cosa ovvia da sospettare, cioè che i nostri fossero passati sotto la sigla Lido:
**nessuno dei 14 atleti del Lido 2005 compare fra i nostri del 2003 o 2004**. Sono persone diverse,
quindi l'esclusione delle righe Lido resta corretta e il calo dei nostri è reale, non un artefatto
di denominazione.

## 4. Risultati

| manifestazione | righe Ranazzurra | ASS scartate | da inserire | gare da creare |
|---|---|---|---|---|
| sdona_2005 | 16 | 2 | 14 | 4 |
| roncade_2005 | 22 | 7 | 15 | 5 |
| vittorio_2005 | 18 | 2 | 16 | 6 |
| sdona_2005_2 | 10 | 1 | 9 | 7 |
| **totale** | **66** | **12** | **54** | **22** |

Una riga RIT, CAMPODALL'ORTO ANDREA sui 100 dorso a San Donà in gennaio: ritiro, quindi gara
disputata, la inserirei con `final_time` NULL. Nessuna staffetta. Nessun tempo anomalo tipo il
14:56.7 di Zanini: il più lento è un 100 dorso in 02:05.8, del tutto plausibile.

## 5. Dettaglio dei risultati da inserire


### sdona_2005 — 2005-01-16, San Donà di Piave, vasca 25

**50 Farfalla — Assoluti Maschi Master** — race da creare, race_event 23

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 4 | FONTANA NICO | 1979 | 00:29.5 | 61 |
| 5 | DA ROS SIMONE | 1980 | 00:29.7 | 81 |

**50 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 5 | GRANZIERA SERENA | 1982 | 00:31.3 | 135 |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 4 | BARRO PAOLO | 1980 | 00:26.9 | 112 |
| 8 | DA ROS SIMONE | 1980 | 00:27.8 | 81 |
| 78 | GIRARDI ERMES | 1961 | 00:36.5 | 134 |
| 79 | CAMPODALL'ORTO ANDREA | 1980 | 00:37.2 | 172 |
| 89 | ZARAMELLA BRUNO | 1943 | 00:38.9 | 165 |
| 93 | MASO ALESSANDRO | 1977 | 00:42.1 | 141 |
| 97 | FRARE MAURIZIO | 1966 | 01:02.2 | 129 |

**100 Dorso — Assoluti Maschi Master** — race da creare, race_event 18

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 2 | BARRO PAOLO | 1980 | 01:06.8 | 112 |
| 4 | FONTANA NICO | 1979 | 01:08.4 | 61 |
| 30 | GIRARDI ERMES | 1961 | 02:05.8 | 134 |
| - | CAMPODALL'ORTO ANDREA | 1980 | RIT | 172 |


### roncade_2005 — 2005-02-27, Roncade, vasca 25

**50 Dorso — Assoluti Maschi Master** — race da creare, race_event 17

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 1 | FONTANA NICO | 1979 | 00:30.4 | 61 |
| 29 | TONON ALESSANDRO | 1977 | 00:45.1 | 181 |
| 45 | GIRARDI ERMES | 1961 | 00:53.2 | 134 |
| 52 | ZARAMELLA BRUNO | 1943 | 01:02.0 | 165 |

**50 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 24 | DAMIAN CARLA | 1969 | 00:40.7 | 122 |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 3 | FONTANA NICO | 1979 | 00:26.1 | 61 |
| 7 | NAVE DANIELE | 1981 | 00:27.5 | 143 |
| 12 | MARCON MICHELE | 1983 | 00:27.9 | 178 |
| 39 | TONON ALESSANDRO | 1977 | 00:31.9 | 181 |
| 80 | CAMPODALL'ORTO ANDREA | 1980 | 00:37.4 | 172 |
| 81 | ZARAMELLA BRUNO | 1943 | 00:38.8 | 165 |

**100 Rana — Assoluti Femmine Master** — race da creare, race_event 21

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 17 | DAMIAN CARLA | 1969 | 01:53.3 | 122 |

**100 Rana — Assoluti Maschi Master** — race da creare, race_event 21

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 2 | NAVE DANIELE | 1981 | 01:16.1 | 143 |
| 24 | CAMPODALL'ORTO ANDREA | 1980 | 01:32.8 | 172 |
| 62 | GIRARDI ERMES | 1961 | 01:50.0 | 134 |


### vittorio_2005 — 2005-03-20, Vittorio Veneto, vasca 25

**50 Rana — Assoluti Femmine Master** — race da creare, race_event 20

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 10 | GRANZIERA SERENA | 1982 | 00:44.6 | 135 |
| 17 | GEROMETTA LORETTA | 1951 | 00:50.6 | 132 |
| 20 | DAMIAN CARLA | 1969 | 00:51.1 | 122 |

**50 Rana — Assoluti Maschi Master** — race da creare, race_event 20

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 3 | NAVE DANIELE | 1981 | 00:34.3 | 143 |
| 35 | CAMPODALL'ORTO ANDREA | 1980 | 00:42.7 | 172 |
| 55 | GIRARDI ERMES | 1961 | 00:47.8 | 134 |

**50 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 4 | GRANZIERA SERENA | 1982 | 00:31.4 | 135 |
| 31 | GEROMETTA LORETTA | 1951 | 00:43.3 | 132 |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 6 | NAVE DANIELE | 1981 | 00:27.4 | 143 |
| 42 | TONON ALESSANDRO | 1977 | 00:32.9 | 181 |
| 59 | CAMPODALL'ORTO ANDREA | 1980 | 00:38.2 | 172 |
| 61 | ZARAMELLA BRUNO | 1943 | 00:38.8 | 165 |
| 66 | FRARE MAURIZIO | 1966 | 01:00.0 | 129 |

**100 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 8

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 17 | DAMIAN CARLA | 1969 | 01:39.3 | 122 |

**100 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 8

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 39 | TONON ALESSANDRO | 1977 | 01:17.5 | 181 |
| 55 | GIRARDI ERMES | 1961 | 01:26.3 | 134 |


### sdona_2005_2 — 2005-06-25, San Donà di Piave, vasca 50

**50 Dorso — Assoluti Femmine Master** — race da creare, race_event 17

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 3 | DEL SIGNORE ENRICA | 1981 | 00:43.3 | 176 |

**50 Dorso — Assoluti Maschi Master** — race da creare, race_event 17

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 3 | BARRO PAOLO | 1980 | 00:33.3 | 112 |

**50 Farfalla — Assoluti Maschi Master** — race da creare, race_event 23

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 17 | GIRARDI ERMES | 1961 | 00:45.8 | 134 |

**50 Rana — Assoluti Femmine Master** — race da creare, race_event 20

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 4 | GEROMETTA LORETTA | 1951 | 00:50.1 | 132 |

**50 Rana — Assoluti Maschi Master** — race da creare, race_event 20

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 3 | NAVE DANIELE | 1981 | 00:36.1 | 143 |

**50 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 1 | GRANZIERA SERENA | 1982 | 00:31.8 | 135 |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | id |
|---|---|---|---|---|
| 15 | TONON ALESSANDRO | 1977 | 00:32.8 | 181 |
| 27 | ZARAMELLA BRUNO | 1943 | 00:38.7 | 165 |
| 30 | MASO ALESSANDRO | 1977 | 00:44.2 | 141 |


## 6. Cosa mi serve da te

Solo il via libera: 4 manifestazioni, 22 gare, 0 atleti nuovi, 54 risultati. Non ci sono casi dubbi
da sciogliere questa volta.
