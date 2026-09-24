# Report finale import PDF 2006

Eseguito il 23/09/2026 sul DB `swim` (Aiven), dopo conferma.

## Cosa e' stato scritto

| operazione | tabella | record |
|---|---|---|
| rinomina manifestazioni | competitions | 4 (1213, 1214, 1216, 1217) |
| nuova manifestazione | competitions | 1 (id 1490) |
| nuove gare | races | 26 (id 22394-22419) |
| atleti censiti | athletes | 22 (id 184-205) |
| risultati | athlete_races | 177 (id 7666-7842) |
| spostamento risultato VEDOVELLI | athlete_races | 1 (ar 2001, race 17427 -> 185) |
| disattivazione manifestazione doppia | competitions + races | 2 (comp 1215, race 17427) |

`athletes` da 151 a 173, `athlete_races` da 5119 a 5296, `races` da 2205 a 2231.
Nessuna cancellazione fisica: la 1215 e la sua gara sono a `is_deleted = true`.

## 1. Manifestazioni

| id | data | sede | vasca | risultati | stato |
|---|---|---|---|---|---|
| 1490 | 2006-01-28 | San Donà di Piave | 25 m | 5 | creata |
| 1213 | 2006-03-19 | Oderzo | 25 m | 36 | esisteva, rinominata |
| 1214 | 2006-04-23 | Vittorio Veneto | 25 m | 42 | esisteva, rinominata |
| 29 | 2006-05-21 | Belluno | 25 m | 45 | esisteva, gia intitolata |
| 1216 | 2006-07-01 | Spresiano | 50 m | 24 | esisteva, rinominata |
| 1217 | 2006-12-03 | Valdobbiadene | 25 m | 35 | esisteva, rinominata |

I quattro titoli generici sono diventati: "2ª Giornata Circuito Master Sinistra Piave - Oderzo",
"3ª Giornata Circuito Master - Vittorio Veneto", "Finale Circuito Masters Provincia di Treviso -
Spresiano" e "1ª Giornata Circuito Master - Valdobbiadene".

## 2. Belluno: la manifestazione doppia e risolta

Il 21/05/2006 c'erano **due competitions per lo stesso evento**, entrambe con `web_id 1246`. Cosa ho fatto:

1. caricato tutte le righe del PDF nella **competition 29** ("7° Trofeo Città di Belluno", da
   natatoria), usando le sue tre gare gia esistenti 184, 185 e 186, che non sono divise per sesso e
   coprono i tre eventi della giornata: **nessuna gara nuova creata per Belluno**;
2. spostato il 50 stile di VEDOVELLI DANILA (`ar 2001`, 00:46.3) dalla race 17427 alla race 185;
3. messo `is_deleted = true` su competition 1215 e sulla sua race 17427, e cambiato il `type` della
   1215 in "DUPLICATO di competition 29 (7° Trofeo Città di Belluno) - non usare", cosi chi la
   incontra capisce subito perche' e li.

Verifica: la 1215 ora ha zero gare attive e zero risultati, e **non resta nessun web_id duplicato
fra le competitions attive** in tutto il database.

## 3. Atleti censiti (22)

Tutti con `company_id = 37`, `birth_date` al 01/01 dell'anno del PDF, `is_deleted = true`,
`creation_user_id = 2`.

