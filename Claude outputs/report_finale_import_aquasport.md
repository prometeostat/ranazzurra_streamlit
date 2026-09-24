# Report finale import PDF Aquasport 2025/26

Eseguito il 22/09/2026 sul DB `swim` (Aiven), dopo conferma.

## Cosa e' stato scritto

| operazione | tabella | record |
|---|---|---|
| correzione tempi errati | athlete_races | 5 (UPDATE) |
| censimento atleti mancanti | athletes | 26 (INSERT, id 82-107) |
| caricamento risultati | athlete_races | 196 (INSERT, id 7006-7201) |

Nessuna cancellazione, nessuna manifestazione o gara creata: tutte e sei le competitions e tutte le races erano gia' presenti.

## 1. Correzioni (5 UPDATE)

| record | gara | atleta | prima | dopo |
|---|---|---|---|---|
| ar 344 | g1 staffetta 4x50 MX (race 32) | BABUIN FRANCESCO | 02:23.7 | **02:23.5** |
| ar 345 | g1 staffetta 4x50 MX (race 32) | GALBINCEA EMMA | 02:23.7 | **02:23.5** |
| ar 346 | g1 staffetta 4x50 MX (race 32) | PIARULLI VITTORIA | 02:23.7 | **02:23.5** |
| ar 556 | g3 100 Rana (race 76) | MASIN STEFANO | 01:18.5 | **01:13.0** |
| ar 1100 | g6 100 Stile Libero (race 132) | MAZZER STEFANO | 01:07.7 | **01:05.9** |

Su tutte e cinque e' stato valorizzato `last_modification_user_id = 2`. I tempi 01:18.5 e 01:07.7 non sono andati persi: sono rientrati come righe nuove intestate a TONON MARCO e FADELLI GIOVANNI, i loro veri proprietari.

## 2. Atleti censiti (26)

