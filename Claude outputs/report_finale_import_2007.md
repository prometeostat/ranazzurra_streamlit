# Report finale import PDF 2007

Eseguito il 23/09/2026 sul DB `swim` (Aiven), dopo conferma.

## Cosa e' stato scritto

| operazione | tabella | record |
|---|---|---|
| rinomina manifestazioni | competitions | 3 (1218, 1219, 1221) |
| nuova manifestazione | competitions | 1 (id 1491) |
| nuove gare | races | 22 (id 22420-22441) |
| atleti censiti | athletes | 8 (id 214-221) |
| risultati | athlete_races | 152 (id 7843-7994) |

`athlete_races` da 5296 a 5448, `races` da 2231 a 2253.

## 1. Il parser avrebbe perso l'83% di una giornata

Il riepilogo di **Belluno 2007 e a cronometraggio automatico** (`Cron: A`) e i tempi hanno **due
decimali**: `02:06.60`, `00:26.20`, `01:08.70`. La regex del tempo ne accettava uno solo e al primo
giro ha scartato **207 righe** di quel documento, tenendone 5 su 30 di Ranazzurra.

L'ha intercettato il controllo di sempre: occorrenze di "RANAZZURRA" nel testo grezzo contro righe
ricostruite (30 contro 5). Corretta la regex per accettare uno o due decimali, anche sui parziali di
staffetta fra parentesi, i quattro documenti tornano esatti con zero righe non interpretate.

**Questo controllo e l'unica cosa che separa un import corretto da uno silenziosamente monco.**

## 2. Manifestazioni

| id | data | sede | vasca | cron | risultati | nome |
|---|---|---|---|---|---|---|
| 1218 | 2007-01-20 | San Donà di Piave | 25 m | M | 60 | 2ª Giornata Circuito Attività Masters |
| 1219 | 2007-05-20 | Belluno | 25 m | A | 26 | Trofeo Master ASD Nuoto Belluno |
| 1491 | 2007-06-23 | Spresiano | 50 m | M | 25 | Finale Masters 2007 Circuito Sinistra Piave |
| 1221 | 2007-12-02 | Valdobbiadene | 25 m | M | 47 | 1ª Giornata Circuito Master 2007/08 |

Le tre esistenti erano di nuovo competitions costruite sulla carriera di VEDOVELLI DANILA, con due
gare ciascuna: tutti e sei i suoi tempi verificati contro il PDF e coincidenti. La 1219 aveva gia
`timing = AUTOMATICO`, coerente col `Cron: A`, e non e stata toccata.

Sui titoli ho usato quelli che avevo proposto. Due note.

**Belluno**: il PDF non porta il nome della manifestazione, solo `ASD NUOTO BELLUNO` in testa ai
fogli, quindi ho messo il titolo neutro "Trofeo Master ASD Nuoto Belluno - Belluno". Se sai che e la
continuazione della serie del "7° Trofeo Città di Belluno" (competition 29, 2006), basta una UPDATE
per farlo diventare "8° Trofeo Città di Belluno".

**Valdobbiadene**: la nuova si chiama "1ª Giornata Circuito Master 2007/08 - Valdobbiadene" con la
stagione nel titolo. La 1217 del 03/12/2006 e rimasta "1ª Giornata Circuito Master - Valdobbiadene",
senza stagione, perche' non mi avevi detto di allinearla: le due restano distinguibili solo per data.
Se vuoi la sistemo in un secondo.

## 3. Atleti censiti (8)

| id | cognome | nome | anno |
|---|---|---|---|
| 214 | DAL CIN | WALTER | 1983 |
| 215 | DAVANZO | WALTER | 1962 |
| 216 | GHIRARDO | VALENTINA | 1987 |
| 217 | GIRARDI | GEMMA | 1949 |
| 218 | SILVESTRIN | STEFANO | 1985 |
| 219 | TOPAN | MAURO | 1982 |
| 220 | ZANETTI | LORENZO | 1982 |
| 221 | ZULIANI | CRISTINA | 1974 |

