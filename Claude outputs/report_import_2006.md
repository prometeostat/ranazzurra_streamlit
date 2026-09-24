# Report preliminare import PDF 2006

Sei riepiloghi natatoria/Siteland della stagione 2006. Nessuna scrittura eseguita.

## 1. Manifestazioni: una sola da creare, cinque gia a DB

| PDF | data | sede | vasca | fogli | gare | competition | nome a DB |
|---|---|---|---|---|---|---|---|
| sdona_2006 | 2006-01-28 | San Donà di Piave | 25 m | 7 | 6 | **da creare** | - |
| oderzo_2006 | 2006-03-19 | Oderzo | 25 m | 8 | 6 | **1213** | generico |
| vittorio_2006 | 2006-04-23 | Vittorio Veneto | 25 m | 7 | 6 | **1214** | generico |
| belluno_2006 | 2006-05-21 | Belluno | 25 m | 8 | 6 | **29** | gia corretto |
| spresiano_2006 | 2006-07-01 | Spresiano | 50 m | 8 | 8 | **1216** | generico |
| valdobbiadene_2006 | 2006-12-03 | Valdobbiadene | 25 m | 9 | 8 | **1217** | generico |

Questa volta il DB e gia parecchio popolato su queste date, ma quasi sempre con **una riga sola**:
lo scraper FIN Veneto ha seguito la carriera di VEDOVELLI DANILA, che nel 2006 gareggiava, e per ogni
giornata ha creato una competition con dentro il suo unico 50 stile. Ho controllato tutti e cinque i
tempi e **coincidono esattamente col PDF**:

| competition | data | atleta | gara | a DB | nel PDF | pos |
|---|---|---|---|---|---|---|
| 1213 | 2006-03-19 Oderzo | VEDOVELLI DANILA | 50 SL | 00:45.2 | 00:45.2 | 30 |
| 1214 | 2006-04-23 Vittorio | VEDOVELLI DANILA | 50 SL | 00:46.8 | 00:46.8 | 31 |
| 1215 | 2006-05-21 Belluno | VEDOVELLI DANILA | 50 SL | 00:46.3 | 00:46.3 | 33 |
| 1216 | 2006-07-01 Spresiano | VEDOVELLI DANILA | 50 SL | 00:45.8 | 00:45.8 | 14 |
| 1217 | 2006-12-03 Valdobbiadene | VEDOVELLI DANILA | 400 SL | 08:32.3 | 08:32.3 | 9 |

Titoli che proporrei per le quattro col `type` generico, piu la nuova:

| competition | titolo proposto |
|---|---|
| da creare (2006-01-28) | 1ª Giornata Circuito Master Sinistra Piave - San Donà di Piave |
| 1213 (2006-03-19) | 2ª Giornata Circuito Master Sinistra Piave - Oderzo |
| 1214 (2006-04-23) | 3ª Giornata Circuito Master - Vittorio Veneto |
| 1216 (2006-07-01) | Finale Circuito Masters Provincia di Treviso - Spresiano |
| 1217 (2006-12-03) | 1ª Giornata Circuito Master - Valdobbiadene |

### Il caso Belluno: la stessa manifestazione due volte

Il 21/05/2006 a DB ci sono **due competitions per lo stesso evento**, entrambe con `web_id = 1246`:

- **competition 29**, `scraping_website_id = 2` (natatoria), gia intitolata **"7° Trofeo Città di
  Belluno"**, cronometraggio SEMI-AUTOMATICO, 3 races con nomi puliti (`200 Stile Libero`,
  `50 Stile Libero`, `100 Misti`) e 5 risultati: FILIPPI 200 SL 02:06.8 e 50 SL 00:26.4, FONTANA
  50 SL 00:26.9, DA ROS 50 SL 00:27.1 e 100 misti 01:15.1. **Tutti e cinque coincidono col PDF.**
- **competition 1215**, `scraping_website_id = 1` (FIN Veneto), `type` generico, 1 race e il solo
  50 stile di VEDOVELLI.

E l'unico caso di web_id duplicato in tutto il database, l'ho verificato. Le tre races della 29 non
sono divise per sesso, esattamente come quelle delle giornate Aquasport recenti, e coprono tutti e
tre gli eventi della giornata: ci stanno dentro tutte le righe del PDF senza crearne nessuna nuova.

