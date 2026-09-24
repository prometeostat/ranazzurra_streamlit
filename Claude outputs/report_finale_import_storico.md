# Report finale import PDF storici 2003 e 2008

Eseguito il 22/09/2026 sul DB `swim` (Aiven), dopo conferma.

## Cosa e' stato scritto

| operazione | tabella | record |
|---|---|---|
| rinomina manifestazioni | competitions | 3 (UPDATE) |
| correzione anno di nascita FONTANA NICO | athletes | 1 (UPDATE) |
| nuove manifestazioni | competitions | 4 (INSERT, id 1478-1481) |
| nuove gare | races | 44 (INSERT, id 22302-22345) |
| atleti storici censiti | athletes | 58 (INSERT, id 108-165) |
| risultati | athlete_races | 195 (INSERT, id 7202-7396) |

Nessuna cancellazione. `athletes` passa da 75 a 133, `athlete_races` da 4655 a 4850.

## 1. Manifestazioni

| competition | data | sede | nome a DB | stato | gare | risultati |
|---|---|---|---|---|---|---|
| 1478 | 2003-01-18 | S. Dona' di Piave | I Giornata Circuito Master - S. Donà di Piave | nuova | 6 | 18 |
| 1447 | 2003-03-02 | Oderzo | 2ª Giornata Attività Master Sinistra Piave | esistente | 5 | 27 |
| 1479 | 2003-04-05 | Vittorio Veneto | Terza Giornata Attività Master Sinistra Piave | nuova | 6 | 29 |
| 1448 | 2003-05-18 | Belluno | 4° Trofeo Masters Città di Belluno | esistente | 5 | 32 |
| 1449 | 2003-06-29 | Lido di Venezia | 5ª Giornata Circuito Master PLAVIS | esistente | 7 | 26 |
| 1480 | 2003-12-14 | Roncade | 1ª Giornata Circuito Master - Roncade | nuova | 6 | 39 |
| 1481 | 2008-06-14 | Spresiano (TV) | Finale Circuito Masters Provincie BL-TV-VE | nuova | 9 | 27 |

Le tre esistenti (1447, 1448, 1449) avevano il `type` generico ereditato dallo scraper FIN Veneto,
sostituito col nome vero letto dal PDF. Le quattro nuove hanno `scraping_website_id = 2` (Natatoria),
`timing = MANUALE` (dalla riga `Cron: M` dei fogli), `end_date` uguale a `start_date`.
`web_id`, `website_link` e `organizer_company_id` sono NULL: dal PDF non si ricavano, e non ho voluto
dedurre la societa organizzatrice dalla sede. Anche `max_races_per_athlete` e NULL perche il
regolamento di quelle giornate non lo conosco.

Le gare seguono la convenzione delle tre races gia esistenti di queste stesse manifestazioni:
`<distanza> <stile> Serie Cat.: <categoria del foglio>`. `pool_length` 25 sulle sei del 2003 e 50 su
Spresiano 2008, letto dalla riga `Base v.`.

## 2. Anagrafica

58 atleti storici censiti, id 108-165, tutti con `company_id = 37`, `birth_date` al 01/01 dell'anno
letto dal PDF, `is_deleted = true`, `creation_user_id = 2`, `fin_code` e `web_id` NULL.

Quattro atleti erano gia presenti e hanno ricevuto i loro risultati storici sul record esistente:
FILIPPI FRANCESCO (60, 12 gare nuove), FONTANA NICO (61, 3), VEDOVELLI DANILA (14, 1) e
MASUTTI DENIS (58, le cui 3 gare erano gia a DB e non sono state toccate).

A FONTANA NICO ho allineato `birth_date` da 1980-01-01 a 1979-01-01, come da tua indicazione:
il valore precedente era un segnaposto condiviso con FILIPPI e DA ROS.

Due dei 58 restano senza risultati collegati, PRADELLA GIANPAOLO e TALAMINI PAOLO: nei PDF compaiono
solo con codice ASS a Spresiano 2008, quindi sono in anagrafica ma non hanno gare. E corretto cosi.

Come da tua scelta, PERINO ALICE (144) e PERINOT ALICE (145) restano due atleti distinti.

## 3. Risultati

