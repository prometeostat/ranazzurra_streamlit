# Report finale import PDF 2004

Eseguito il 22/09/2026 sul DB `swim` (Aiven), dopo conferma.

## Cosa e' stato scritto

| operazione | tabella | record |
|---|---|---|
| nuove manifestazioni | competitions | 4 (id 1482-1485) |
| nuove gare | races | 26 (id 22346-22371) |
| atleti censiti | athletes | 17 (id 166-182) |
| risultati | athlete_races | 212 (id 7397-7608) |

`athletes` da 133 a 150, `athlete_races` da 4850 a 5062, `races` da 2157 a 2183, `competitions` da 528 a 532.
Nessuna cancellazione, nessun record preesistente modificato.

## 1. Manifestazioni create

| id | data | sede | vasca | nome | gare | risultati |
|---|---|---|---|---|---|---|
| 1482 | 2004-01-31 | San Donà di Piave | 25 m | 2ª Giornata Circuito Master - San Donà di Piave | 6 | 59 |
| 1483 | 2004-03-28 | Oderzo | 25 m | 3ª Giornata Attività Master Sinistra Piave | 6 | 71 |
| 1484 | 2004-05-23 | Belluno | 25 m | 5° Trofeo Master - Belluno | 6 | 49 |
| 1485 | 2004-06-26 | Vittorio Veneto | 50 m | Finale Attività Master 2004 - Vittorio Veneto | 8 | 32 |

Il circuito Sinistra Piave adesso e coperto per due stagioni intere: 2003 con S. Dona', Oderzo,
Vittorio Veneto, Belluno, Lido e Roncade, e 2004 con queste quattro. La finale di Vittorio Veneto
del 26/06/2004 e l'unica in vasca da 50 fra le quattro.

## 2. Atleti censiti (17)

Tutti con `company_id = 37`, `birth_date` al 01/01 dell'anno letto dal PDF, `is_deleted = true`,
`creation_user_id = 2`, `fin_code` e `web_id` NULL.

| id | cognome | nome | anno | sesso |
|---|---|---|---|---|
| 166 | ANDREETTA | JOHNNY | 1970 | M |
| 167 | ANDREOLA | ALESSANDRO | 1996 | M |
| 168 | BETETTO | ELI | 1946 | M |
| 169 | BIASIOL | MASSIMO | 1979 | M |
| 170 | BOLOGNA | GIANLUCA | 1978 | M |
| 171 | BULDO | ELISA | 1983 | F |
| 172 | CAMPODALL'ORTO | ANDREA | 1980 | M |
| 173 | DA ROS | FABRICE | 1968 | M |
| 174 | DAMO | STEFANO | 1971 | M |
| 175 | DE ROSA | MARCO | 1972 | M |
| 176 | DEL SIGNORE | ENRICA | 1981 | F |
| 177 | FOLTRAN | ANDREA | 1980 | M |
| 178 | MARCON | MICHELE | 1983 | M |
| 179 | POL | MARZIO | 1955 | M |
| 180 | ROSSI | FULVIO | 1964 | M |
| 181 | TONON | ALESSANDRO | 1977 | M |
| 182 | ZANINI | SILVIA | 1979 | F |

Gli altri 33 atleti dei quattro riepiloghi erano gia in anagrafica, quasi tutti fra i 58 censiti
con lo storico 2003: il lavoro di ieri ha fatto risparmiare due terzi del censimento.

FOLTRAN ANDREA (177) resta senza risultati collegati: nel PDF compare solo con codice ASS.

## 3. Il caso ANDREOLA e chiuso

Hai confermato che **ANDREOLA ALESSANDRO e un atleta Ranazzurra a se**, non una storpiatura di
ANDREON. L'ho censito (id 167) e gli ho attribuito la riga rimasta in sospeso dall'import di ieri:
50 stile libero a Roncade il 14/12/2003 in 00:29.3, race 22334, competition 1480. Quella
manifestazione passa da 39 a 40 risultati ed e ora completa.

L'anno di nascita resta il **1996** stampato sul PDF, che vorrebbe dire sette anni a Roncade 2003.
Se conosci l'anno giusto basta una UPDATE su `athletes.birth_date`.

## 4. Risultati

| manifestazione | righe nei PDF | ASS scartate | inserite |
|---|---|---|---|
| sdona_2004 | 67 | 8 | 59 |
| oderzo_2004 | 78 | 5 | 71 |
| belluno_2004 | 53 | 4 | 49 |
| vittorio_2004 | 38 | 5 | 32 |
| Roncade 2003 (riga ANDREOLA) | - | - | 1 |
| **totale** | **236** | **22** | **212** |

Le 22 righe ASS sono assenze e restano fuori. La riga RIT di ANDREETTA JOHNNY sui 200 stile a
Belluno e stata inserita con `final_time` NULL: ritiro, quindi gara disputata.
`athlete_races.group` NULL come su tutto lo storico. Escluse le 28 righe di RANAZZURRA Lido.

## 5. Verifica

Ricostruito dai PDF l'insieme atteso di terne (race_id, athlete_id, final_time) e confrontato col DB
via md5 della stringa ordinata. **Tutte e cinque le manifestazioni toccate coincidono.**

| competition | righe | md5 |
|---|---|---|
| 1480 | 40 | `bbe98241faa69820` |
| 1482 | 59 | `6690903547ba923a` |
| 1483 | 71 | `da4948558afc35bd` |
| 1484 | 49 | `051f3adaa36100b6` |
| 1485 | 32 | `9670388cd5f6e008` |

Zero doppioni nelle quattro manifestazioni 2004, zero chiavi orfane in tutto il DB, zero gare nuove
rimaste senza risultati. Le quattro sequence (athletes, races, athlete_races, competitions) erano
gia allineate prima di iniziare e lo sono ancora: **nessun INSERT e fallito**, il controllo
preventivo introdotto ieri funziona.

## 6. Due cose in sospeso

**OMETTO GIULIA, anno 1992**, non censita e i suoi 3 risultati non inseriti, come mi hai chiesto:
50 stile a Oderzo 00:36.8, 50 rana a Oderzo 00:44.4, 50 rana alla finale di Vittorio 00:43.5,
tutti e tre in fogli Assoluti Maschi Master. Hai indicato che va trattata come **femmina** seguendo
il nome: appena confermi, la inserisco con `sex = false` e i tre risultati vanno nelle race 22355,
22353 e 22369.

**Un tempo palesemente sbagliato nel PDF.** A S. Dona' ZANINI SILVIA risulta ventesima nei 100 rana
femmine con **14:56.7**, subito dopo un 02:03.4. E impossibile per un 100 rana ed e un errore del
riepilogo originale, non dell'estrazione: la riga stampata dice proprio cosi. L'ho caricata fedele
alla fonte, ma e **l'unico tempo sopra i 10 minuti su una gara fino ai 200 m in tutto il database**,
quindi falsera qualunque calcolo di personale o di media sui 100 rana. Se preferisci te la metto a
NULL lasciando la partecipazione: dimmi tu, non la tocco di mia iniziativa.