La mia proposta: **caricare Belluno dentro la competition 29**, spostare il risultato di VEDOVELLI
(`ar 2001`) dalla race 17427 alla race 185 e mettere `is_deleted = true` sulla competition 1215 e
sulla sua race. Cosi la giornata sta tutta in un posto solo. In alternativa lascio le due
competitions separate e carico in 29, ma la giornata resta spezzata e Vedovelli finisce in un
contenitore diverso dalle sue compagne. Non tocco niente finche non decidi.

Segnalo anche, per scrupolo, che il 03/12/2006 c'e una **seconda** competition, la 1392 con
`web_id 1351`, che contiene due risultati di MONDELLI CLAUDIO in gare `Cat.: P3 F`. Web_id diverso,
categoria propaganda, e MONDELLI non compare nel nostro PDF: **e un'altra manifestazione**, la lascio
stare.

## 2. Anagrafica

Nei sei PDF ci sono **50 atleti Ranazzurra distinti**: 28 gia in anagrafica e 22 da censire. Zero ambigui. L'unica somiglianza segnalata dal controllo automatico e ANDREON ALESSANDRO 1970 contro ANDREOLA ALESSANDRO 1996, che pero' hai gia confermato essere due persone diverse.

### Gia presenti

| cognome nome | anno | id | gare 2006 |
|---|---|---|---|
| CAMPODALL'ORTO ANDREA | 1980 | 172 | 11 |
| BARAZZA CLAUDIA | 1965 | 111 | 9 |
| FRARE MAURIZIO | 1966 | 129 | 8 |
| BARRO PAOLO | 1980 | 112 | 8 |
| CHECCHIN MATTEO | 1986 | 120 | 8 |
| NAVE DANIELE | 1981 | 143 | 7 |
| FILIPPI FRANCESCO | 1980 | 60 | 7 |
| CALESSO GIORGIO | 1983 | 118 | 7 |
| FONTANA NICO | 1979 | 61 | 7 |
| ZARAMELLA BRUNO | 1943 | 165 | 6 |
| GIRARDI ERMES | 1961 | 134 | 6 |
| BETTIOL GIULIA | 1985 | 115 | 6 |
| MASO ALESSANDRO | 1977 | 141 | 5 |
| VEDOVELLI DANILA | 1957 | 14 | 5 |
| VENERANDO MANUELA | 1968 | 161 | 5 |
| DA ROS SIMONE | 1980 | 81 | 4 |
| ROSOLEN IRENE | 1984 | 151 | 4 |
| PINESE MASSIMO | 1977 | 146 | 4 |
| RONSIVALLE GUIDO | 1981 | 150 | 3 |
| MILANESE STEFANIA | 1986 | 142 | 3 |
| GHIRARDI CLAUDIA | 1964 | 133 | 2 |
| TONON ALESSANDRO | 1977 | 181 | 2 |
| GRANZIERA SERENA | 1982 | 135 | 2 |
| ANDREON ALESSANDRO | 1970 | 108 | 2 |
| LAZZARIN CRISTINA | 1984 | 138 | 2 |
| ZACCARIN ERMANNO | 1951 | 162 | 1 |
| BELLAGAMBA UMBERTO | 1963 | 114 | 1 |
| GEROMETTA LORETTA | 1951 | 132 | 1 |

### Da censire (22)

| cognome nome | anno | sesso | gare | manifestazioni |
|---|---|---|---|---|
| GHIRARDO LETIZIA | 1984 | F | 8 | 5 |
| SALVALAGGIO CATIA | 1964 | F | 8 | 5 |
| CASAGRANDE FABRIZIO | 1976 | M | 7 | 4 |
| MENIS ALESSANDRO | 1973 | M | 7 | 5 |
| SCHIEVENE FEDERICA | 1976 | F | 5 | 4 |
| DONADEL ANDREA | 1976 | M | 4 | 2 |
| COZZUOL MATTEO | 1976 | M | 3 | 2 |
| DAVANZO GESSICA | 1985 | F | 3 | 3 |
| PICCOLI IVANO | 1971 | M | 3 | 3 |
| DA ROS GABRIELE | 1983 | M | 2 | 1 |
| DE STEFANI PAOLO | 1970 | M | 2 | 2 |
| GRANZOTTO ANDREA | 1976 | M | 2 | 2 |
| ZANCHETTA MICHELA | 1980 | F | 2 | 2 |
| BLASI STEFANO | 1983 | M | 1 | 1 |
| GERARDO SIMONE | 1979 | M | 1 | 1 |
| MENEGHIN LORETTA | 1964 | F | 1 | 1 |
| PAPA IVAN | 1974 | M | 1 | 1 |
| RUI ALBERTO | 1982 | M | 1 | 1 |
| SARTORI EROS | 1981 | M | 1 | 1 |
| SEMENZATO DANIELE | 1978 | M | 1 | 1 |
| ZANATTA SARA | 1983 | F | 1 | 1 |
| ZANIN ANNALISA | 1972 | F | 1 | 1 |

