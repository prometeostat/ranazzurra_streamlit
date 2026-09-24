# Report preliminare import PDF 2008

Cinque riepiloghi natatoria/Siteland del 2008. **Nessuna scrittura eseguita**, come da procedura.

## 0. Il primo risultato del controllo: uno dei cinque PDF è già dentro

`riepilogo_risultati_spresiano_20082.pdf` è **identico byte per byte** (stesso md5 del testo estratto)
a `riepilogo_risultati_spresiano_2008.pdf`, quello che avevamo importato nel primo lotto storico e che
è diventato la competition **1481** (14/06/2008, Spresiano, vasca 50, "Finale Circuito Masters
Provincie BL-TV-VE"). Ho confrontato riga per riga le 30 righe Ranazzurra del PDF con le 27 già a
database: coincidono tutte, e le 3 che mancano sono esattamente le tre righe ASS (VENERANDO sui 50
farfalla, PRADELLA sui 50 rana, TALAMINI sui 50 stile), che la convenzione consolidata non importa.
Su questo file **non c'è niente da fare**: lo escludo dal piano.

Restano quattro manifestazioni vere.

## 1. Manifestazioni: tre esistono già, una è nuova

Su questo lotto la trappola delle date sovrapposte si è presentata tre volte su quattro, e in tutti i
casi la manifestazione master era già a database come record generico scaricato da finveneto. L'ho
verificata incrociando data, cronometraggio, categoria e soprattutto i risultati già presenti, non solo
la data.

| PDF | data | sede | vasca | Cron | competition | come l'ho riconosciuta |
|---|---|---|---|---|---|---|
| sdona_2008 | 02/02/2008 | San Donà di Piave | 25 | A | **da creare** | nessuna competition in quella data |
| oderzo_2008 | 16/03/2008 | Oderzo (TV) | 25 | M | **1222** | VEDOVELLI DANILA 50 sl 00:47.9 e 100 sl 01:51.3, identiche nel PDF |
| belluno_2008 | 18/05/2008 | Piscina di Belluno | 25 | A | **1223** | VEDOVELLI DANILA 50 sl 00:47.3 e 200 sl 03:50.4, identiche nel PDF |
| valdobbiadene_2008 | 30/11/2008 | Valdobbiadene | 25 | M | **1402** | FOLTRAN FRANCESCO 50 sl 00:32.6 e 50 dorso 00:39.2, identiche nel PDF |

Nelle stesse date ci sono altre competitions che ho **escluso** dopo averle guardate dentro: la 1377
(16/03/2008) e la 1036 (18/05/2008) contengono gare di categoria P2/P3 ed Esordienti con MASIN e
MONDELLI, sono manifestazioni giovanili diverse e le lascio stare.

Nomi che proporrei, seguendo lo stile già usato per 1218/1219/1221:

- 1222 → `3ª Giornata Circuito Master 2007/08 - Oderzo`
- 1223 → `Trofeo Master ASD Nuoto Belluno - Belluno` (il PDF ha solo l'intestazione "ASD NUOTO BELLUNO")
- 1402 → `1ª Giornata Circuito Master 2008/09 - Valdobbiadene`
- nuova → `2ª Giornata Circuito Master 2007/08 - San Donà di Piave`, vasca 25, timing AUTOMATICO,
  scraping_website_id 2, web_id NULL (stessa impostazione di 1481 e 1491)

## 2. Atleti: 40 su 43 già in anagrafica, zero casi ambigui

198 righe Ranazzurra in tutto, 43 atleti distinti. Il match contro l'anagrafica (riletta dal database
adesso, non dalla copia locale) dà **40 trovati, 0 dubbi, 3 assenti**. I tre assenti hanno una cosa in
comune, ed è il punto che ti chiedo di decidere.

## 3. La novità vera: a Valdobbiadene compare "RANAZZURRA SPRESIANO"

Nel riepilogo del 30/11/2008 gli atleti Ranazzurra sono divisi fra **due sigle diverse nello stesso
documento**: nove sotto `RANAZZURRA SPRESIANO`, sei sotto `RANAZZURRA S.S.D.`. Nessun atleta compare
sotto entrambe. La sigla Spresiano non era mai apparsa nei 25 riepiloghi precedenti, dal 2003 al
giugno 2008.

| atleta | anno | id anagrafica | sigla a Valdobbiadene |
|---|---|---|---|
| BETTIOL GIULIA | 1985 | 115 | SPRESIANO |
| BINOTO DENIS | 1975 | **non in anagrafica** | SPRESIANO |
| FURLAN CARLOTTA | 1988 | 130 | SPRESIANO |
| MENIS ALESSANDRO | 1973 | 195 | SPRESIANO |
| MILANESE STEFANIA | 1986 | 142 | SPRESIANO |
| RONSIVALLE GUIDO | 1981 | 150 | SPRESIANO |
| BARBON LINA | 1965 | **non in anagrafica** | SPRESIANO |
| BRINO WALTER | 1963 | **non in anagrafica** | SPRESIANO |
| TORRESAN PAOLO | 1958 | 158 | SPRESIANO |
| ANZANELLO STEFANO | 1975 | 109 | S.S.D. |
| CAMERIN SEBASTIANO | 1978 | 119 | S.S.D. |
| FACCHINI STEFANO | 1959 | 126 | S.S.D. |
| FOLTRAN FRANCESCO | 1987 | 48 | S.S.D. |
| SALVIATO ANDREA | 1988 | 152 | S.S.D. |
| ZARAMELLA BRUNO | 1943 | 165 | S.S.D. |

Sei dei nove "Spresiano" sono atleti nostri con risultati già a database, e cinque mesi prima, alla
finale del 14/06/2008, MILANESE, FURLAN, RONSIVALLE e TORRESAN nuotavano ancora come `RANAZZURRA
S.S.D.`. Sembra quindi una scissione o un tesseramento su due società affiliate a partire dalla
stagione 2008/09, non un'omonimia. Ma non lo so, e non lo deduco da solo: **decidi tu**.

Cosa cambia in pratica: sono 15 righe su 26 a Valdobbiadene. Se le escludiamo, spariscono anche
cinque gare intere (50 stile femmine, 50 farfalla femmine, 50 dorso femmine, 400 stile maschi, 400
stile femmine, tutte composte solo da atleti Spresiano) e i tre atleti nuovi non vanno censiti.

La mia proposta è **importarle**, perché sono le carriere degli stessi nuotatori e spezzarle a metà
stagione rende inutilizzabili i personali; però è una tua chiamata, non mia.

## 4. Le staffette di Belluno, di nuovo, non portano niente

Come nel 2007, il riepilogo di Belluno ha due fogli di staffetta 4x50 stile libero, maschile e
femminile, e anche stavolta **tutte le squadre iscritte sono ASS**: nessun tempo, nessuna posizione,
gara annunciata e non disputata. Le nostre due formazioni sarebbero LAZZARIN/BETTIOL/MILANESE/GRANZIERA
e VECCHIATO/FILIPPI/FIORENTINI/CALDATO. Non creo le due races e non importo le otto righe, coerente
con quanto fatto l'anno scorso.

## 5. Risultati

| manifestazione | righe | ASS | già a DB | da inserire | gare da creare | gare esistenti |
|---|---|---|---|---|---|---|
| sdona_2008 | 40 | 3 | 0 | 37 | 5 | 0 |
| oderzo_2008 | 47 | 1 | 2 | 44 | 4 | 2 |
| belluno_2008 | 55 | 0 | 2 | 53 | 4 | 2 |
| valdobbiadene_2008 | 26 | 0 | 2 | 24 | 6 | 2 |
| **totale** | **168** | **4** | **6** | **158** | **19** | **6** |

Le 6 righe già a database sono le quattro di VEDOVELLI e le due di FOLTRAN citate sopra, e i tempi
coincidono al decimo: nessuna discordanza da sanare, riuso le loro races.

I quattro ASS (FACCHINI sui 50 stile e CALESSO sui 100 rana a San Donà, GIRARDI ERMES sui 100 dorso a
San Donà, FRARE sui 50 stile a Oderzo) non si importano. C'è invece **un RIT**, FACCHINI STEFANO sui
200 stile a Belluno, gara disputata: va inserito con `final_time` NULL, come SQU e RIT degli altri lotti.

San Donà ha una gara, i 100 rana femmine, senza nessuna Ranazzurra: non creo la race, come sempre.

Tempi: 163 tempi validi, nessuno anomalo. Il più lento in assoluto è il 50 stile di FRARE MAURIZIO in
01:01.0 a Belluno, il più veloce il 50 stile di CALDATO SIMONE in 00:24.4, entrambi plausibili. Niente
di paragonabile al 14:56.7 di ZANINI che resta aperto dal 2004.

Sulla categoria: nessun atleta è sotto i 20 anni alla data della manifestazione (i più giovani sono
del 1988, quindi ventenni nel 2008), quindi nessun "mini" da calcolare. La colonna `group` resta NULL
come in tutto lo storico.

## 6. Stato del database adesso

Le quattro sequence sono allineate al max(id) — athletes 221, races 22441, athlete_races 7994,
competitions 1491 — e i conteggi (189 atleti, 2253 races, 5448 risultati) sono esattamente quelli
lasciati dal lotto 2007: nessun'altra sessione ha scritto nel frattempo. Ricontrollerò comunque
subito prima di scrivere.

## 7. Cosa scriverei, in ordine

1. 3 UPDATE sui nomi di 1222, 1223, 1402
2. 1 INSERT competition (San Donà 02/02/2008)
3. 3 INSERT athletes (BINOTO DENIS 1975 M, BARBON LINA 1965 F, BRINO WALTER 1963 M — nati 01/01,
   company 37, is_deleted true come gli altri storici) **solo se accetti le righe Spresiano**
4. 19 INSERT races
5. 158 INSERT athlete_races
6. verifica con checksum md5 per competition, Python contro Postgres, e report finale

---

## 8. Dettaglio completo dei risultati

### sdona_2008 — 2008-02-02, San Donà di Piave, vasca 25, Cron A
titolo PDF: 2^ GIORNATA CIRCUITO MASTER  |  competition: NEW

**50 Stile Libero — Assoluti Maschi Master** — race DA CREARE, race_event 7
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 1 | CALDATO SIMONE | 1985 | S.S.D. | 00:24.40 | 117 | da inserire |
| 2 | FIORENTINI PABLO | 1985 | S.S.D. | 00:24.80 | 128 | da inserire |
| 7 | BARRO PAOLO | 1980 | S.S.D. | 00:26.30 | 112 | da inserire |
| 7 | VECCHIATO SIMONE | 1976 | S.S.D. | 00:26.30 | 160 | da inserire |
| 10 | ARDUINO DAVIDE | 1975 | S.S.D. | 00:26.70 | 110 | da inserire |
| 10 | NAVE DANIELE | 1981 | S.S.D. | 00:26.70 | 143 | da inserire |
| 14 | FILIPPI FRANCESCO | 1980 | S.S.D. | 00:27.90 | 60 | da inserire |
| 15 | SILVESTRIN STEFANO | 1985 | S.S.D. | 00:28.10 | 218 | da inserire |
| 18 | BAZZO FABIO | 1981 | S.S.D. | 00:28.50 | 113 | da inserire |
| 21 | ZANETTI LORENZO | 1982 | S.S.D. | 00:28.90 | 220 | da inserire |
| 23 | MENIS ALESSANDRO | 1973 | S.S.D. | 00:29.20 | 195 | da inserire |
| 26 | SALVIATO ANDREA | 1988 | S.S.D. | 00:29.60 | 152 | da inserire |
| 34 | PINESE MASSIMO | 1977 | S.S.D. | 00:30.50 | 146 | da inserire |
| 48 | CAMERIN SEBASTIANO | 1978 | S.S.D. | 00:32.70 | 119 | da inserire |
| 73 | ZARAMELLA BRUNO | 1943 | S.S.D. | 00:38.60 | 165 | da inserire |
| 74 | GIRARDI ERMES | 1961 | S.S.D. | 00:39.10 | 134 | da inserire |
| 78 | MASO ALESSANDRO | 1977 | S.S.D. | 00:42.20 | 141 | da inserire |

**50 Stile Libero — Assoluti Femmine Master** — race DA CREARE, race_event 7
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 3 | LAZZARIN CRISTINA | 1984 | S.S.D. | 00:30.70 | 138 | da inserire |
| 5 | GRANZIERA SERENA | 1982 | S.S.D. | 00:32.00 | 135 | da inserire |
| 6 | MILANESE STEFANIA | 1986 | S.S.D. | 00:32.50 | 142 | da inserire |
| 7 | BETTIOL GIULIA | 1985 | S.S.D. | 00:32.70 | 115 | da inserire |
| 17 | FURLAN CARLOTTA | 1988 | S.S.D. | 00:35.40 | 130 | da inserire |

**100 Rana — Assoluti Maschi Master** — race DA CREARE, race_event 21
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 4 | NAVE DANIELE | 1981 | S.S.D. | 01:15.20 | 143 | da inserire |
| 6 | FIORENTINI PABLO | 1985 | S.S.D. | 01:18.20 | 128 | da inserire |
| 7 | BAZZO FABIO | 1981 | S.S.D. | 01:21.90 | 113 | da inserire |
| 11 | VECCHIATO SIMONE | 1976 | S.S.D. | 01:24.70 | 160 | da inserire |

**100 Dorso — Assoluti Maschi Master** — race DA CREARE, race_event 18
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 1 | CALDATO SIMONE | 1985 | S.S.D. | 01:06.00 | 117 | da inserire |
| 2 | BARRO PAOLO | 1980 | S.S.D. | 01:06.20 | 112 | da inserire |
| 3 | ARDUINO DAVIDE | 1975 | S.S.D. | 01:08.60 | 110 | da inserire |
| 4 | FILIPPI FRANCESCO | 1980 | S.S.D. | 01:09.90 | 60 | da inserire |
| 11 | CAMERIN SEBASTIANO | 1978 | S.S.D. | 01:22.70 | 119 | da inserire |
| 12 | MENIS ALESSANDRO | 1973 | S.S.D. | 01:24.00 | 195 | da inserire |
| 16 | SILVESTRIN STEFANO | 1985 | S.S.D. | 01:28.50 | 218 | da inserire |
| 21 | SALVIATO ANDREA | 1988 | S.S.D. | 01:30.10 | 152 | da inserire |

**100 Dorso — Assoluti Femmine Master** — race DA CREARE, race_event 18
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 1 | LAZZARIN CRISTINA | 1984 | S.S.D. | 01:16.90 | 138 | da inserire |
| 6 | BETTIOL GIULIA | 1985 | S.S.D. | 01:27.10 | 115 | da inserire |
| 10 | FURLAN CARLOTTA | 1988 | S.S.D. | 01:35.90 | 130 | da inserire |

### oderzo_2008 — 2008-03-16, Oderzo, vasca 25, Cron M
titolo PDF: 3° G.TA attività MASTER sx piave  |  competition: 1222

**50 Stile Libero — Assoluti Maschi Master** — race DA CREARE, race_event 7
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 1 | CALDATO SIMONE | 1985 | S.S.D. | 00:24.9 | 117 | da inserire |
| 6 | NAVE DANIELE | 1981 | S.S.D. | 00:26.4 | 143 | da inserire |
| 9 | VECCHIATO SIMONE | 1976 | S.S.D. | 00:26.7 | 160 | da inserire |
| 10 | ARDUINO DAVIDE | 1975 | S.S.D. | 00:27.0 | 110 | da inserire |
| 14 | FILIPPI FRANCESCO | 1980 | S.S.D. | 00:27.9 | 60 | da inserire |
| 16 | BAZZO FABIO | 1981 | S.S.D. | 00:28.6 | 113 | da inserire |
| 21 | SALVIATO ANDREA | 1988 | S.S.D. | 00:29.4 | 152 | da inserire |
| 22 | MENIS ALESSANDRO | 1973 | S.S.D. | 00:29.5 | 195 | da inserire |
| 30 | PINESE MASSIMO | 1977 | S.S.D. | 00:30.7 | 146 | da inserire |
| 35 | CAMERIN SEBASTIANO | 1978 | S.S.D. | 00:31.3 | 119 | da inserire |
| 39 | FACCHINI STEFANO | 1959 | S.S.D. | 00:32.2 | 126 | da inserire |
| 53 | BELLAGAMBA UMBERTO | 1963 | S.S.D. | 00:34.5 | 114 | da inserire |
| 57 | TORRESAN PAOLO | 1958 | S.S.D. | 00:36.2 | 158 | da inserire |
| 62 | ZARAMELLA BRUNO | 1943 | S.S.D. | 00:38.2 | 165 | da inserire |
| 65 | MASO ALESSANDRO | 1977 | S.S.D. | 00:42.2 | 141 | da inserire |

**50 Stile Libero — Assoluti Femmine Master** — race 17479 (esistente), race_event 7
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 2 | LAZZARIN CRISTINA | 1984 | S.S.D. | 00:30.6 | 138 | da inserire |
| 4 | MILANESE STEFANIA | 1986 | S.S.D. | 00:31.8 | 142 | da inserire |
| 9 | DALLE CRODE LISA | 1987 | S.S.D. | 00:32.8 | 121 | da inserire |
| 16 | FURLAN CARLOTTA | 1988 | S.S.D. | 00:34.8 | 130 | da inserire |
| 23 | VENERANDO MANUELA | 1968 | S.S.D. | 00:37.8 | 161 | da inserire |
| 27 | SALVALAGGIO CATIA | 1964 | S.S.D. | 00:40.0 | 199 | da inserire |
| 39 | VEDOVELLI DANILA | 1957 | S.S.D. | 00:47.9 | 14 | gia a DB |

**50 Rana — Assoluti Maschi Master** — race DA CREARE, race_event 20
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 5 | NAVE DANIELE | 1981 | S.S.D. | 00:33.9 | 143 | da inserire |
| 21 | BELLAGAMBA UMBERTO | 1963 | S.S.D. | 00:40.9 | 114 | da inserire |
| 35 | PINESE MASSIMO | 1977 | S.S.D. | 00:43.4 | 146 | da inserire |
| 44 | GIRARDI ERMES | 1961 | S.S.D. | 00:47.3 | 134 | da inserire |

**50 Rana — Assoluti Femmine Master** — race DA CREARE, race_event 20
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 15 | VENERANDO MANUELA | 1968 | S.S.D. | 00:47.9 | 161 | da inserire |
| 16 | BETTIOL GIULIA | 1985 | S.S.D. | 00:48.4 | 115 | da inserire |

**100 Stile Libero — Assoluti Maschi Master** — race DA CREARE, race_event 8
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 2 | CALDATO SIMONE | 1985 | S.S.D. | 00:56.7 | 117 | da inserire |
| 5 | VECCHIATO SIMONE | 1976 | S.S.D. | 00:59.2 | 160 | da inserire |
| 8 | ARDUINO DAVIDE | 1975 | S.S.D. | 01:00.1 | 110 | da inserire |
| 12 | FILIPPI FRANCESCO | 1980 | S.S.D. | 01:02.9 | 60 | da inserire |
| 14 | BAZZO FABIO | 1981 | S.S.D. | 01:03.7 | 113 | da inserire |
| 17 | MENIS ALESSANDRO | 1973 | S.S.D. | 01:06.3 | 195 | da inserire |
| 29 | SALVIATO ANDREA | 1988 | S.S.D. | 01:09.9 | 152 | da inserire |
| 30 | CAMERIN SEBASTIANO | 1978 | S.S.D. | 01:10.1 | 119 | da inserire |
| 54 | FACCHINI STEFANO | 1959 | S.S.D. | 01:17.5 | 126 | da inserire |
| 61 | GIRARDI ERMES | 1961 | S.S.D. | 01:24.9 | 134 | da inserire |
| 68 | ZARAMELLA BRUNO | 1943 | S.S.D. | 01:32.1 | 165 | da inserire |

**100 Stile Libero — Assoluti Femmine Master** — race 17483 (esistente), race_event 8
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 2 | LAZZARIN CRISTINA | 1984 | S.S.D. | 01:07.3 | 138 | da inserire |
| 6 | MILANESE STEFANIA | 1986 | S.S.D. | 01:13.3 | 142 | da inserire |
| 8 | DALLE CRODE LISA | 1987 | S.S.D. | 01:14.7 | 121 | da inserire |
| 9 | BETTIOL GIULIA | 1985 | S.S.D. | 01:15.1 | 115 | da inserire |
| 14 | FURLAN CARLOTTA | 1988 | S.S.D. | 01:19.2 | 130 | da inserire |
| 21 | SALVALAGGIO CATIA | 1964 | S.S.D. | 01:31.7 | 199 | da inserire |
| 27 | VEDOVELLI DANILA | 1957 | S.S.D. | 01:51.3 | 14 | gia a DB |

### belluno_2008 — 2008-05-18, Belluno, vasca 25, Cron A
titolo PDF: ASD NUOTO BELLUNO  |  competition: 1223

**50 Stile Libero — Assoluti Femmine Master** — race 17484 (esistente), race_event 7
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 4 | LAZZARIN CRISTINA | 1984 | S.S.D. | 00:30.80 | 138 | da inserire |
| 5 | MILANESE STEFANIA | 1986 | S.S.D. | 00:32.10 | 142 | da inserire |
| 8 | GRANZIERA SERENA | 1982 | S.S.D. | 00:32.60 | 135 | da inserire |
| 9 | DALLE CRODE LISA | 1987 | S.S.D. | 00:32.80 | 121 | da inserire |
| 9 | BETTIOL GIULIA | 1985 | S.S.D. | 00:32.80 | 115 | da inserire |
| 14 | FURLAN CARLOTTA | 1988 | S.S.D. | 00:34.90 | 130 | da inserire |
| 22 | VENERANDO MANUELA | 1968 | S.S.D. | 00:38.60 | 161 | da inserire |
| 32 | VEDOVELLI DANILA | 1957 | S.S.D. | 00:47.30 | 14 | gia a DB |

**50 Stile Libero — Assoluti Maschi Master** — race DA CREARE, race_event 7
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 1 | CALDATO SIMONE | 1985 | S.S.D. | 00:24.40 | 117 | da inserire |
| 4 | FIORENTINI PABLO | 1985 | S.S.D. | 00:25.80 | 128 | da inserire |
| 7 | ARDUINO DAVIDE | 1975 | S.S.D. | 00:26.30 | 110 | da inserire |
| 8 | NAVE DANIELE | 1981 | S.S.D. | 00:26.80 | 143 | da inserire |
| 13 | BAZZO FABIO | 1981 | S.S.D. | 00:28.30 | 113 | da inserire |
| 15 | CALESSO GIORGIO | 1983 | S.S.D. | 00:28.60 | 118 | da inserire |
| 15 | RONSIVALLE GUIDO | 1981 | S.S.D. | 00:28.60 | 150 | da inserire |
| 18 | MENIS ALESSANDRO | 1973 | S.S.D. | 00:29.00 | 195 | da inserire |
| 19 | GERARDO SIMONE | 1979 | S.S.D. | 00:29.30 | 191 | da inserire |
| 28 | SALVIATO ANDREA | 1988 | S.S.D. | 00:30.40 | 152 | da inserire |
| 30 | CAMERIN SEBASTIANO | 1978 | S.S.D. | 00:30.50 | 119 | da inserire |
| 32 | PINESE MASSIMO | 1977 | S.S.D. | 00:30.60 | 146 | da inserire |
| 41 | FACCHINI STEFANO | 1959 | S.S.D. | 00:32.10 | 126 | da inserire |
| 44 | CHECCHIN MATTEO | 1986 | S.S.D. | 00:32.60 | 120 | da inserire |
| 58 | TORRESAN PAOLO | 1958 | S.S.D. | 00:35.50 | 158 | da inserire |
| 64 | PRADELLA GIANPAOLO | 1961 | S.S.D. | 00:37.50 | 149 | da inserire |
| 66 | ZARAMELLA BRUNO | 1943 | S.S.D. | 00:39.20 | 165 | da inserire |
| 67 | MASO ALESSANDRO | 1977 | S.S.D. | 00:43.20 | 141 | da inserire |
| 69 | FRARE MAURIZIO | 1966 | S.S.D. | 01:01.00 | 129 | da inserire |

**100 Misti — Assoluti Femmine Master** — race DA CREARE, race_event 1
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 1 | LAZZARIN CRISTINA | 1984 | S.S.D. | 01:17.80 | 138 | da inserire |
| 6 | MILANESE STEFANIA | 1986 | S.S.D. | 01:25.20 | 142 | da inserire |
| 17 | VENERANDO MANUELA | 1968 | S.S.D. | 01:38.70 | 161 | da inserire |

**100 Misti — Assoluti Maschi Master** — race DA CREARE, race_event 1
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 6 | FIORENTINI PABLO | 1985 | S.S.D. | 01:05.60 | 128 | da inserire |
| 8 | ARDUINO DAVIDE | 1975 | S.S.D. | 01:07.70 | 110 | da inserire |
| 9 | NAVE DANIELE | 1981 | S.S.D. | 01:07.90 | 143 | da inserire |
| 10 | FILIPPI FRANCESCO | 1980 | S.S.D. | 01:10.20 | 60 | da inserire |
| 11 | VECCHIATO SIMONE | 1976 | S.S.D. | 01:10.60 | 160 | da inserire |
| 15 | CHECCHIN MATTEO | 1986 | S.S.D. | 01:13.60 | 120 | da inserire |
| 20 | CAMERIN SEBASTIANO | 1978 | S.S.D. | 01:16.10 | 119 | da inserire |
| 24 | CALESSO GIORGIO | 1983 | S.S.D. | 01:18.20 | 118 | da inserire |
| 25 | SALVIATO ANDREA | 1988 | S.S.D. | 01:20.00 | 152 | da inserire |
| 31 | GERARDO SIMONE | 1979 | S.S.D. | 01:22.50 | 191 | da inserire |
| 34 | ANZANELLO STEFANO | 1975 | S.S.D. | 01:24.60 | 109 | da inserire |

**200 Stile Libero — Assoluti Femmine Master** — race 17488 (esistente), race_event 9
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 11 | DALLE CRODE LISA | 1987 | S.S.D. | 02:49.20 | 121 | da inserire |
| 12 | BETTIOL GIULIA | 1985 | S.S.D. | 02:51.80 | 115 | da inserire |
| 13 | FURLAN CARLOTTA | 1988 | S.S.D. | 03:00.00 | 130 | da inserire |
| 22 | VEDOVELLI DANILA | 1957 | S.S.D. | 03:50.40 | 14 | gia a DB |

**200 Stile Libero — Assoluti Maschi Master** — race DA CREARE, race_event 9
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 4 | CALDATO SIMONE | 1985 | S.S.D. | 02:10.80 | 117 | da inserire |
| 5 | VECCHIATO SIMONE | 1976 | S.S.D. | 02:14.90 | 160 | da inserire |
| 10 | BAZZO FABIO | 1981 | S.S.D. | 02:21.40 | 113 | da inserire |
| 11 | FILIPPI FRANCESCO | 1980 | S.S.D. | 02:24.30 | 60 | da inserire |
| 13 | RONSIVALLE GUIDO | 1981 | S.S.D. | 02:27.60 | 150 | da inserire |
| 21 | MENIS ALESSANDRO | 1973 | S.S.D. | 02:40.50 | 195 | da inserire |
| 33 | ANZANELLO STEFANO | 1975 | S.S.D. | 02:52.60 | 109 | da inserire |
| 44 | PRADELLA GIANPAOLO | 1961 | S.S.D. | 03:19.10 | 149 | da inserire |
| 49 | ZARAMELLA BRUNO | 1943 | S.S.D. | 03:57.10 | 165 | da inserire |
| - | FACCHINI STEFANO | 1959 | S.S.D. | RIT | 126 | da inserire |

### valdobbiadene_2008 — 2008-11-30, Valdobbiadene, vasca 25, Cron M
titolo PDF: 1^ Giornata Circuito Master  |  competition: 1402

**50 Stile Libero — Assoluti Maschi Master** — race 21256 (esistente), race_event 7
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 19 | RONSIVALLE GUIDO | 1981 | SPRESIANO | 00:29.2 | 150 | da inserire |
| 21 | MENIS ALESSANDRO | 1973 | SPRESIANO | 00:29.4 | 195 | da inserire |
| 23 | BINOTO DENIS | 1975 | SPRESIANO | 00:29.6 | NUOVO | da inserire |
| 24 | SALVIATO ANDREA | 1988 | S.S.D. | 00:29.8 | 152 | da inserire |
| 25 | CAMERIN SEBASTIANO | 1978 | S.S.D. | 00:30.2 | 119 | da inserire |
| 45 | FOLTRAN FRANCESCO | 1987 | S.S.D. | 00:32.6 | 48 | gia a DB |
| 50 | FACCHINI STEFANO | 1959 | S.S.D. | 00:33.0 | 126 | da inserire |
| 64 | TORRESAN PAOLO | 1958 | SPRESIANO | 00:35.5 | 158 | da inserire |
| 68 | BRINO WALTER | 1963 | SPRESIANO | 00:36.8 | NUOVO | da inserire |
| 75 | ZARAMELLA BRUNO | 1943 | S.S.D. | 00:39.3 | 165 | da inserire |

**50 Stile Libero — Assoluti Femmine Master** — race DA CREARE, race_event 7
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 7 | MILANESE STEFANIA | 1986 | SPRESIANO | 00:32.8 | 142 | da inserire |
| 10 | FURLAN CARLOTTA | 1988 | SPRESIANO | 00:33.7 | 130 | da inserire |
| 27 | BARBON LINA | 1965 | SPRESIANO | 00:46.1 | NUOVO | da inserire |

**50 Farfalla — Assoluti Maschi Master** — race DA CREARE, race_event 23
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 13 | CAMERIN SEBASTIANO | 1978 | S.S.D. | 00:32.0 | 119 | da inserire |
| 17 | ANZANELLO STEFANO | 1975 | S.S.D. | 00:34.4 | 109 | da inserire |
| 22 | BINOTO DENIS | 1975 | SPRESIANO | 00:35.7 | NUOVO | da inserire |

**50 Farfalla — Assoluti Femmine Master** — race DA CREARE, race_event 23
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 3 | MILANESE STEFANIA | 1986 | SPRESIANO | 00:37.8 | 142 | da inserire |

**50 Dorso — Assoluti Maschi Master** — race 21260 (esistente), race_event 17
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 6 | SALVIATO ANDREA | 1988 | S.S.D. | 00:38.1 | 152 | da inserire |
| 7 | ANZANELLO STEFANO | 1975 | S.S.D. | 00:38.3 | 109 | da inserire |
| 8 | FOLTRAN FRANCESCO | 1987 | S.S.D. | 00:39.2 | 48 | gia a DB |
| 19 | FACCHINI STEFANO | 1959 | S.S.D. | 00:43.3 | 126 | da inserire |

**50 Dorso — Assoluti Femmine Master** — race DA CREARE, race_event 17
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 6 | BETTIOL GIULIA | 1985 | SPRESIANO | 00:39.1 | 115 | da inserire |
| 7 | FURLAN CARLOTTA | 1988 | SPRESIANO | 00:42.6 | 130 | da inserire |

**400 Stile Libero — Assoluti Maschi Master** — race DA CREARE, race_event 10
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 9 | RONSIVALLE GUIDO | 1981 | SPRESIANO | 05:34.1 | 150 | da inserire |
| 10 | MENIS ALESSANDRO | 1973 | SPRESIANO | 05:37.8 | 195 | da inserire |

**400 Stile Libero — Assoluti Femmine Master** — race DA CREARE, race_event 10
| pos | atleta | anno | societa | tempo | anagrafica | stato |
|---|---|---|---|---|---|---|
| 6 | BETTIOL GIULIA | 1985 | SPRESIANO | 06:03.5 | 115 | da inserire |