Gli altri 49 dei 57 erano gia in anagrafica. Tenuti separati da chi ha il cognome simile:
GHIRARDO VALENTINA non e GHIRARDO LETIZIA (192), DAVANZO WALTER non e DAVANZO GESSICA (188),
GIRARDI GEMMA non e GIRARDI ERMES (134) ne DOPPIERI GEMMA (125).

**TALAMINI PAOLO** (id 155) era in anagrafica dal 2003 con zero risultati, perche' nei PDF compariva
solo come assente. Adesso ne ha quattro: tre gare regolari e un ritiro sui 200 stile a Belluno.

## 4. Le staffette di Belluno non hanno prodotto nulla

I due fogli di staffetta 4x50 stile, i primi che compaiono nello storico, hanno **tutte le squadre
marcate ASS**: cinque fra i maschi e quattro fra le femmine, nessun tempo e nessuna posizione. Gara
annunciata e non disputata, niente da importare e nessuna race creata.

## 5. Risultati

| manifestazione | righe nei PDF | ASS | gia a DB | inserite |
|---|---|---|---|---|
| sdona_2007 | 64 | 4 | 2 | 58 |
| belluno_2007 | 29 | 3 | 2 | 24 |
| spresiano_2007 | 25 | 0 | 0 | 25 |
| valdobbiadene_2007 | 47 | 0 | 2 | 45 |
| **totale** | **165** | **7** | **6** | **152** |

Quattro righe con `final_time` NULL: due squalifiche (MENIS ALESSANDRO 50 stile a San Donà,
BETTIOL GIULIA 50 dorso a Valdobbiadene) e due ritiri (TALAMINI PAOLO 200 stile a Belluno,
GRANZIERA SERENA 400 stile a Valdobbiadene). Nessun tempo anomalo.

## 6. Verifica

md5 dell'insieme atteso di terne (race_id, athlete_id, final_time) contro il DB. **Tutte e quattro
le manifestazioni coincidono.**

| competition | righe | md5 |
|---|---|---|
| 1218 | 60 | `47eac266e8ca7eb3` |
| 1219 | 26 | `2e1db78653b09df6` |
| 1491 | 25 | `1f8bbecdca24e200` |
| 1221 | 47 | `2436f822b72c7d35` |

Zero doppioni, zero chiavi orfane, zero gare nuove senza risultati, zero atleti nuovi senza gare.
Le quattro sequence allineate.

## 7. Qualcun altro sta lavorando sul database

Il controllo preliminare delle sequence ha trovato `athletes` a **213** invece dei 205 che avevo
lasciato ieri. Non era un disallineamento: sono **otto atleti inseriti oggi alle 15:05-15:19 da
`creation_user_id = 1`**, tutti nati fra il 2010 e il 2013, `is_deleted = false`, company 37:
ADORNI OLIVER UMBERTO, CASAGRANDE CAMILLA, CESCHIN ALESSANDRO, FAVRETTO MADDALENA, FERRARI JACOPO,
PENNISI LUIGI, ZAMPOLLI RAPHAEL e MARCO SERGHEJ (quest'ultimo senza data di nascita).

Sono giovani della squadra attuale, nessuno in conflitto con gli otto dello storico che dovevo
censire. Li ho verificati uno per uno prima di procedere. Vale pero' la pena saperlo: **il database
non e piu' solo mio durante questi import**, quindi il controllo delle sequence e degli id va fatto
sempre subito prima di scrivere, non una volta per sessione.

## 8. Stato dello storico

Le **25 giornate del circuito Master** ora a DB, dal 18/01/2003 al 02/12/2007, contengono
**812 risultati di 110 atleti distinti**. Il circuito e completo per 2003, 2004, 2005, 2006 e 2007.