Cognomi che si somigliano ma sono persone diverse: GHIRARDO LETIZIA (1984) non e GHIRARDI CLAUDIA
(id 133, 1964), DONADEL ANDREA non e DONADEL LORIS (id 124), DA ROS GABRIELE non e DA ROS SIMONE
(id 81) ne DA ROS FABRICE (id 173).

## 3. Gare

**26 races da creare**, 10 riutilizzate fra quelle gia presenti (17413, 17419, 17436, 17445 di Vedovelli e 184, 185, 186 della competition 29).

Una gara non la creo: i 50 farfalla maschi di San Donà hanno una sola riga Ranazzurra ed e un'assenza.

## 4. Risultati

| manifestazione | righe | ASS | gia a DB | da inserire |
|---|---|---|---|---|
| sdona_2006 | 7 | 2 | 0 | 5 |
| oderzo_2006 | 41 | 5 | 1 | 35 |
| vittorio_2006 | 42 | 0 | 1 | 41 |
| belluno_2006 | 48 | 3 | 6 | 39 |
| spresiano_2006 | 27 | 3 | 1 | 23 |
| valdobbiadene_2006 | 36 | 1 | 1 | 34 |
| **totale** | **201** | **14** | **10** | **177** |

Una riga SQU, DONADEL ANDREA sui 50 stile a Vittorio Veneto: gara disputata, da inserire con
`final_time` NULL. Nessuna staffetta. Nessun tempo anomalo: ho controllato il piu lento per ogni
distanza e sono tutti plausibili.

Da notare il crollo di San Donà in gennaio, appena 7 righe Ranazzurra, e la ripresa netta nelle
giornate successive (41, 42, 48). Dopo il minimo del 2005 la squadra torna a riempire i fogli.

## 5. Dettaglio dei risultati da inserire


### sdona_2006 — 2006-01-28, San Donà di Piave, vasca 25

**50 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 6 | BARAZZA CLAUDIA | 1965 | 00:33.4 | 111 |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 45 | CAMPODALL'ORTO ANDREA | 1980 | 00:34.1 | 172 |
| 58 | ZARAMELLA BRUNO | 1943 | 00:38.8 | 165 |
| 63 | MASO ALESSANDRO | 1977 | 00:43.9 | 141 |

**100 Dorso — Assoluti Maschi Master** — race da creare, race_event 18

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 13 | CAMPODALL'ORTO ANDREA | 1980 | 01:49.0 | 172 |


### oderzo_2006 — 2006-03-19, Oderzo, vasca 25

**50 Dorso — Assoluti Femmine Master** — race da creare, race_event 17

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 15 | SCHIEVENE FEDERICA | 1976 | 00:52.2 | nuovo |
| 17 | SALVALAGGIO CATIA | 1964 | 00:52.9 | nuovo |

**50 Dorso — Assoluti Maschi Master** — race da creare, race_event 17

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 1 | FONTANA NICO | 1979 | 00:31.1 | 61 |
| 3 | BARRO PAOLO | 1980 | 00:32.8 | 112 |
| 4 | FILIPPI FRANCESCO | 1980 | 00:33.0 | 60 |

