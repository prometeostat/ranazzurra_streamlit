# Report preliminare import PDF Aquasport 2025/26

Sei riepiloghi natatoria, confronto con il DB `swim` (Aiven, defaultdb/public).
Nessuna scrittura eseguita: il report e' solo di verifica.

## 1. Manifestazioni

Tutte e sei risultano gia' a DB, nessuna da inserire, nessun duplicato.

| PDF | data | sede | vasca | fogli | competition | web_id | nome a DB |
|---|---|---|---|---|---|---|---|
| it1 | 2025-11-09 | Montebelluna | 25 m | 13 | **10** | 1780 | 1ª Giornata Aquasport - Montebelluna |
| it2 | 2026-01-18 | Conegliano V.to | 25 m | 24 | **15** | 1807 | 2ª Giornata Circuito Aquasport 2026 Conegliano |
| it3 | 2026-02-07 | Spresiano | 25 m | 10 | **17** | 1852 | 3ª Giornata Circuito Aquasport 2026 - Spresiano |
| it4 | 2026-03-15 | Preganziol | 25 m | 13 | **16** | 1863 | 4ª G.ta Circuito Aquasport TV - Preganziol |
| it5 | 2026-04-19 | Mirano | 25 m | 12 | **22** | 1899 | 5ª Giornata Circuito AQUASPORT |
| it6 | 2026-05-09 | Monastier | 50 m | 12 | **23** | 1919 | 6ª Giornata Circuito AQUASPORT |

Tutte e sei hanno `scraping_website_id` coerente (1 per la prima, 2 per le altre cinque: natatoria).
Le 38 `races` collegate coprono tutte le gare in cui compaiono atleti Ranazzurra: nessuna gara da creare.

## 2. Anagrafica atleti

Nei sei PDF compaiono **58 atleti distinti** di RANAZZURRA CONEGLIANO SSD.

- **32 gia' presenti** in `athletes` (company_id 37), match esatto su cognome+nome normalizzati e anno di nascita coerente.
- **1 match non letterale, confermato**: `GALBINCEA EMMA MARIA` (PDF) -> id 15 `GALBINCEA EMMA`, nata 2009-04-04, anno coerente. Nessun altro GALBINCEA a DB. Lo tratto come lo stesso atleta.
- **0 ambigui**.
- **26 non trovati**, tutti propaganda/giovanili. Il sesso e' dedotto dall'intestazione del foglio (Assoluti Femmine / Maschi), sempre univoco. Della data di nascita il PDF da' solo l'anno.

| cognome nome | anno | sesso | giornate | risultati | gare |
|---|---|---|---|---|---|
| BERNARDI GIULIO | 2007 | M | 2 | 4 | 100 Stile Libero, 50 Dorso |
| BERTAZZON MATTEO | 2011 | M | 3 | 6 | 100 Misti, 100 Stile Libero, 50 Dorso |
| BEUKEMA TERESA | 2010 | F | 1 | 2 | 100 Misti, 50 Farfalla |
| BOTTEON NICOLA | 2009 | M | 4 | 8 | 100 Rana, 100 Stile Libero, 400 Stile Libero, 50 Dorso, 50 Rana, 50 Stile Libero |
| BRAVIN GABRIELE | 2011 | M | 5 | 13 | 100 Misti, 100 Rana, 100 Stile Libero, 200 Rana, 4x50 Stile Libero, 50 Farfalla, 50 Rana, 50 Stile Libero, 8x50 Stile Libero |
| BREDA GIORDANO | 2011 | M | 2 | 4 | 50 Dorso, 50 Rana, 50 Stile Libero |
| CARLESSO MATTIA | 2010 | M | 2 | 4 | 100 Misti, 50 Stile Libero |
| D'ALISE SPARTACO | 2012 | M | 5 | 10 | 100 Stile Libero, 200 Dorso, 200 Stile Libero, 50 Dorso, 50 Rana, 50 Stile Libero |
| DAL POS SAMUELE | 2007 | M | 1 | 2 | 100 Rana, 50 Stile Libero |
| GAVA LEONE | 2011 | M | 2 | 4 | 100 Misti, 50 Stile Libero |
| GONG YISHENG MATTEO | 2012 | M | 4 | 8 | 100 Dorso, 100 Stile Libero, 50 Dorso, 50 Stile Libero |
| MASCELLANI IRENE | 2012 | F | 4 | 8 | 100 Misti, 100 Rana, 50 Farfalla, 50 Rana |
| MASCHIO MARTA | 2007 | F | 1 | 2 | 50 Dorso, 50 Stile Libero |
| MODOLO ESTER | 2010 | F | 5 | 12 | 100 Dorso, 100 Farfalla, 200 Dorso, 4x50 Stile Libero, 50 Dorso, 50 Farfalla, 50 Stile Libero, 8x50 Stile Libero |
| PAGOTTO GAIA | 2012 | F | 4 | 8 | 100 Misti, 100 Stile Libero, 50 Dorso, 50 Farfalla, 50 Stile Libero |
| PALFERENT ALESSIA | 2008 | F | 5 | 10 | 100 Misti, 100 Stile Libero, 200 Stile Libero, 50 Dorso, 50 Farfalla, 50 Stile Libero |
| PERIN LEONARDO | 2008 | M | 6 | 13 | 100 Farfalla, 100 Misti, 100 Stile Libero, 200 Misti, 200 Rana, 200 Stile Libero, 400 Stile Libero, 4x50 Stile Libero, 50 Dorso, 50 Farfalla, 50 Stile Libero |
| PIARULLI FILIPPO | 2011 | M | 6 | 16 | 100 Dorso, 100 Misti, 100 Stile Libero, 200 Dorso, 200 Misti, 200 Stile Libero, 4x50 Misti, 4x50 Stile Libero, 50 Dorso, 50 Farfalla, 50 Stile Libero, 8x50 Stile Libero |
| POL ADELE | 2012 | F | 3 | 6 | 100 Misti, 200 Stile Libero, 400 Stile Libero, 50 Dorso |
| REBULI TOMMASO | 2012 | M | 5 | 10 | 100 Rana, 100 Stile Libero, 200 Stile Libero, 50 Farfalla, 50 Rana, 50 Stile Libero |
| SALAMON GRETA | 2008 | F | 5 | 11 | 100 Misti, 100 Rana, 200 Rana, 50 Dorso, 50 Farfalla, 50 Rana, 50 Stile Libero, 8x50 Stile Libero |
| SOLDA' BENEDETTA | 2010 | F | 3 | 6 | 100 Misti, 50 Dorso, 50 Farfalla, 50 Rana, 50 Stile Libero |
| TERZARIOL NADIA | 2012 | F | 4 | 8 | 100 Dorso, 100 Rana, 100 Stile Libero, 50 Dorso, 50 Stile Libero |
| VINERA NICOLO' | 2008 | M | 3 | 6 | 100 Dorso, 50 Dorso, 50 Stile Libero |
| WU PEIQIANG WILLIAM | 2010 | M | 4 | 9 | 100 Rana, 100 Stile Libero, 200 Rana, 4x50 Stile Libero, 50 Farfalla, 50 Rana, 50 Stile Libero |
| ZAGO MIA | 2012 | F | 4 | 8 | 100 Misti, 100 Stile Libero, 50 Dorso, 50 Stile Libero |