Tutti con `company_id = 37`, `birth_date = 01/01/<anno>`, `is_deleted = true` (come Babuin, Piarulli, Tome', Carniel), `creation_user_id = 2`, `fin_code` e `web_id` NULL perche' il PDF non li riporta.

| id | cognome | nome | nascita | sesso |
|---|---|---|---|---|
| 82 | BERNARDI | GIULIO | 2007-01-01 | M |
| 83 | BERTAZZON | MATTEO | 2011-01-01 | M |
| 84 | BEUKEMA | TERESA | 2010-01-01 | F |
| 85 | BOTTEON | NICOLA | 2009-01-01 | M |
| 86 | BRAVIN | GABRIELE | 2011-01-01 | M |
| 87 | BREDA | GIORDANO | 2011-01-01 | M |
| 88 | CARLESSO | MATTIA | 2010-01-01 | M |
| 89 | D'ALISE | SPARTACO | 2012-01-01 | M |
| 90 | DAL POS | SAMUELE | 2007-01-01 | M |
| 91 | GAVA | LEONE | 2011-01-01 | M |
| 92 | GONG YISHENG | MATTEO | 2012-01-01 | M |
| 93 | MASCELLANI | IRENE | 2012-01-01 | F |
| 94 | MASCHIO | MARTA | 2007-01-01 | F |
| 95 | MODOLO | ESTER | 2010-01-01 | F |
| 96 | PAGOTTO | GAIA | 2012-01-01 | F |
| 97 | PALFERENT | ALESSIA | 2008-01-01 | F |
| 98 | PERIN | LEONARDO | 2008-01-01 | M |
| 99 | PIARULLI | FILIPPO | 2011-01-01 | M |
| 100 | POL | ADELE | 2012-01-01 | F |
| 101 | REBULI | TOMMASO | 2012-01-01 | M |
| 102 | SALAMON | GRETA | 2008-01-01 | F |
| 103 | SOLDA' | BENEDETTA | 2010-01-01 | F |
| 104 | TERZARIOL | NADIA | 2012-01-01 | F |
| 105 | VINERA | NICOLO' | 2008-01-01 | M |
| 106 | WU PEIQIANG | WILLIAM | 2010-01-01 | M |
| 107 | ZAGO | MIA | 2012-01-01 | F |

## 3. Risultati caricati (196)

| giornata | data | competition | righe prima | inserite | righe dopo |
|---|---|---|---|---|---|
| g1 | 2025-11-09 | 10 | 53 | 23 | 76 |
| g2 | 2026-01-18 | 15 | 47 | 38 | 85 |
| g3 | 2026-02-07 | 17 | 33 | 40 | 73 |
| g4 | 2026-03-15 | 16 | 35 | 21 | 56 |
| g5 | 2026-04-19 | 22 | 33 | 36 | 69 |
| g6 | 2026-05-09 | 23 | 43 | 38 | 81 |
| **totale** | | | **244** | **196** | **440** |

Di queste, 193 appartengono ai 26 atleti appena censiti e 3 ad atleti gia' in anagrafica:

- **TONON MARCO**, g3 100 Rana, 01:18.5, race 76
- **PIARULLI VITTORIA**, g4 4x50 Stile Libero (staffetta), 02:03.4, race 67
- **FADELLI GIOVANNI**, g6 100 Stile Libero, 01:07.7, race 132

Sei righe hanno `final_time` NULL perche' nel PDF portano il codice SQU: PIARULLI FILIPPO (g1 100 dorso), ZAGO MIA (g1 100 misti e g3 50 stile), GAVA LEONE (g1 100 misti), PALFERENT ALESSIA (g2 100 misti), BOTTEON NICOLA (g3 400 stile). Le 13 righe ASS non sono state inserite: sono assenze, l'atleta non ha nuotato.

`athlete_races.group` lasciato NULL su tutte le 196 righe, coerente con le 244 preesistenti delle stesse sei manifestazioni. La categoria resta calcolabile a runtime: ora tutti i 58 atleti hanno una data di nascita.

## 4. Verifica finale

Ricostruito dai sei PDF l'insieme atteso di terne (race_id, athlete_id, final_time) e confrontato con il contenuto reale del DB tramite md5 della stringa ordinata. **Tutte e sei le manifestazioni coincidono esattamente.**

| competition | righe attese | righe a DB | md5 atteso | md5 a DB | esito |
|---|---|---|---|---|---|
| 10 (g1) | 76 | 76 | `fd42f0c52017` | `fd42f0c52017` | identico |
| 15 (g2) | 85 | 85 | `93d67a592821` | `93d67a592821` | identico |
| 17 (g3) | 73 | 73 | `d34a7d4f8d0d` | `d34a7d4f8d0d` | identico |
| 16 (g4) | 56 | 56 | `b24ce58b7ab2` | `b24ce58b7ab2` | identico |
| 22 (g5) | 69 | 69 | `874fa28332b7` | `874fa28332b7` | identico |
| 23 (g6) | 81 | 81 | `8e853645bf37` | `8e853645bf37` | identico |

Altri controlli, tutti puliti:

- 0 doppioni (race_id, athlete_id, final_time) nelle sei manifestazioni;
- 0 righe con `race_id` orfano;
- tutti i 26 atleti nuovi hanno almeno un risultato collegato;
- `athlete_races` passa da 4459 a 4655 righe, `athletes` da 49 a 75.

## 5. Un intoppo incontrato e risolto

Il primo INSERT dei risultati e' fallito con `duplicate key value violates unique constraint
"athlete_races_pkey"`: la sequence `athlete_races_id_seq` era ferma a 6593 mentre il massimo id
della tabella era 7005, segno che in passato qualche import ha scritto gli id espliciti senza
riallineare il contatore. L'INSERT e' andato in rollback completo (nessuna riga parziale, conteggio
verificato subito dopo), ho fatto `ALTER SEQUENCE athlete_races_id_seq RESTART WITH 7006` e ripetuto.

**Vale la pena controllare anche le altre sequence** prima del prossimo import automatico: se lo
scraper FIN Veneto scrive id espliciti, lo stesso problema si ripresenta su `races` e `competitions`.

## 6. Due punti da confermare quando puoi

1. **GONG YISHENG MATTEO** (id 92) e' stato spezzato in cognome `GONG YISHENG` + nome `MATTEO`, per
   analogia con WU PEIQIANG / WILLIAM che mi hai confermato. Se sul tesseramento FIN e' diverso basta
   una UPDATE sui due campi.
2. **Quattro righe della 5a giornata nei 200 stile (race 117)**: PIARULLI FILIPPO, PERIN LEONARDO,
   D'ALISE SPARTACO e REBULI TOMMASO. Dato che per DRIOLI il foglio "200 Stile Libero" conteneva in
   realta' una prestazione di farfalla, quel foglio mescola gli stili e non posso escludere che
   qualcuno di questi quattro fosse anch'esso a farfalla. Se lo sai, si spostano sulla race 126.

## 7. Nota sulla staffetta 8x50 della 6a giornata

Ranazzurra ha schierato due squadre: 04:05.1 (a DB con tutti e 8 i frazionisti, presi a suo tempo dal
sito) e 04:35.7. Della seconda il PDF stampa solo 4 nomi su 8 (PIARULLI FILIPPO, BRAVIN, SALAMON,
MODOLO), perche' il riepilogo natatoria mostra due frazionisti sopra e due sotto la riga squadra
indipendentemente dalla lunghezza della staffetta. Le altre quattro frazioni restano ignote: se
servono, vanno prese dal sito e non dal PDF.