**50 Stile Libero — Assoluti Femmine Master** — race 17413 (esistente)

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 9 | ROSOLEN IRENE | 1984 | 00:34.3 | 151 |
| 19 | SALVALAGGIO CATIA | 1964 | 00:41.8 | nuovo |
| 23 | GHIRARDO LETIZIA | 1984 | 00:43.1 | nuovo |
| 27 | ZANCHETTA MICHELA | 1980 | 00:44.1 | nuovo |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 3 | BARRO PAOLO | 1980 | 00:26.2 | 112 |
| 8 | DA ROS SIMONE | 1980 | 00:27.5 | 81 |
| 8 | NAVE DANIELE | 1981 | 00:27.5 | 143 |
| 16 | CHECCHIN MATTEO | 1986 | 00:28.7 | 120 |
| 18 | FILIPPI FRANCESCO | 1980 | 00:29.0 | 60 |
| 27 | MENIS ALESSANDRO | 1973 | 00:31.0 | nuovo |
| 32 | CALESSO GIORGIO | 1983 | 00:31.8 | 118 |
| 49 | CAMPODALL'ORTO ANDREA | 1980 | 00:33.9 | 172 |
| 55 | FONTANA NICO | 1979 | 00:34.7 | 61 |
| 57 | CASAGRANDE FABRIZIO | 1976 | 00:34.9 | nuovo |
| 60 | GIRARDI ERMES | 1961 | 00:35.5 | 134 |
| 71 | DE STEFANI PAOLO | 1970 | 00:37.8 | nuovo |
| 72 | ZARAMELLA BRUNO | 1943 | 00:38.5 | 165 |
| 76 | MASO ALESSANDRO | 1977 | 00:43.1 | 141 |
| 77 | FRARE MAURIZIO | 1966 | 01:06.0 | 129 |

**100 Rana — Assoluti Femmine Master** — race da creare, race_event 21

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 10 | ROSOLEN IRENE | 1984 | 01:43.0 | 151 |
| 13 | GHIRARDO LETIZIA | 1984 | 01:49.5 | nuovo |

**100 Rana — Assoluti Maschi Master** — race da creare, race_event 21

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 3 | NAVE DANIELE | 1981 | 01:15.7 | 143 |
| 7 | CHECCHIN MATTEO | 1986 | 01:21.3 | 120 |
| 15 | CAMPODALL'ORTO ANDREA | 1980 | 01:29.5 | 172 |
| 20 | CALESSO GIORGIO | 1983 | 01:32.1 | 118 |
| 35 | GRANZOTTO ANDREA | 1976 | 01:41.1 | nuovo |
| 36 | CASAGRANDE FABRIZIO | 1976 | 01:41.2 | nuovo |
| 42 | PICCOLI IVANO | 1971 | 01:46.4 | nuovo |
| 48 | GIRARDI ERMES | 1961 | 01:51.2 | 134 |
| 50 | FRARE MAURIZIO | 1966 | 02:10.0 | 129 |


### vittorio_2006 — 2006-04-23, Vittorio Veneto, vasca 25

**50 Rana — Assoluti Femmine Master** — race da creare, race_event 20

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 8 | ROSOLEN IRENE | 1984 | 00:44.4 | 151 |
| 9 | BARAZZA CLAUDIA | 1965 | 00:45.1 | 111 |
| 12 | GHIRARDO LETIZIA | 1984 | 00:50.1 | nuovo |
| 15 | VENERANDO MANUELA | 1968 | 00:52.4 | 161 |

**50 Rana — Assoluti Maschi Master** — race da creare, race_event 20

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 2 | NAVE DANIELE | 1981 | 00:34.3 | 143 |
| 5 | CHECCHIN MATTEO | 1986 | 00:35.9 | 120 |
| 11 | COZZUOL MATTEO | 1976 | 00:39.3 | nuovo |
| 16 | CAMPODALL'ORTO ANDREA | 1980 | 00:40.4 | 172 |
| 19 | DONADEL ANDREA | 1976 | 00:42.8 | nuovo |
| 22 | CALESSO GIORGIO | 1983 | 00:43.0 | 118 |
| 33 | CASAGRANDE FABRIZIO | 1976 | 00:45.1 | nuovo |
| 45 | GIRARDI ERMES | 1961 | 00:48.8 | 134 |
| 48 | FRARE MAURIZIO | 1966 | 01:23.0 | 129 |