| manifestazione | righe nei PDF | ASS scartate | gia a DB | inserite | totale a DB |
|---|---|---|---|---|---|
| sdona_2003 | 18 | 0 | 0 | 18 | 18 |
| oderzo_2003 | 32 | 5 | 1 | 26 | 27 |
| vittorio_2003 | 32 | 3 | 0 | 29 | 29 |
| belluno_2003 | 33 | 1 | 1 | 31 | 32 |
| lido_2003 | 26 | 0 | 1 | 25 | 26 |
| roncade_2003 | 40 | 0 | 0 | 39 | 39 |
| spresiano_2008 | 30 | 3 | 0 | 27 | 27 |
| **totale** | **211** | **12** | **3** | **195** | **198** |

Una sola riga SQU, GATTI ANNA sui 50 stile a Belluno, inserita con `final_time` NULL.
Le 68 righe di `RANAZZURRA Lido` sono state escluse: e la societa 57, un altro club.
`athlete_races.group` lasciato NULL, come su tutto il resto dello storico.

## 4. Verifica

Ricostruito dai sette PDF l'insieme atteso di terne (race_id, athlete_id, final_time) e confrontato
col DB via md5 della stringa ordinata (`ORDER BY k COLLATE "C"`). **Tutte e sette coincidono.**

| competition | righe | md5 |
|---|---|---|
| 1478 | 18 | `ed0c784d3d7a5420` |
| 1447 | 27 | `5d51fff6032d00ac` |
| 1479 | 29 | `ff72fda70f09d63b` |
| 1448 | 32 | `e379fb2fd42d6509` |
| 1449 | 26 | `25ec97c75d45518a` |
| 1480 | 39 | `db54553849d3886d` |
| 1481 | 27 | `47f328760462930e` |

Altri controlli, tutti puliti: 0 doppioni (race_id, athlete_id, final_time) nelle sette
manifestazioni, 0 race_id o athlete_id orfani, 0 races nuove rimaste senza risultati, 0 races
con competition_id orfano. Tutte e quattro le sequence (athletes, races, athlete_races,
competitions) sono allineate al massimo id della rispettiva tabella.

## 5. Sequence: il problema si e ripresentato

Come previsto dopo l'import Aquasport, anche `races_id_seq` era disallineata: ferma a 22287 con
massimo id 22301. L'ho riallineata con `ALTER SEQUENCE public.races_id_seq RESTART WITH 22302`
**prima** di inserire, quindi stavolta nessun INSERT e fallito. `competitions_id_seq` era invece
a posto (1477 contro un massimo di 1476).

Resta da verificare `split_times_id_seq` e le altre tabelle non toccate qui.

## 6. L'unica riga rimasta fuori, e cosa ho scoperto guardandola meglio

**ANDREOLA ALESSANDRO, anno 1996**, 50 stile libero maschi a Roncade il 14/12/2003, 00:29.3,
posizione 13. Non e stato censito e il risultato non e stato inserito.

Rimettendo in fila tutte le righe, pero, la spiegazione piu probabile non e un anno sbagliato ma
un refuso doppio su cognome e anno, e la persona e **ANDREON ALESSANDRO 1970** (id 108):

| manifestazione | gara | nome nel PDF | anno | tempo |
|---|---|---|---|---|
| S. Dona' 18/01 | 50 stile | ANDREON ALESSANDRO | 1970 | 00:30.2 |
| S. Dona' 18/01 | 50 farfalla | ANDREON ALESSANDRO | 1970 | 00:34.7 |
| Oderzo 02/03 | 50 stile | ANDREON ALESSANDRO | 1970 | 00:30.0 |
| Oderzo 02/03 | 50 dorso | ANDREON ALESSANDRO | 1970 | 00:40.7 |
| Belluno 18/05 | 50 stile | ANDREON ALESSANDRO | 1970 | 00:30.2 |
| Belluno 18/05 | 200 stile | ANDREON ALESSANDRO | 1970 | 02:39.0 |
| **Roncade 14/12** | **50 stile** | **ANDREOLA ALESSANDRO** | **1996** | **00:29.3** |
| Roncade 14/12 | 50 farfalla | ANDREON ALESSANDRO | 1970 | 00:32.9 |

Tre indizi che puntano nella stessa direzione: il tempo sui 50 stile, 29.3, e in linea con i suoi
30.2 / 30.0 / 30.2 delle altre giornate e non con un bambino di sette anni; a Roncade le due righe
non compaiono mai nella stessa gara, quindi non e il caso di due persone iscritte insieme; e con
quella riga ANDREON avrebbe a Roncade le sue solite due gare, 50 stile e 50 farfalla, esattamente
come in tutte le altre giornate.

Se sei d'accordo basta inserire quella riga su ANDREON (id 108) nella race 22334, senza censire
nessun atleta nuovo. Dimmi tu.
