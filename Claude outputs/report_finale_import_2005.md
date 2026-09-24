# Report finale import PDF 2005

Eseguito il 22/09/2026 sul DB `swim` (Aiven), dopo conferma.

## Cosa e' stato scritto

| operazione | tabella | record |
|---|---|---|
| OMETTO GIULIA (femmina) | athletes | 1 (id 183) |
| risultati 2004 di OMETTO | athlete_races | 3 (id 7609-7611) |
| nuove manifestazioni 2005 | competitions | 4 (id 1486-1489) |
| nuove gare 2005 | races | 22 (id 22372-22393) |
| risultati 2005 | athlete_races | 54 (id 7612-7665) |

`athletes` da 150 a 151, `athlete_races` da 5062 a 5119, `races` da 2183 a 2205, `competitions` da 532 a 536. Nessuna cancellazione, nessun atleta nuovo per il 2005.

## 1. OMETTO GIULIA

Censita come **femmina** (`sex = false`), nata 1992-01-01, `company_id = 37`, `is_deleted = true`. I suoi tre risultati del 2004: 50 stile a Oderzo 00:36.8 (race 22355), 50 rana a Oderzo 00:44.4 (race 22353), 50 rana alla finale di Vittorio 00:43.5 (race 22369). La competition 1483 passa a 73 risultati e la 1485 a 33. Il 2004 e ora completo.

## 2. Manifestazioni 2005 create

| id | data | sede | vasca | gare | risultati |
|---|---|---|---|---|---|
| 1486 | 2005-01-16 | San Donà di Piave | 25 m | 4 | 14 |
| 1487 | 2005-02-27 | Roncade | 25 m | 5 | 15 |
| 1488 | 2005-03-20 | Vittorio Veneto | 25 m | 6 | 16 |
| 1489 | 2005-06-25 | San Donà di Piave | 50 m | 7 | 9 |

Il circuito Master e ora coperto per tre stagioni di fila. La 5ª giornata del 25/06 a San Dona' e
l'unica delle quattro in vasca da 50. Manca la 4ª giornata 2005, come mancava nel 2003.

Verifica fatta prima di creare: il 27/02/2005, stesso giorno di Roncade, esistevano gia le
competitions 1165 e 1166, ma sono gare `Assoluti Femmine Agonisti` di CARLET FEDERICA con
cronometraggio AUTOMATICO da finveneto (id_manifestazione 852 e 866). Manifestazione diversa,
nessun duplicato creato.

## 3. Risultati

| manifestazione | righe nei PDF | ASS scartate | inserite |
|---|---|---|---|
| sdona_2005 | 16 | 2 | 14 |
| roncade_2005 | 22 | 7 | 15 |
| vittorio_2005 | 18 | 2 | 16 |
| sdona_2005_2 | 10 | 1 | 9 |
| **totale** | **66** | **12** | **54** |

I 17 atleti dei quattro riepiloghi erano **tutti gia in anagrafica**: primo import dello storico
senza nemmeno un censimento. La riga RIT di CAMPODALL'ORTO ANDREA sui 100 dorso a San Dona' in
gennaio e stata inserita con `final_time` NULL. Escluse le righe di RANAZZURRA Lido.

## 4. Verifica

md5 dell'insieme atteso di terne (race_id, athlete_id, final_time) contro il contenuto reale del DB,
una manifestazione per volta. **Tutte e quattro coincidono.**

| competition | righe | md5 |
|---|---|---|
| 1486 | 14 | `18c4262f2d0b3c9d` |
| 1487 | 15 | `d00d7b3e67f1312b` |
| 1488 | 16 | `8a52b52b4c417006` |
| 1489 | 9 | `e2f529ca6dad4598` |

Zero doppioni, zero chiavi orfane in tutto il DB, zero gare nuove rimaste senza risultati. Le quattro
sequence erano allineate prima di iniziare e lo sono ancora: nessun INSERT fallito.

## 5. Il calo della squadra nel 2005

Non e un problema di dati, ma vale la pena averlo scritto da qualche parte:

| stagione | RANAZZURRA S.S.D. (company 37) | RANAZZURRA Lido (company 57) |
|---|---|---|
| 2003, 6 giornate | 211 righe, 63 atleti | 68 righe |
| 2004, 4 giornate | 236 righe, 50 atleti | 28 righe |
| 2005, 4 giornate | 66 righe, 17 atleti | 67 righe, 14 atleti |

Verificato che non sia un travaso di denominazione: **nessuno dei 14 atleti del Lido 2005 compare
fra i nostri del 2003 o 2004**. Il calo e reale.

## 6. Stato dello storico

Le 15 manifestazioni d'epoca ora a DB (2003, 2004, 2005, 2008) contengono **467 risultati di 78
atleti**. Prima di questa serie di import il periodo 2003-2008 aveva 10 atleti con almeno un
risultato e nessuna manifestazione sopra le cinque righe.