**50 Stile Libero — Assoluti Femmine Master** — race 17419 (esistente)

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 5 | GRANZIERA SERENA | 1982 | 00:32.0 | 135 |
| 9 | BARAZZA CLAUDIA | 1965 | 00:33.9 | 111 |
| 10 | ROSOLEN IRENE | 1984 | 00:34.5 | 151 |
| 11 | ZANATTA SARA | 1983 | 00:35.4 | nuovo |
| 13 | BETTIOL GIULIA | 1985 | 00:35.8 | 115 |
| 18 | VENERANDO MANUELA | 1968 | 00:38.3 | 161 |
| 20 | GHIRARDO LETIZIA | 1984 | 00:40.2 | nuovo |
| 21 | SALVALAGGIO CATIA | 1964 | 00:40.4 | nuovo |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 2 | BARRO PAOLO | 1980 | 00:26.8 | 112 |
| 4 | FILIPPI FRANCESCO | 1980 | 00:27.2 | 60 |
| 8 | NAVE DANIELE | 1981 | 00:28.2 | 143 |
| 11 | CHECCHIN MATTEO | 1986 | 00:28.9 | 120 |
| 22 | TONON ALESSANDRO | 1977 | 00:30.9 | 181 |
| 24 | CALESSO GIORGIO | 1983 | 00:31.0 | 118 |
| 24 | PINESE MASSIMO | 1977 | 00:31.0 | 146 |
| 29 | MENIS ALESSANDRO | 1973 | 00:32.0 | nuovo |
| 39 | CASAGRANDE FABRIZIO | 1976 | 00:34.0 | nuovo |
| 43 | CAMPODALL'ORTO ANDREA | 1980 | 00:34.3 | 172 |
| 52 | GIRARDI ERMES | 1961 | 00:37.7 | 134 |
| 57 | ZARAMELLA BRUNO | 1943 | 00:39.0 | 165 |
| 61 | MASO ALESSANDRO | 1977 | 00:42.6 | 141 |
| 62 | FRARE MAURIZIO | 1966 | 01:01.5 | 129 |
| - | DONADEL ANDREA | 1976 | SQU | nuovo |

**100 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 8

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 19 | SALVALAGGIO CATIA | 1964 | 01:35.6 | nuovo |

**100 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 8

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 2 | FILIPPI FRANCESCO | 1980 | 00:59.3 | 60 |
| 4 | BARRO PAOLO | 1980 | 01:01.3 | 112 |
| 19 | MENIS ALESSANDRO | 1973 | 01:11.1 | nuovo |
| 27 | TONON ALESSANDRO | 1977 | 01:14.3 | 181 |


### belluno_2006 — 2006-05-21, Belluno, vasca 25

**50 Stile Libero — Assoluti Femmine Master** — race 185 (esistente)

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 7 | MILANESE STEFANIA | 1986 | 00:33.3 | 142 |
| 8 | BETTIOL GIULIA | 1985 | 00:33.5 | 115 |
| 17 | VENERANDO MANUELA | 1968 | 00:38.0 | 161 |
| 21 | SCHIEVENE FEDERICA | 1976 | 00:40.6 | nuovo |
| 22 | GHIRARDO LETIZIA | 1984 | 00:41.3 | nuovo |
| 23 | SALVALAGGIO CATIA | 1964 | 00:41.9 | nuovo |
| 30 | ZANCHETTA MICHELA | 1980 | 00:44.3 | nuovo |
| 32 | DAVANZO GESSICA | 1985 | 00:45.7 | nuovo |

**50 Stile Libero — Assoluti Maschi Master** — race 185 (esistente)

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 3 | BARRO PAOLO | 1980 | 00:26.5 | 112 |
| 10 | NAVE DANIELE | 1981 | 00:27.7 | 143 |
| 12 | CHECCHIN MATTEO | 1986 | 00:28.7 | 120 |
| 19 | PINESE MASSIMO | 1977 | 00:29.9 | 146 |
| 19 | ANDREON ALESSANDRO | 1970 | 00:29.9 | 108 |
| 23 | MENIS ALESSANDRO | 1973 | 00:30.4 | nuovo |
| 24 | RONSIVALLE GUIDO | 1981 | 00:30.5 | 150 |
| 28 | CALESSO GIORGIO | 1983 | 00:30.8 | 118 |
| 39 | DONADEL ANDREA | 1976 | 00:33.5 | nuovo |
| 41 | CASAGRANDE FABRIZIO | 1976 | 00:33.7 | nuovo |
| 43 | COZZUOL MATTEO | 1976 | 00:34.3 | nuovo |
| 47 | CAMPODALL'ORTO ANDREA | 1980 | 00:34.6 | 172 |
| 61 | GIRARDI ERMES | 1961 | 00:37.8 | 134 |
| 64 | ZARAMELLA BRUNO | 1943 | 00:38.8 | 165 |
| 67 | MASO ALESSANDRO | 1977 | 00:42.0 | 141 |
| 69 | FRARE MAURIZIO | 1966 | 01:00.8 | 129 |