Attenzione a tre omonimie parziali, tutte persone diverse dai tesserati gia' a DB: `PIARULLI FILIPPO` vs PIARULLI VITTORIA (id 16), `SOLDA' BENEDETTA` vs SOLDA' VALENTINA (id 3), `MASCELLANI IRENE` vs MASCELLANI MARCO (id 57). Non sono state accorpate.

Dubbio da sciogliere su un solo nome: `WU PEIQIANG WILLIAM` (2010). Puo' essere cognome `WU PEIQIANG` + nome `WILLIAM` oppure cognome `WU` + nome `PEIQIANG WILLIAM`. Dimmi tu.

## 3. Risultati

449 righe Ranazzurra estratte dai sei PDF (401 individuali + 48 frazioni di staffetta).

| giornata | comp | righe PDF | gia' presenti e uguali | differenti | da inserire (anagrafica ok) | da inserire (atleti nuovi) | ASS (non gare) |
|---|---|---|---|---|---|---|---|
| g1 | 10 | 76 | 50 | 3 | 0 | 23 | 0 |
| g2 | 15 | 87 | 47 | 0 | 0 | 38 | 2 |
| g3 | 17 | 76 | 32 | 1 | 1 | 39 | 3 |
| g4 | 16 | 60 | 35 | 0 | 1 | 20 | 4 |
| g5 | 22 | 69 | 32 | 0 | 1 | 36 | 0 |
| g6 | 23 | 81 | 38 | 1 | 1 | 37 | 4 |
| **totale** | | **449** | **234** | **5** | **4** | **193** | **13** |

Le 13 righe `ASS` sono assenze: l'atleta non ha nuotato, non vanno inserite e infatti nessuna di esse risulta a DB.
Le 6 righe `SQU` (squalifica) sono gare disputate e rientrano fra quelle da inserire, con `final_time` NULL (a DB esistono gia' 65 righe con `final_time` NULL, quindi la convenzione regge).

### 3.1 Righe presenti ma con dati differenti (5) -- da decidere, non le tocco

| giornata | gara | atleta | PDF | DB | record |
|---|---|---|---|---|---|
| g1 | 4x50 Misti | GALBINCEA EMMA MARIA | 02:23.5 | 02:23.7 | ar 345 |
| g1 | 4x50 Misti | BABUIN FRANCESCO | 02:23.5 | 02:23.7 | ar 344 |
| g1 | 4x50 Misti | PIARULLI VITTORIA | 02:23.5 | 02:23.7 | ar 346 |
| g3 | 100 Rana | MASIN STEFANO | 01:13.0 | 01:18.5 | ar 556 |
| g6 | 100 Stile Libero | MAZZER STEFANO | 01:05.9 | 01:07.7 | ar 1100 |

Tre casi distinti:

**a) Staffetta 4x50 MX, g1 (race 32).** La terza squadra Ranazzurra nel PDF chiude in **02:23.5** (pos. 8);
02:23.7 e' il tempo della squadra A.R.C.A. che arriva subito dopo (pos. 9). Le tre righe a DB (ar 344, 345, 346)
hanno preso il tempo sbagliato. Manca inoltre la quarta frazione, PIARULLI FILIPPO.

**b) 100 Rana g3 (race 76), MASIN STEFANO.** Nel PDF MASIN e' 1° in **01:13.0** e TONON MARCO 6° in 01:18.5.
A DB esiste una sola riga, `ar 556`, che attribuisce **01:18.5 a MASIN**: e' il tempo di TONON sotto il nome
sbagliato. Serve correggere ar 556 e inserire la riga mancante.

**c) 100 Stile Libero g6 (race 132), MAZZER STEFANO.** Stessa dinamica: nel PDF MAZZER e' 19° in **01:05.9**
e FADELLI GIOVANNI 26° in 01:07.7. A DB `ar 1100` assegna 01:07.7 a MAZZER.

Per b) e c) ci sono due letture possibili: o la riga a DB e' di TONON/FADELLI con athlete_id sbagliato,
oppure e' di MASIN/MAZZER col tempo sbagliato. In entrambi i casi il risultato finale e' lo stesso
(due righe corrette), cambia solo quale campo si aggiorna. Propongo di correggere il `final_time`
della riga esistente e inserire la riga mancante, cosi' non si toccano le foreign key.

### 3.2 Righe da inserire per atleti gia' in anagrafica (4)

| giornata | race | gara | atleta | tempo | pos |
|---|---|---|---|---|---|
| g3 | 76 | 100 Rana | TONON MARCO | 01:18.5 | 6 |
| g4 | 67 | 4x50 Stile Libero (staffetta) | PIARULLI VITTORIA | 02:03.4 | 8 |
| g5 | 117 | 200 Stile Libero | DRIOLI SPINAZZE' ALBERTO | 02:18.4 | 10 |
| g6 | 132 | 100 Stile Libero | FADELLI GIOVANNI | 01:07.7 | 26 |

Le prime due erano gia' note dal confronto di settembre. Le altre due emergono ora.

### 3.3 Anomalia sulla gara 126

A DB la competition 22 (g5, Mirano) ha una race **126 "200 Farfalla"** con un solo risultato,
`ar 1066` DRIOLI SPINAZZE' ALBERTO 02:18.4. Nel PDF della 5ª giornata **non esistono i 200 Farfalla**:
i fogli sono 200 SL, 50 Dorso, 100 SL, 200 Rana e le due staffette 4x50. DRIOLI compare nei
**200 Stile Libero Maschi in 02:18.4**, pos. 10, subito davanti a TONON (02:18.7, gia' a DB nella race 117).

Quindi la race 126 e' una gara inesistente e `ar 1066` va spostato sulla race 117. In alternativa si lascia
tutto com'e' e si inserisce una riga nuova nella 117, ma a quel punto il tempo risulterebbe due volte.
Serve una tua decisione: non modifico nulla.

### 3.4 Staffetta 8x50 g6: il PDF e' meno completo del DB

Il riepilogo della 6ª giornata stampa solo **4 frazionisti su 8** per ciascuna squadra
(CANCIAN, DRIOLI, PICCIN ANNA, BATTISTELLA per Ranazzurra). Il DB ne ha 8, con MODENESE, MINET,
CANAL e CARAMBIA in piu'. Non e' un errore del DB: e' il PDF che non li riporta. Nessuna azione.

### 3.5 Dettaglio delle righe da inserire, per gara


**g1 / competition 10 / race 32 -- Staffetta Mixed 4x50 MX Serie Assoluti (vasca 25 m)** -- 1 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| PIARULLI FILIPPO | 2011 | staffetta | 02:23.5 | 8 | atleta nuovo |

**g1 / competition 10 / race 33 -- 100 Dorso (vasca 25 m)** -- 3 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| MODOLO ESTER | 2010 | individuale | 01:24.4 | 10 | atleta nuovo |
| PIARULLI FILIPPO | 2011 | individuale | SQU | - | atleta nuovo |
| VINERA NICOLO' | 2008 | individuale | 01:24.1 | 14 | atleta nuovo |

**g1 / competition 10 / race 34 -- 50 Stile Libero (vasca 25 m)** -- 6 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| CARLESSO MATTIA | 2010 | individuale | 00:32.3 | 44 | atleta nuovo |
| GAVA LEONE | 2011 | individuale | 00:35.4 | 54 | atleta nuovo |
| PERIN LEONARDO | 2008 | individuale | 00:34.4 | 52 | atleta nuovo |
| PIARULLI FILIPPO | 2011 | individuale | 00:29.9 | 27 | atleta nuovo |
| VINERA NICOLO' | 2008 | individuale | 00:30.2 | 29 | atleta nuovo |
| ZAGO MIA | 2012 | individuale | 00:41.6 | 43 | atleta nuovo |

**g1 / competition 10 / race 35 -- 100 Misti (vasca 25 m)** -- 8 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BEUKEMA TERESA | 2010 | individuale | 01:32.8 | 29 | atleta nuovo |
| CARLESSO MATTIA | 2010 | individuale | 01:29.6 | 36 | atleta nuovo |
| GAVA LEONE | 2011 | individuale | SQU | - | atleta nuovo |
| MASCELLANI IRENE | 2012 | individuale | 01:29.3 | 27 | atleta nuovo |
| PERIN LEONARDO | 2008 | individuale | 01:27.5 | 35 | atleta nuovo |
| SALAMON GRETA | 2008 | individuale | 01:27.4 | 22 | atleta nuovo |
| SOLDA' BENEDETTA | 2010 | individuale | 01:20.2 | 11 | atleta nuovo |
| ZAGO MIA | 2012 | individuale | SQU | - | atleta nuovo |

**g1 / competition 10 / race 36 -- 50 Farfalla (vasca 25 m)** -- 5 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BEUKEMA TERESA | 2010 | individuale | 00:41.3 | 19 | atleta nuovo |
| MASCELLANI IRENE | 2012 | individuale | 00:41.6 | 20 | atleta nuovo |
| MODOLO ESTER | 2010 | individuale | 00:37.6 | 11 | atleta nuovo |
| SALAMON GRETA | 2008 | individuale | 00:39.3 | 15 | atleta nuovo |
| SOLDA' BENEDETTA | 2010 | individuale | 00:34.8 | 4 | atleta nuovo |

**g2 / competition 15 / race 57 -- 200 Stile Libero Serie (vasca 25 m)** -- 1 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| POL ADELE | 2012 | individuale | 02:52.3 | 10 | atleta nuovo |

**g2 / competition 15 / race 58 -- 50 Rana (vasca 25 m)** -- 9 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BOTTEON NICOLA | 2009 | individuale | 00:48.4 | 16 | atleta nuovo |
| BRAVIN GABRIELE | 2011 | individuale | 00:38.1 | 4 | atleta nuovo |
| BREDA GIORDANO | 2011 | individuale | 00:48.1 | 15 | atleta nuovo |
| D'ALISE SPARTACO | 2012 | individuale | 00:50.3 | 17 | atleta nuovo |
| MASCELLANI IRENE | 2012 | individuale | 00:48.9 | 13 | atleta nuovo |
| REBULI TOMMASO | 2012 | individuale | 00:53.0 | 18 | atleta nuovo |
| SALAMON GRETA | 2008 | individuale | 00:44.0 | 5 | atleta nuovo |
| SOLDA' BENEDETTA | 2010 | individuale | 00:44.4 | 8 | atleta nuovo |
| WU PEIQIANG WILLIAM | 2010 | individuale | 00:41.6 | 7 | atleta nuovo |

**g2 / competition 15 / race 59 -- 100 Misti (vasca 25 m)** -- 7 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| CARLESSO MATTIA | 2010 | individuale | 01:23.7 | 9 | atleta nuovo |
| MASCELLANI IRENE | 2012 | individuale | 01:31.1 | 18 | atleta nuovo |
| PAGOTTO GAIA | 2012 | individuale | 01:32.2 | 19 | atleta nuovo |
| PALFERENT ALESSIA | 2008 | individuale | SQU | - | atleta nuovo |
| POL ADELE | 2012 | individuale | 01:25.7 | 10 | atleta nuovo |
| SALAMON GRETA | 2008 | individuale | 01:30.3 | 11 | atleta nuovo |
| SOLDA' BENEDETTA | 2010 | individuale | 01:21.7 | 6 | atleta nuovo |

**g2 / competition 15 / race 60 -- 100 Dorso (vasca 25 m)** -- 4 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| GONG YISHENG MATTEO | 2012 | individuale | 01:34.5 | 8 | atleta nuovo |
| PIARULLI FILIPPO | 2011 | individuale | 01:15.6 | 3 | atleta nuovo |
| TERZARIOL NADIA | 2012 | individuale | 01:47.8 | 9 | atleta nuovo |
| VINERA NICOLO' | 2008 | individuale | 01:25.2 | 6 | atleta nuovo |

**g2 / competition 15 / race 61 -- 100 Farfalla (vasca 25 m)** -- 2 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| MODOLO ESTER | 2010 | individuale | 01:30.0 | 5 | atleta nuovo |
| PERIN LEONARDO | 2008 | individuale | 01:31.5 | 12 | atleta nuovo |

**g2 / competition 15 / race 62 -- 50 Stile Libero Serie Assoluti (vasca 25 m)** -- 15 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BOTTEON NICOLA | 2009 | individuale | 00:34.0 | 23 | atleta nuovo |
| BRAVIN GABRIELE | 2011 | individuale | 00:29.8 | 9 | atleta nuovo |
| BREDA GIORDANO | 2011 | individuale | 00:35.8 | 27 | atleta nuovo |
| CARLESSO MATTIA | 2010 | individuale | 00:31.4 | 16 | atleta nuovo |
| D'ALISE SPARTACO | 2012 | individuale | 00:36.3 | 28 | atleta nuovo |
| GONG YISHENG MATTEO | 2012 | individuale | 00:35.4 | 26 | atleta nuovo |
| MODOLO ESTER | 2010 | individuale | 00:34.9 | 21 | atleta nuovo |
| PAGOTTO GAIA | 2012 | individuale | 00:36.5 | 25 | atleta nuovo |
| PALFERENT ALESSIA | 2008 | individuale | 00:38.6 | 23 | atleta nuovo |
| PERIN LEONARDO | 2008 | individuale | 00:33.9 | 41 | atleta nuovo |
| PIARULLI FILIPPO | 2011 | individuale | 00:28.3 | 2 | atleta nuovo |
| REBULI TOMMASO | 2012 | individuale | 00:41.0 | 31 | atleta nuovo |
| TERZARIOL NADIA | 2012 | individuale | 00:39.4 | 31 | atleta nuovo |
| VINERA NICOLO' | 2008 | individuale | 00:29.6 | 18 | atleta nuovo |
| WU PEIQIANG WILLIAM | 2010 | individuale | 00:33.7 | 21 | atleta nuovo |

**g3 / competition 17 / race 74 -- 400 Stile Libero (vasca 25 m)** -- 3 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BOTTEON NICOLA | 2009 | individuale | SQU | - | atleta nuovo |
| PERIN LEONARDO | 2008 | individuale | 05:02.4 | 10 | atleta nuovo |
| POL ADELE | 2012 | individuale | 05:57.5 | 16 | atleta nuovo |

**g3 / competition 17 / race 76 -- 100 Rana (vasca 25 m)** -- 6 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BRAVIN GABRIELE | 2011 | individuale | 01:25.5 | 17 | atleta nuovo |
| DAL POS SAMUELE | 2007 | individuale | 01:24.2 | 14 | atleta nuovo |
| REBULI TOMMASO | 2012 | individuale | 01:55.3 | 43 | atleta nuovo |
| SALAMON GRETA | 2008 | individuale | 01:37.7 | 18 | atleta nuovo |
| TONON MARCO | 1990 | individuale | 01:18.5 | 6 | anagrafica ok |
| WU PEIQIANG WILLIAM | 2010 | individuale | 01:31.5 | 28 | atleta nuovo |

**g3 / competition 17 / race 78 -- 50 Stile Libero (vasca 25 m)** -- 17 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BOTTEON NICOLA | 2009 | individuale | 00:34.2 | 68 | atleta nuovo |
| BRAVIN GABRIELE | 2011 | individuale | 00:29.9 | 36 | atleta nuovo |
| BREDA GIORDANO | 2011 | individuale | 00:35.0 | 73 | atleta nuovo |
| D'ALISE SPARTACO | 2012 | individuale | 00:36.1 | 78 | atleta nuovo |
| DAL POS SAMUELE | 2007 | individuale | 00:29.0 | 29 | atleta nuovo |
| MASCHIO MARTA | 2007 | individuale | 00:42.1 | 57 | atleta nuovo |
| MODOLO ESTER | 2010 | individuale | 00:34.8 | 36 | atleta nuovo |
| PAGOTTO GAIA | 2012 | individuale | 00:36.6 | 46 | atleta nuovo |
| PALFERENT ALESSIA | 2008 | individuale | 00:38.9 | 52 | atleta nuovo |
| PIARULLI FILIPPO | 2011 | individuale | 00:28.7 | 26 | atleta nuovo |
| REBULI TOMMASO | 2012 | individuale | 00:39.0 | 83 | atleta nuovo |
| SALAMON GRETA | 2008 | individuale | 00:35.2 | 38 | atleta nuovo |
| SOLDA' BENEDETTA | 2010 | individuale | 00:31.4 | 17 | atleta nuovo |
| TERZARIOL NADIA | 2012 | individuale | 00:40.6 | 56 | atleta nuovo |
| VINERA NICOLO' | 2008 | individuale | 00:29.0 | 29 | atleta nuovo |
| WU PEIQIANG WILLIAM | 2010 | individuale | 00:34.7 | 71 | atleta nuovo |
| ZAGO MIA | 2012 | individuale | SQU | - | atleta nuovo |

**g3 / competition 17 / race 80 -- 50 Dorso  (vasca 25 m)** -- 14 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BREDA GIORDANO | 2011 | individuale | 00:49.1 | 50 | atleta nuovo |
| D'ALISE SPARTACO | 2012 | individuale | 00:43.8 | 41 | atleta nuovo |
| GONG YISHENG MATTEO | 2012 | individuale | 00:41.8 | 37 | atleta nuovo |
| MASCHIO MARTA | 2007 | individuale | 00:48.1 | 43 | atleta nuovo |
| MODOLO ESTER | 2010 | individuale | 00:38.8 | 18 | atleta nuovo |
| PAGOTTO GAIA | 2012 | individuale | 00:44.5 | 37 | atleta nuovo |
| PALFERENT ALESSIA | 2008 | individuale | 00:46.1 | 38 | atleta nuovo |
| PERIN LEONARDO | 2008 | individuale | 00:40.5 | 35 | atleta nuovo |
| PIARULLI FILIPPO | 2011 | individuale | 00:34.6 | 10 | atleta nuovo |
| POL ADELE | 2012 | individuale | 00:40.4 | 25 | atleta nuovo |
| SOLDA' BENEDETTA | 2010 | individuale | 00:37.0 | 11 | atleta nuovo |
| TERZARIOL NADIA | 2012 | individuale | 00:47.8 | 42 | atleta nuovo |
| VINERA NICOLO' | 2008 | individuale | 00:36.6 | 16 | atleta nuovo |
| ZAGO MIA | 2012 | individuale | 00:49.2 | 44 | atleta nuovo |

**g4 / competition 16 / race 63 -- 100 Misti (vasca 25 m)** -- 5 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BERTAZZON MATTEO | 2011 | individuale | 01:41.9 | 54 | atleta nuovo |
| BRAVIN GABRIELE | 2011 | individuale | 01:16.7 | 24 | atleta nuovo |
| MASCELLANI IRENE | 2012 | individuale | 01:31.8 | 41 | atleta nuovo |
| PERIN LEONARDO | 2008 | individuale | 01:25.8 | 45 | atleta nuovo |
| PIARULLI FILIPPO | 2011 | individuale | 01:17.5 | 26 | atleta nuovo |

**g4 / competition 16 / race 64 -- 200 Dorso (vasca 25 m)** -- 3 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| D'ALISE SPARTACO | 2012 | individuale | 03:32.8 | 15 | atleta nuovo |
| MODOLO ESTER | 2010 | individuale | 03:00.9 | 8 | atleta nuovo |
| PIARULLI FILIPPO | 2011 | individuale | 02:59.0 | 10 | atleta nuovo |

**g4 / competition 16 / race 65 -- 100 Stile Libero (vasca 25 m)** -- 4 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BERTAZZON MATTEO | 2011 | individuale | 01:28.7 | 67 | atleta nuovo |
| D'ALISE SPARTACO | 2012 | individuale | 01:24.5 | 66 | atleta nuovo |
| PALFERENT ALESSIA | 2008 | individuale | 01:26.6 | 42 | atleta nuovo |
| REBULI TOMMASO | 2012 | individuale | 01:34.2 | 69 | atleta nuovo |

**g4 / competition 16 / race 66 -- 50 Farfalla (vasca 25 m)** -- 5 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BRAVIN GABRIELE | 2011 | individuale | 00:32.9 | 26 | atleta nuovo |
| MASCELLANI IRENE | 2012 | individuale | 00:42.0 | 30 | atleta nuovo |
| MODOLO ESTER | 2010 | individuale | 00:38.9 | 23 | atleta nuovo |
| PALFERENT ALESSIA | 2008 | individuale | 00:43.0 | 32 | atleta nuovo |
| PERIN LEONARDO | 2008 | individuale | 00:36.6 | 45 | atleta nuovo |

**g4 / competition 16 / race 67 -- Staffetta Mixed 4x50 SL Serie Assoluti (vasca 25 m)** -- 4 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BRAVIN GABRIELE | 2011 | staffetta | 02:03.4 | 8 | atleta nuovo |
| MODOLO ESTER | 2010 | staffetta | 02:03.4 | 8 | atleta nuovo |
| PIARULLI FILIPPO | 2011 | staffetta | 02:03.4 | 8 | atleta nuovo |
| PIARULLI VITTORIA | 2008 | staffetta | 02:03.4 | 8 | anagrafica ok |

**g5 / competition 22 / race 116 -- 200 Stile Libero Serie Assoluti Femmine (vasca 25 m)** -- 2 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| PALFERENT ALESSIA | 2008 | individuale | 03:04.4 | 24 | atleta nuovo |
| POL ADELE | 2012 | individuale | 02:44.5 | 16 | atleta nuovo |

**g5 / competition 22 / race 117 -- 200 Stile Libero Serie Assoluti Maschi (vasca 25 m)** -- 5 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| D'ALISE SPARTACO | 2012 | individuale | 02:57.8 | 25 | atleta nuovo |
| DRIOLI SPINAZZE' ALBERTO | 2005 | individuale | 02:18.4 | 10 | anagrafica ok |
| PERIN LEONARDO | 2008 | individuale | 02:48.7 | 21 | atleta nuovo |
| PIARULLI FILIPPO | 2011 | individuale | 02:33.2 | 18 | atleta nuovo |
| REBULI TOMMASO | 2012 | individuale | 03:32.0 | 26 | atleta nuovo |

**g5 / competition 22 / race 118 -- 50 Dorso Serie Assoluti Femmine (vasca 25 m)** -- 5 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| PAGOTTO GAIA | 2012 | individuale | 00:42.3 | 26 | atleta nuovo |
| POL ADELE | 2012 | individuale | 00:39.8 | 18 | atleta nuovo |
| SALAMON GRETA | 2008 | individuale | 00:42.0 | 25 | atleta nuovo |
| TERZARIOL NADIA | 2012 | individuale | 00:46.5 | 30 | atleta nuovo |
| ZAGO MIA | 2012 | individuale | 00:45.7 | 29 | atleta nuovo |

**g5 / competition 22 / race 119 -- 50 Dorso Serie Assoluti Maschi (vasca 25 m)** -- 4 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BERNARDI GIULIO | 2007 | individuale | 00:39.2 | 21 | atleta nuovo |
| BERTAZZON MATTEO | 2011 | individuale | 00:46.1 | 35 | atleta nuovo |
| BOTTEON NICOLA | 2009 | individuale | 00:42.0 | 29 | atleta nuovo |
| GONG YISHENG MATTEO | 2012 | individuale | 00:40.2 | 26 | atleta nuovo |

**g5 / competition 22 / race 120 -- 100 Stile Libero Serie Assoluti Femmine (vasca 25 m)** -- 4 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| PAGOTTO GAIA | 2012 | individuale | 01:16.3 | 22 | atleta nuovo |
| PALFERENT ALESSIA | 2008 | individuale | 01:25.8 | 35 | atleta nuovo |
| TERZARIOL NADIA | 2012 | individuale | 01:32.6 | 39 | atleta nuovo |
| ZAGO MIA | 2012 | individuale | 01:28.0 | 38 | atleta nuovo |

**g5 / competition 22 / race 121 -- 100 Stile Libero Serie Assoluti Maschi (vasca 25 m)** -- 9 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BERNARDI GIULIO | 2007 | individuale | 01:12.2 | 42 | atleta nuovo |
| BERTAZZON MATTEO | 2011 | individuale | 01:27.1 | 65 | atleta nuovo |
| BOTTEON NICOLA | 2009 | individuale | 01:15.0 | 49 | atleta nuovo |
| BRAVIN GABRIELE | 2011 | individuale | 01:08.0 | 31 | atleta nuovo |
| D'ALISE SPARTACO | 2012 | individuale | 01:17.0 | 54 | atleta nuovo |
| GONG YISHENG MATTEO | 2012 | individuale | 01:19.6 | 58 | atleta nuovo |
| PIARULLI FILIPPO | 2011 | individuale | 01:07.2 | 27 | atleta nuovo |
| REBULI TOMMASO | 2012 | individuale | 01:35.1 | 68 | atleta nuovo |
| WU PEIQIANG WILLIAM | 2010 | individuale | 01:16.9 | 53 | atleta nuovo |

**g5 / competition 22 / race 122 -- 200 Rana Serie Assoluti Femmine (vasca 25 m)** -- 1 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| SALAMON GRETA | 2008 | individuale | 03:36.9 | 13 | atleta nuovo |

**g5 / competition 22 / race 123 -- 200 Rana Serie Assoluti Maschi (vasca 25 m)** -- 3 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BRAVIN GABRIELE | 2011 | individuale | 03:10.9 | 13 | atleta nuovo |
| PERIN LEONARDO | 2008 | individuale | 03:26.6 | 25 | atleta nuovo |
| WU PEIQIANG WILLIAM | 2010 | individuale | 03:19.9 | 21 | atleta nuovo |

**g5 / competition 22 / race 125 -- Staff. 4x50 Stile L. Serie Assoluti Maschi (vasca 25 m)** -- 4 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BRAVIN GABRIELE | 2011 | staffetta | 02:06.0 | 11 | atleta nuovo |
| PERIN LEONARDO | 2008 | staffetta | 02:06.0 | 11 | atleta nuovo |
| PIARULLI FILIPPO | 2011 | staffetta | 02:06.0 | 11 | atleta nuovo |
| WU PEIQIANG WILLIAM | 2010 | staffetta | 02:06.0 | 11 | atleta nuovo |

**g6 / competition 23 / race 127 -- 8x50 Stile Libero (vasca 50 m)** -- 4 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BRAVIN GABRIELE | 2011 | staffetta | 04:35.7 | 7 | atleta nuovo |
| MODOLO ESTER | 2010 | staffetta | 04:35.7 | 7 | atleta nuovo |
| PIARULLI FILIPPO | 2011 | staffetta | 04:35.7 | 7 | atleta nuovo |
| SALAMON GRETA | 2008 | staffetta | 04:35.7 | 7 | atleta nuovo |

**g6 / competition 23 / race 128 -- 100 Rana (vasca 50 m)** -- 7 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BOTTEON NICOLA | 2009 | individuale | 01:47.9 | 28 | atleta nuovo |
| BRAVIN GABRIELE | 2011 | individuale | 01:28.4 | 10 | atleta nuovo |
| MASCELLANI IRENE | 2012 | individuale | 01:39.5 | 10 | atleta nuovo |
| REBULI TOMMASO | 2012 | individuale | 01:55.8 | 29 | atleta nuovo |
| SALAMON GRETA | 2008 | individuale | 01:40.0 | 11 | atleta nuovo |
| TERZARIOL NADIA | 2012 | individuale | 01:57.4 | 17 | atleta nuovo |
| WU PEIQIANG WILLIAM | 2010 | individuale | 01:32.0 | 18 | atleta nuovo |

**g6 / competition 23 / race 129 -- 200 Misti (vasca 50 m)** -- 2 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| PERIN LEONARDO | 2008 | individuale | 03:17.5 | 23 | atleta nuovo |
| PIARULLI FILIPPO | 2011 | individuale | 02:52.3 | 11 | atleta nuovo |

**g6 / competition 23 / race 130 -- 50 Dorso (vasca 50 m)** -- 6 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BERTAZZON MATTEO | 2011 | individuale | 00:47.5 | 30 | atleta nuovo |
| D'ALISE SPARTACO | 2012 | individuale | 00:40.5 | 20 | atleta nuovo |
| GONG YISHENG MATTEO | 2012 | individuale | 00:40.7 | 21 | atleta nuovo |
| MODOLO ESTER | 2010 | individuale | 00:38.9 | 12 | atleta nuovo |
| TERZARIOL NADIA | 2012 | individuale | 00:47.5 | 33 | atleta nuovo |
| ZAGO MIA | 2012 | individuale | 00:46.9 | 32 | atleta nuovo |

**g6 / competition 23 / race 131 -- 50 Farfalla (vasca 50 m)** -- 8 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BRAVIN GABRIELE | 2011 | individuale | 00:33.1 | 24 | atleta nuovo |
| MASCELLANI IRENE | 2012 | individuale | 00:39.8 | 33 | atleta nuovo |
| MODOLO ESTER | 2010 | individuale | 00:36.7 | 18 | atleta nuovo |
| PAGOTTO GAIA | 2012 | individuale | 00:35.6 | 11 | atleta nuovo |
| PALFERENT ALESSIA | 2008 | individuale | 00:42.6 | 35 | atleta nuovo |
| PIARULLI FILIPPO | 2011 | individuale | 00:32.9 | 23 | atleta nuovo |
| SALAMON GRETA | 2008 | individuale | 00:38.9 | 27 | atleta nuovo |
| WU PEIQIANG WILLIAM | 2010 | individuale | 00:40.9 | 50 | atleta nuovo |

**g6 / competition 23 / race 132 -- 100 Stile Libero (vasca 50 m)** -- 11 righe

| atleta | anno | tipo | tempo | pos | provenienza |
|---|---|---|---|---|---|
| BERNARDI GIULIO | 2007 | individuale | 01:12.8 | 49 | atleta nuovo |
| BERTAZZON MATTEO | 2011 | individuale | 01:24.2 | 66 | atleta nuovo |
| BOTTEON NICOLA | 2009 | individuale | 01:13.7 | 52 | atleta nuovo |
| D'ALISE SPARTACO | 2012 | individuale | 01:14.5 | 55 | atleta nuovo |
| FADELLI GIOVANNI | 1985 | individuale | 01:07.7 | 26 | anagrafica ok |
| GONG YISHENG MATTEO | 2012 | individuale | 01:16.0 | 60 | atleta nuovo |
| PAGOTTO GAIA | 2012 | individuale | 01:16.0 | 24 | atleta nuovo |
| PALFERENT ALESSIA | 2008 | individuale | 01:22.0 | 41 | atleta nuovo |
| PERIN LEONARDO | 2008 | individuale | 01:11.3 | 39 | atleta nuovo |
| REBULI TOMMASO | 2012 | individuale | 01:33.6 | 68 | atleta nuovo |
| ZAGO MIA | 2012 | individuale | 01:23.0 | 45 | atleta nuovo |

## 4. Regola categoria

`athlete_races` non ha un campo posizione, quindi il piazzamento del PDF non e' memorizzabile:
resta solo come riscontro in questo report. La categoria sta in `athlete_races.group`, che pero'
per tutte e sei queste manifestazioni e' **NULL su tutte le 244 righe gia' presenti**
(a DB e' valorizzato solo su 412 righe, tutte di provenienza FIN Veneto, nella forma `M45`, `M50`).

Applicando la tua regola: tutti e 26 i nuovi atleti hanno fra i 13 e i 19 anni alla data di ogni
manifestazione, quindi tutte le 193 righe nuove sarebbero **`mini`**. Nessun caso e' indeterminato
(nessun anno di nascita e' a cavallo dei 20 anni rispetto alla data gara). Delle 4 righe di atleti
gia' in anagrafica, tutte sono sopra i 20 anni.

Valorizzare `group` solo sulle righe nuove creerebbe pero' una incoerenza con le 244 righe esistenti
che sono NULL. Tre opzioni: lascio NULL come le altre, scrivo `mini` solo sulle nuove, oppure scrivo
la categoria su tutte e 437 le righe delle sei manifestazioni. Dimmi tu quale.

## 5. Controlli di integrita' fatti

- Schema letto da `information_schema` e dalla DDL di progetto. Le uniche chiavi sono le primary key:
  **non esiste alcun vincolo di unicita'** su `athlete_races`, quindi la protezione dai duplicati e'
  solo logica. Il confronto e' stato fatto sulla quadrupla (competition, athlete_id, distanza, stile)
  con abbinamento uno a uno dei tempi, cosi' le doppie partecipazioni non generano falsi positivi.
- Foreign key verificate: `athlete_races.race_id -> races.id`, `athlete_races.athlete_id -> athletes.id`,
  `races.competition_id`, `races.race_event_id`. Tutte le 197 righe da inserire puntano a races esistenti.
- `creation_user_id`: a DB si usano 1 (system) e 2 (devsupport). Userei **2**, come lo scraper.
- Estrazione PDF validata: le occorrenze di "RANAZZURRA CONEGLIANO SSD" nel testo grezzo coincidono
  esattamente con le righe ricostruite in tutti e sei i documenti (67, 87, 76, 51, 57, 75), zero righe
  non interpretate, numerazione dei fogli completa e senza buchi.
- Cognomi a DB con spazio in coda (28 su 49): il match e' fatto su stringhe normalizzate, accenti
  rimossi e spazi compattati.