| id | cognome | nome | anno |
|---|---|---|---|
| 184 | BLASI | STEFANO | 1983 |
| 185 | CASAGRANDE | FABRIZIO | 1976 |
| 186 | COZZUOL | MATTEO | 1976 |
| 187 | DA ROS | GABRIELE | 1983 |
| 188 | DAVANZO | GESSICA | 1985 |
| 189 | DE STEFANI | PAOLO | 1970 |
| 190 | DONADEL | ANDREA | 1976 |
| 191 | GERARDO | SIMONE | 1979 |
| 192 | GHIRARDO | LETIZIA | 1984 |
| 193 | GRANZOTTO | ANDREA | 1976 |
| 194 | MENEGHIN | LORETTA | 1964 |
| 195 | MENIS | ALESSANDRO | 1973 |
| 196 | PAPA | IVAN | 1974 |
| 197 | PICCOLI | IVANO | 1971 |
| 198 | RUI | ALBERTO | 1982 |
| 199 | SALVALAGGIO | CATIA | 1964 |
| 200 | SARTORI | EROS | 1981 |
| 201 | SCHIEVENE | FEDERICA | 1976 |
| 202 | SEMENZATO | DANIELE | 1978 |
| 203 | ZANATTA | SARA | 1983 |
| 204 | ZANCHETTA | MICHELA | 1980 |
| 205 | ZANIN | ANNALISA | 1972 |

Gli altri 28 dei 50 atleti erano gia in anagrafica. Tutti e 22 i nuovi hanno almeno un risultato
collegato. Cognomi vicini ma persone diverse, tenute separate: GHIRARDO LETIZIA e GHIRARDI CLAUDIA
(133), DONADEL ANDREA e DONADEL LORIS (124), DA ROS GABRIELE, DA ROS SIMONE (81) e DA ROS FABRICE (173).

## 4. Risultati

| manifestazione | righe nei PDF | ASS | gia a DB | inserite |
|---|---|---|---|---|
| sdona_2006 | 7 | 2 | 0 | 5 |
| oderzo_2006 | 41 | 5 | 1 | 35 |
| vittorio_2006 | 42 | 0 | 1 | 41 |
| belluno_2006 | 48 | 3 | 6 | 39 |
| spresiano_2006 | 27 | 3 | 1 | 23 |
| valdobbiadene_2006 | 36 | 1 | 1 | 34 |
| **totale** | **201** | **14** | **10** | **177** |

Le 10 righe gia presenti erano i 5 risultati della competition 29 (FILIPPI, FONTANA, DA ROS) e i 5
50 stile di VEDOVELLI, uno per giornata: tutti verificati contro il PDF prima di procedere, tutti
coincidenti. La riga SQU di DONADEL ANDREA sui 50 stile a Vittorio e stata inserita con
`final_time` NULL. Una gara non e stata creata, i 50 farfalla maschi di San Donà, perche' l'unica
riga Ranazzurra era un'assenza.

## 5. Verifica

md5 dell'insieme atteso di terne (race_id, athlete_id, final_time) contro il contenuto reale del DB.
**Tutte e sei le manifestazioni coincidono.**

| competition | righe | md5 |
|---|---|---|
| 1490 | 5 | `a9ae62fb2d36c41e` |
| 1213 | 36 | `9b07e3868b10fc83` |
| 1214 | 42 | `1dd72debdb19ffa7` |
| 29 | 45 | `8c89a7c8654e0dfd` |
| 1216 | 24 | `635c0c925932610d` |
| 1217 | 35 | `74b776342842d0b4` |

Zero doppioni, zero chiavi orfane, zero gare nuove senza risultati, zero atleti nuovi senza gare.
Le quattro sequence sono allineate al massimo id.

## 6. Un intoppo di rete

Il primo INSERT delle 26 gare e tornato con `fetch failed` senza risposta dal server. Prima di
ripetere ho controllato lo stato: `max(id)` e sequence di `races` erano entrambi ancora a 22393 e
nelle competitions 2006 c'erano solo le 4 gare preesistenti, quindi **la richiesta non era arrivata
al database**. Ripetuta senza conseguenze. Regola confermata: dopo un errore di trasporto non si
ripete mai a scatola chiusa, si conta prima.

## 7. Stato dello storico

Le **21 giornate del circuito Master** ora a DB, dal 18/01/2003 al 14/06/2008, contengono
**654 risultati di 100 atleti distinti**. Il circuito e completo per 2003, 2004, 2005 e 2006.