**100 Misti — Assoluti Femmine Master** — race 186 (esistente)

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 15 | BETTIOL GIULIA | 1985 | 01:36.5 | 115 |
| 17 | VENERANDO MANUELA | 1968 | 01:41.1 | 161 |

**100 Misti — Assoluti Maschi Master** — race 186 (esistente)

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 2 | NAVE DANIELE | 1981 | 01:08.0 | 143 |
| 4 | FONTANA NICO | 1979 | 01:10.1 | 61 |
| 8 | CHECCHIN MATTEO | 1986 | 01:14.9 | 120 |
| 21 | PINESE MASSIMO | 1977 | 01:24.0 | 146 |
| 29 | COZZUOL MATTEO | 1976 | 01:26.2 | nuovo |
| 38 | CAMPODALL'ORTO ANDREA | 1980 | 01:33.6 | 172 |

**200 Stile Libero — Assoluti Femmine Master** — race 184 (esistente)

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 9 | GHIRARDO LETIZIA | 1984 | 03:23.1 | nuovo |
| 10 | SALVALAGGIO CATIA | 1964 | 03:30.8 | nuovo |

**200 Stile Libero — Assoluti Maschi Master** — race 184 (esistente)

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 8 | RONSIVALLE GUIDO | 1981 | 02:36.8 | 150 |
| 9 | ANDREON ALESSANDRO | 1970 | 02:38.2 | 108 |
| 16 | DONADEL ANDREA | 1976 | 02:55.5 | nuovo |
| 19 | MENIS ALESSANDRO | 1973 | 02:59.7 | nuovo |
| 21 | CASAGRANDE FABRIZIO | 1976 | 03:03.0 | nuovo |


### spresiano_2006 — 2006-07-01, Spresiano, vasca 50

**50 Dorso — Assoluti Femmine Master** — race da creare, race_event 17

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 4 | SALVALAGGIO CATIA | 1964 | 00:53.1 | nuovo |
| 6 | SCHIEVENE FEDERICA | 1976 | 00:54.0 | nuovo |
| 7 | DAVANZO GESSICA | 1985 | 00:54.2 | nuovo |

**50 Dorso — Assoluti Maschi Master** — race da creare, race_event 17

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 1 | FONTANA NICO | 1979 | 00:32.1 | 61 |
| 7 | ZACCARIN ERMANNO | 1951 | 00:46.3 | 162 |

**50 Farfalla — Assoluti Femmine Master** — race da creare, race_event 23

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 3 | MENEGHIN LORETTA | 1964 | 00:43.1 | nuovo |
| 4 | VENERANDO MANUELA | 1968 | 00:48.0 | 161 |

**50 Farfalla — Assoluti Maschi Master** — race da creare, race_event 23

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 1 | FILIPPI FRANCESCO | 1980 | 00:28.4 | 60 |

**50 Rana — Assoluti Femmine Master** — race da creare, race_event 20

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 11 | ZANIN ANNALISA | 1972 | 01:02.0 | nuovo |

**50 Rana — Assoluti Maschi Master** — race da creare, race_event 20

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 1 | NAVE DANIELE | 1981 | 00:35.1 | 143 |
| 3 | BELLAGAMBA UMBERTO | 1963 | 00:39.1 | 114 |
| 6 | CAMPODALL'ORTO ANDREA | 1980 | 00:40.8 | 172 |
| 11 | SEMENZATO DANIELE | 1978 | 00:45.8 | nuovo |
| 15 | PICCOLI IVANO | 1971 | 00:47.8 | nuovo |

**50 Stile Libero — Assoluti Femmine Master** — race 17436 (esistente)

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 2 | GRANZIERA SERENA | 1982 | 00:32.7 | 135 |
| 3 | MILANESE STEFANIA | 1986 | 00:33.4 | 142 |
| 4 | BETTIOL GIULIA | 1985 | 00:33.9 | 115 |
| 9 | GHIRARDO LETIZIA | 1984 | 00:41.4 | nuovo |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 1 | BARRO PAOLO | 1980 | 00:26.3 | 112 |
| 7 | RONSIVALLE GUIDO | 1981 | 00:30.6 | 150 |
| 7 | MENIS ALESSANDRO | 1973 | 00:30.6 | nuovo |
| 19 | CASAGRANDE FABRIZIO | 1976 | 00:35.1 | nuovo |
| 24 | ZARAMELLA BRUNO | 1943 | 00:38.3 | 165 |


