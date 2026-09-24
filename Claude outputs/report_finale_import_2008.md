# Report finale import PDF 2008

Inserimento eseguito il 23/09/2026 dopo nulla osta, con inclusione delle righe `RANAZZURRA
SPRESIANO` sotto la società Ranazzurra SSD (company 37) come da tua indicazione.

## Cosa è stato scritto

| passo | oggetto | esito |
|---|---|---|
| 1 | rinomina competition **1222** → `3ª Giornata Circuito Master 2007/08 - Oderzo` | ok |
| 2 | rinomina competition **1223** → `Trofeo Master ASD Nuoto Belluno - Belluno` | ok |
| 3 | rinomina competition **1402** → `1ª Giornata Circuito Master 2008/09 - Valdobbiadene` | ok |
| 4 | nuova competition **1492** `2ª Giornata Circuito Master 2007/08 - San Donà di Piave` | ok |
| 5 | 3 atleti nuovi, id **222-224** | ok |
| 6 | 19 races, id **22442-22460** | ok |
| 7 | 158 risultati, id **7995-8152** | ok |

La nuova competition 1492 è impostata come le altre nate da PDF: 02/02/2008, vasca 25,
`timing = AUTOMATICO` (il riepilogo è a cronometraggio automatico), `scraping_website_id = 2`,
`web_id` NULL, `creation_user_id = 2`.

### Atleti censiti

| id | cognome | nome | nascita | sesso | società |
|---|---|---|---|---|---|
| 222 | BARBON | LINA | 01/01/1965 | F | 37 |
| 223 | BINOTO | DENIS | 01/01/1975 | M | 37 |
| 224 | BRINO | WALTER | 01/01/1963 | M | 37 |

Data di nascita al 01/01 dell'anno letto dal PDF e `is_deleted = true`, come tutti gli altri atleti
storici non più tesserati.

## Verifica

Checksum md5 calcolato in Python sui dati attesi e riletto da Postgres sulla tripla
`race_id:athlete_id:final_time`, per competition. **Tutti e quattro coincidono.**

| competition | manifestazione | righe | md5 |
|---|---|---|---|
| 1222 | Oderzo 16/03/2008 | 46 | `8f8049897a286c5ef93615cedb398843` |
| 1223 | Belluno 18/05/2008 | 55 | `1128729c72711c4e0d091ce1f3ef8c7e` |
| 1402 | Valdobbiadene 30/11/2008 | 26 | `e5f035848bfc05881e7eceb9cb08d2e0` |
| 1492 | San Donà 02/02/2008 | 37 | `053119ab2210d4b461d85ab735cacb1e` |

Le righe includono le 6 preesistenti di VEDOVELLI e FOLTRAN, riusate e non duplicate. Controllo
esplicito sulle coppie `(race_id, athlete_id)` nelle quattro competitions: **zero duplicati**.

## Stato del database

| tabella | prima | dopo | delta | sequence |
|---|---|---|---|---|
| athletes | 189 | 192 | +3 | 224, allineata |
| races | 2253 | 2272 | +19 | 22460, allineata |
| athlete_races | 5448 | 5606 | +158 | 8152, allineata |
| competitions | 538 | 539 | +1 | 1492, allineata |

Lo storico master arriva ora a **28 manifestazioni dal 18/01/2003 al 30/11/2008, 931 risultati,
114 atleti distinti**.

## Record non inseriti, per scelta

- **4 righe ASS**: FACCHINI STEFANO (50 stile) e CALESSO GIORGIO (100 rana) e GIRARDI ERMES
  (100 dorso) a San Donà, FRARE MAURIZIO (50 stile) a Oderzo. Assenti, gara non disputata da loro.
- **8 righe di staffetta 4x50 stile a Belluno**, maschile e femminile: tutte le squadre iscritte
  erano ASS, la gara non è stata disputata. Le due races non sono state create.
- **il quinto PDF**, `spresiano_20082.pdf`, identico byte per byte a quello già importato nella
  competition 1481: nessuna scrittura.

Inserito invece con `final_time` NULL **un RIT**: FACCHINI STEFANO sui 200 stile a Belluno
(race 22454), gara disputata e non conclusa.

## Anomalie residue

Nessuna nuova. Restano aperte da prima:

- il **14:56.7 di ZANINI SILVIA** sui 100 rana a San Donà 2004 (race 22350), impossibile, errore
  del riepilogo di origine, caricato fedelmente. È l'unico tempo sopra i 10 minuti su una distanza
  fino ai 200 m in tutto il database e falsa qualsiasi media o personale sui 100 rana.
- la competition **1219** si chiama `Trofeo Master ASD Nuoto Belluno - Belluno` e la 29
  `7° Trofeo Città di Belluno`: se il trofeo di Belluno è lo stesso evento numerato di anno in anno,
  1219 sarebbe l'8° e la 1223 appena rinominata il 9°. Non l'ho dedotto da solo, serve una conferma.

## Nota di metodo, per la prossima volta

La sigla `RANAZZURRA SPRESIANO` compare per la prima volta nel riepilogo del 30/11/2008 e d'ora in
avanti è da attendersi nei PDF della stagione 2008/09 e successive. Da questo lotto la regola è:
**va trattata come Ranazzurra SSD, company 37**, al pari di `RANAZZURRA S.S.D.`. Resta esclusa solo
`RANAZZURRA Lido`, che è la società 57, diversa.