### valdobbiadene_2006 — 2006-12-03, Valdobbiadene, vasca 25

**50 Farfalla — Assoluti Maschi Master** — race da creare, race_event 23

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 2 | DA ROS GABRIELE | 1983 | 00:29.3 | nuovo |
| 11 | CHECCHIN MATTEO | 1986 | 00:32.7 | 120 |

**50 Stile Libero — Assoluti Femmine Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 4 | LAZZARIN CRISTINA | 1984 | 00:31.2 | 138 |
| 7 | MILANESE STEFANIA | 1986 | 00:32.9 | 142 |
| 9 | BETTIOL GIULIA | 1985 | 00:33.9 | 115 |
| 17 | GHIRARDO LETIZIA | 1984 | 00:39.7 | nuovo |
| 20 | SCHIEVENE FEDERICA | 1976 | 00:40.2 | nuovo |
| 22 | DAVANZO GESSICA | 1985 | 00:43.1 | nuovo |
| 24 | GEROMETTA LORETTA | 1951 | 00:44.3 | 132 |

**50 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 7

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 1 | BARRO PAOLO | 1980 | 00:26.4 | 112 |
| 4 | FONTANA NICO | 1979 | 00:26.7 | 61 |
| 9 | CHECCHIN MATTEO | 1986 | 00:28.5 | 120 |
| 13 | CALESSO GIORGIO | 1983 | 00:29.4 | 118 |
| 15 | RUI ALBERTO | 1982 | 00:29.8 | nuovo |
| 20 | PINESE MASSIMO | 1977 | 00:30.6 | 146 |
| 39 | SARTORI EROS | 1981 | 00:33.5 | nuovo |
| 45 | CAMPODALL'ORTO ANDREA | 1980 | 00:34.5 | 172 |
| 56 | DE STEFANI PAOLO | 1970 | 00:38.3 | nuovo |
| 60 | ZARAMELLA BRUNO | 1943 | 00:39.4 | 165 |
| 61 | MASO ALESSANDRO | 1977 | 00:41.9 | 141 |
| 62 | PICCOLI IVANO | 1971 | 00:42.6 | nuovo |
| 64 | FRARE MAURIZIO | 1966 | 00:59.2 | 129 |

**100 Dorso — Assoluti Femmine Master** — race da creare, race_event 18

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 2 | LAZZARIN CRISTINA | 1984 | 01:20.4 | 138 |
| 3 | BETTIOL GIULIA | 1985 | 01:32.2 | 115 |
| 9 | SCHIEVENE FEDERICA | 1976 | 01:57.7 | nuovo |

**100 Dorso — Assoluti Maschi Master** — race da creare, race_event 18

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 1 | BARRO PAOLO | 1980 | 01:05.5 | 112 |
| 3 | FONTANA NICO | 1979 | 01:08.0 | 61 |
| 4 | DA ROS GABRIELE | 1983 | 01:10.4 | nuovo |
| 15 | CAMPODALL'ORTO ANDREA | 1980 | 01:41.4 | 172 |

**400 Stile Libero — Assoluti Femmine Master** — race 17445 (esistente)

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 7 | SALVALAGGIO CATIA | 1964 | 07:18.1 | nuovo |

**400 Stile Libero — Assoluti Maschi Master** — race da creare, race_event 10

| pos | atleta | anno | tempo | anagrafica |
|---|---|---|---|---|
| 7 | BLASI STEFANO | 1983 | 05:39.8 | nuovo |
| 15 | MENIS ALESSANDRO | 1973 | 06:05.2 | nuovo |
| 16 | PAPA IVAN | 1974 | 06:05.3 | nuovo |
| 17 | GERARDO SIMONE | 1979 | 06:12.1 | nuovo |


## 6. Cosa mi serve da te

1. Via libera all'import: 1 manifestazione, 26 gare, 22 atleti, 177 risultati.
2. **Belluno**: accorpo tutto nella competition 29 spostando il risultato di Vedovelli e disattivando
   la 1215 doppia, oppure lascio le due competitions separate?
3. Rinomino le quattro competitions col `type` generico (1213, 1214, 1216, 1217) come ho fatto per il
   2003?
