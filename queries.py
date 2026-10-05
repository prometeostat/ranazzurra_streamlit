"""
queries.py — SQL parametrizzato.

Tutte le query prendono i confini di stagione come parametri: niente piu'
date hardcoded, la stagione si sceglie a runtime (vedi season.py).

Convenzioni del DB da tenere a mente:
  - athletes.last_name ha spazi in coda su meta' anagrafica -> btrim() ovunque
  - split_times contiene TEMPI DI FRAZIONE, non cumulati (verificato: la somma
    coincide col final_time nel 98% delle gare). L'ordine e' quello di id.
  - athlete_races non ha la posizione in gara e il DB contiene solo i nostri
    tesserati: le classifiche sono interne alla squadra, il confronto con gli
    avversari passa dal punteggio FIN.
"""

# ══════════════════════════════════════════════════════════════════
# Anagrafica
# ══════════════════════════════════════════════════════════════════

# %s: season_end_year, season_start, season_end
ATHLETES_SQL = """
SELECT
    a.id                                        AS athlete_id,
    btrim(a.last_name) || ' ' || btrim(a.first_name) AS full_name,
    btrim(a.first_name)                         AS first_name,
    btrim(a.last_name)                          AS last_name,
    EXTRACT(YEAR FROM AGE(a.birth_date))::int   AS age,
    EXTRACT(YEAR FROM a.birth_date)::int        AS birth_year,
    CASE WHEN a.sex THEN 'M' ELSE 'F' END       AS sex,
    (%s - EXTRACT(YEAR FROM a.birth_date)::int) / 5 * 5 AS master_cat,
    a.fin_code,
    btrim(co_s.name)                            AS team
FROM athletes a
LEFT JOIN companies co_s ON co_s.id = a.company_id AND co_s.is_deleted = FALSE
WHERE a.is_deleted = FALSE
  AND a.is_athlete = TRUE
  AND EXISTS (
    SELECT 1 FROM athlete_races ar
    JOIN races r        ON r.id  = ar.race_id        AND r.is_deleted  = FALSE
    JOIN competitions c ON c.id  = r.competition_id  AND c.is_deleted  = FALSE
    JOIN race_events re ON re.id = r.race_event_id   AND re.is_deleted = FALSE
    WHERE ar.athlete_id  = a.id
      AND ar.is_deleted  = FALSE
      AND ar.final_time IS NOT NULL
      AND re.is_relay    = FALSE
      AND c.start_date BETWEEN %s AND %s
  )
ORDER BY btrim(a.last_name), btrim(a.first_name)
"""

# Tutti gli atleti in anagrafica, anche senza gare in stagione.
# %s: season_end_year
ALL_ATHLETES_SQL = """
SELECT
    a.id                                        AS athlete_id,
    btrim(a.last_name) || ' ' || btrim(a.first_name) AS full_name,
    btrim(a.first_name)                         AS first_name,
    btrim(a.last_name)                          AS last_name,
    EXTRACT(YEAR FROM AGE(a.birth_date))::int   AS age,
    EXTRACT(YEAR FROM a.birth_date)::int        AS birth_year,
    CASE WHEN a.sex THEN 'M' ELSE 'F' END       AS sex,
    (%s - EXTRACT(YEAR FROM a.birth_date)::int) / 5 * 5 AS master_cat,
    a.fin_code,
    btrim(co_s.name)                            AS team,
    a.is_deleted,
    a.is_staff
FROM athletes a
LEFT JOIN companies co_s ON co_s.id = a.company_id AND co_s.is_deleted = FALSE
WHERE a.is_athlete = TRUE
ORDER BY btrim(a.last_name), btrim(a.first_name)
"""

# Verifica credenziali: codice FIN + data di nascita.
# %s: fin_code, birth_date
AUTH_BY_FIN_SQL = """
SELECT
    a.id                                        AS athlete_id,
    btrim(a.last_name) || ' ' || btrim(a.first_name) AS full_name,
    a.fin_code,
    a.is_deleted
FROM athletes a
WHERE a.fin_code = %s
  AND a.birth_date = %s
LIMIT 1
"""

# Mapping email -> atleta, per il login OIDC.
# %s: email (minuscola)
AUTH_BY_EMAIL_SQL = """
SELECT
    a.id                                        AS athlete_id,
    btrim(a.last_name) || ' ' || btrim(a.first_name) AS full_name,
    a.fin_code
FROM athletes a
WHERE lower(btrim(a.email)) = %s
  AND a.is_deleted = FALSE
LIMIT 1
"""

# ══════════════════════════════════════════════════════════════════
# Scheda atleta
# ══════════════════════════════════════════════════════════════════

# %s: athlete_id, season_start, season_end
SEASON_META_SQL = """
SELECT
    COUNT(ar.id)                                 AS total_races,
    COUNT(DISTINCT r.competition_id)             AS total_competitions,
    COUNT(DISTINCT re.id)                        AS distinct_events,
    MAX(co.start_date)                           AS last_competition,
    AVG(ar.fin_score)::float                     AS avg_fin_score,
    MAX(ar.fin_score)                            AS best_fin_score
FROM athlete_races ar
JOIN races        r  ON r.id  = ar.race_id       AND r.is_deleted = FALSE
JOIN competitions co ON co.id = r.competition_id  AND co.is_deleted = FALSE
JOIN race_events  re ON re.id = r.race_event_id   AND re.is_deleted = FALSE
WHERE ar.athlete_id  = %s
  AND ar.is_deleted  = FALSE
  AND ar.final_time IS NOT NULL
  AND re.is_relay    = FALSE
  AND co.start_date BETWEEN %s AND %s
"""

# %s: curr_start, curr_end, prev_start, prev_end, curr_start, curr_end,
#     athlete_id, curr_start, curr_end
PB_SQL = """
SELECT
    s.name                                                  AS stroke,
    d.type                                                  AS distance,
    r.pool_length,
    s.name || ' ' || d.type || 'm'                          AS event_label,

    MIN(CASE WHEN co.start_date BETWEEN %s AND %s
             THEN EXTRACT(EPOCH FROM ar.final_time) END)::float  AS pb_curr_sec,

    MIN(CASE WHEN co.start_date BETWEEN %s AND %s
             THEN EXTRACT(EPOCH FROM ar.final_time) END)::float  AS pb_prev_sec,

    MIN(EXTRACT(EPOCH FROM ar.final_time))::float            AS pb_alltime_sec,

    COUNT(CASE WHEN co.start_date BETWEEN %s AND %s
               THEN ar.id END)                               AS swims_curr,

    COUNT(ar.id)                                             AS swims_total
FROM athlete_races ar
JOIN races        r  ON r.id  = ar.race_id       AND r.is_deleted = FALSE
JOIN competitions co ON co.id = r.competition_id  AND co.is_deleted = FALSE
JOIN race_events  re ON re.id = r.race_event_id   AND re.is_deleted = FALSE
JOIN strokes      s  ON s.id  = re.stroke_id      AND s.is_deleted  = FALSE
JOIN distances    d  ON d.id  = re.distance_id    AND d.is_deleted  = FALSE
WHERE ar.athlete_id  = %s
  AND ar.is_deleted  = FALSE
  AND ar.final_time IS NOT NULL
  AND re.is_relay    = FALSE
GROUP BY s.name, d.type, r.pool_length
HAVING MIN(CASE WHEN co.start_date BETWEEN %s AND %s
                THEN EXTRACT(EPOCH FROM ar.final_time) END) IS NOT NULL
ORDER BY s.name, CAST(d.type AS int), r.pool_length
"""

# %s: season_start, season_end, athlete_id
RANKING_SQL = """
WITH ranked AS (
    SELECT
        a.id                                          AS athlete_id,
        btrim(a.last_name) || ' ' || btrim(a.first_name) AS full_name,
        CASE WHEN a.sex THEN 'M' ELSE 'F' END        AS sex,
        s.name                                        AS stroke,
        d.type                                        AS distance,
        r.pool_length,
        MIN(EXTRACT(EPOCH FROM ar.final_time))::float AS pb_sec,
        TO_CHAR(MIN(ar.final_time), 'MI:SS.MS')       AS pb_fmt,
        RANK() OVER (
            PARTITION BY a.sex, s.name, d.type, r.pool_length
            ORDER BY MIN(EXTRACT(EPOCH FROM ar.final_time))
        )                                             AS rank_club,
        COUNT(*) OVER (
            PARTITION BY a.sex, s.name, d.type, r.pool_length
        )                                             AS n_club
    FROM athletes a
    JOIN athlete_races ar ON ar.athlete_id = a.id       AND ar.is_deleted = FALSE
    JOIN races         r  ON r.id = ar.race_id          AND r.is_deleted  = FALSE
    JOIN competitions  co ON co.id = r.competition_id   AND co.is_deleted = FALSE
    JOIN race_events   re ON re.id = r.race_event_id    AND re.is_deleted = FALSE
    JOIN strokes       s  ON s.id  = re.stroke_id       AND s.is_deleted  = FALSE
    JOIN distances     d  ON d.id  = re.distance_id     AND d.is_deleted  = FALSE
    WHERE a.is_deleted   = FALSE
      AND ar.is_deleted  = FALSE
      AND ar.final_time IS NOT NULL
      AND re.is_relay    = FALSE
      AND co.start_date BETWEEN %s AND %s
    GROUP BY a.id, a.last_name, a.first_name, a.sex,
             s.name, d.type, r.pool_length
)
SELECT * FROM ranked
WHERE athlete_id = %s
ORDER BY stroke, CAST(distance AS int), pool_length
"""

# %s: athlete_id, season_start, season_end
FREQUENCY_SQL = """
SELECT
    co.start_date                           AS comp_date,
    co.id                                   AS comp_id,
    COUNT(ar.id)                            AS races,
    COUNT(DISTINCT re.id)                   AS events,
    STRING_AGG(DISTINCT s.name, ', '
               ORDER BY s.name)             AS strokes_swum
FROM athlete_races ar
JOIN races        r  ON r.id  = ar.race_id       AND r.is_deleted = FALSE
JOIN competitions co ON co.id = r.competition_id  AND co.is_deleted = FALSE
JOIN race_events  re ON re.id = r.race_event_id   AND re.is_deleted = FALSE
JOIN strokes      s  ON s.id  = re.stroke_id      AND s.is_deleted  = FALSE
WHERE ar.athlete_id  = %s
  AND ar.is_deleted  = FALSE
  AND ar.final_time IS NOT NULL
  AND re.is_relay    = FALSE
  AND co.start_date BETWEEN %s AND %s
GROUP BY co.start_date, co.id
ORDER BY co.start_date
"""

# Trend completo, tutte le stagioni. %s: athlete_id
TREND_SQL = """
SELECT
    co.start_date                            AS comp_date,
    s.name || ' ' || d.type || 'm'           AS event_label,
    r.pool_length,
    EXTRACT(EPOCH FROM ar.final_time)::float AS time_sec,
    TO_CHAR(ar.final_time, 'MI:SS.MS')       AS time_fmt,
    ar.fin_score,
    CASE WHEN EXTRACT(MONTH FROM co.start_date) >= 9
         THEN EXTRACT(YEAR FROM co.start_date)::int
         ELSE EXTRACT(YEAR FROM co.start_date)::int - 1
    END                                      AS season_start_year
FROM athlete_races ar
JOIN races        r  ON r.id  = ar.race_id       AND r.is_deleted = FALSE
JOIN competitions co ON co.id = r.competition_id  AND co.is_deleted = FALSE
JOIN race_events  re ON re.id = r.race_event_id   AND re.is_deleted = FALSE
JOIN strokes      s  ON s.id  = re.stroke_id      AND s.is_deleted  = FALSE
JOIN distances    d  ON d.id  = re.distance_id    AND d.is_deleted  = FALSE
WHERE ar.athlete_id  = %s
  AND ar.is_deleted  = FALSE
  AND ar.final_time IS NOT NULL
  AND re.is_relay    = FALSE
ORDER BY event_label, r.pool_length, co.start_date
"""

# ══════════════════════════════════════════════════════════════════
# Gare e passaggi
# ══════════════════════════════════════════════════════════════════

# Elenco gare di un atleta in stagione. %s: athlete_id, season_start, season_end
RACES_SQL = """
SELECT
    ar.id                                    AS athlete_race_id,
    co.id                                    AS comp_id,
    co.start_date                            AS comp_date,
    co.type                                  AS comp_type,
    co.website_link,
    co.timing,
    s.name                                   AS stroke,
    d.type                                   AS distance,
    r.pool_length,
    s.name || ' ' || d.type || 'm'           AS event_label,
    EXTRACT(EPOCH FROM ar.final_time)::float AS time_sec,
    ar.fin_score,
    ar."group"                               AS category,
    (SELECT COUNT(*) FROM split_times st
      WHERE st.athlete_race_id = ar.id AND st.is_deleted = FALSE) AS n_split
FROM athlete_races ar
JOIN races        r  ON r.id  = ar.race_id       AND r.is_deleted = FALSE
JOIN competitions co ON co.id = r.competition_id  AND co.is_deleted = FALSE
JOIN race_events  re ON re.id = r.race_event_id   AND re.is_deleted = FALSE
JOIN strokes      s  ON s.id  = re.stroke_id      AND s.is_deleted  = FALSE
JOIN distances    d  ON d.id  = re.distance_id    AND d.is_deleted  = FALSE
WHERE ar.athlete_id  = %s
  AND ar.is_deleted  = FALSE
  AND ar.final_time IS NOT NULL
  AND re.is_relay    = FALSE
  AND co.start_date BETWEEN %s AND %s
ORDER BY co.start_date DESC, s.name, CAST(d.type AS int)
"""

# Parziali di una gara. %s: athlete_race_id
SPLITS_SQL = """
SELECT
    st.id,
    EXTRACT(EPOCH FROM st."time")::float AS seg_sec
FROM split_times st
WHERE st.athlete_race_id = %s
  AND st.is_deleted = FALSE
ORDER BY st.id
"""

# Tutte le gare con parziali di un atleta su una specialita', per confrontare
# le curve dei passaggi. %s: athlete_id, stroke, distance, pool_length
SPLITS_BY_EVENT_SQL = """
SELECT
    ar.id                                    AS athlete_race_id,
    co.start_date                            AS comp_date,
    EXTRACT(EPOCH FROM ar.final_time)::float AS time_sec,
    st.id                                    AS split_id,
    EXTRACT(EPOCH FROM st."time")::float     AS seg_sec
FROM athlete_races ar
JOIN races        r  ON r.id  = ar.race_id       AND r.is_deleted = FALSE
JOIN competitions co ON co.id = r.competition_id  AND co.is_deleted = FALSE
JOIN race_events  re ON re.id = r.race_event_id   AND re.is_deleted = FALSE
JOIN strokes      s  ON s.id  = re.stroke_id      AND s.is_deleted  = FALSE
JOIN distances    d  ON d.id  = re.distance_id    AND d.is_deleted  = FALSE
JOIN split_times  st ON st.athlete_race_id = ar.id AND st.is_deleted = FALSE
WHERE ar.athlete_id  = %s
  AND ar.is_deleted  = FALSE
  AND ar.final_time IS NOT NULL
  AND s.name = %s
  AND d.type = %s
  AND r.pool_length = %s
ORDER BY co.start_date, st.id
"""

# Personali di sempre per specialita'. %s: athlete_id
ALLTIME_PB_SQL = """
SELECT
    s.name                                        AS stroke,
    d.type                                        AS distance,
    r.pool_length,
    MIN(EXTRACT(EPOCH FROM ar.final_time))::float AS pb_alltime_sec,
    MIN(co.start_date)                            AS prima_gara
FROM athlete_races ar
JOIN races        r  ON r.id  = ar.race_id       AND r.is_deleted = FALSE
JOIN competitions co ON co.id = r.competition_id  AND co.is_deleted = FALSE
JOIN race_events  re ON re.id = r.race_event_id   AND re.is_deleted = FALSE
JOIN strokes      s  ON s.id  = re.stroke_id      AND s.is_deleted  = FALSE
JOIN distances    d  ON d.id  = re.distance_id    AND d.is_deleted  = FALSE
WHERE ar.athlete_id  = %s
  AND ar.is_deleted  = FALSE
  AND ar.final_time IS NOT NULL
  AND re.is_relay    = FALSE
GROUP BY s.name, d.type, r.pool_length
"""

# ══════════════════════════════════════════════════════════════════
# Confronto e classifiche di squadra
# ══════════════════════════════════════════════════════════════════

# Personali di piu' atleti nello stesso intervallo, con la gara in cui sono
# stati fatti: serve alla pagina Confronta, che sotto al tempo scrive data,
# punteggio FIN e manifestazione. DISTINCT ON tiene la riga piu' veloce di
# ogni atleta/specialita'/vasca; a parita' di tempo vince la piu' vecchia,
# come per il badge PB della scheda.
# %s: lista athlete_id, season_start, season_end
COMPARE_PB_SQL = """
SELECT * FROM (
    SELECT DISTINCT ON (a.id, s.name, d.type, r.pool_length)
        a.id                                          AS athlete_id,
        btrim(a.last_name) || ' ' || btrim(a.first_name) AS full_name,
        CASE WHEN a.sex THEN 'M' ELSE 'F' END         AS sex,
        s.name                                        AS stroke,
        d.type                                        AS distance,
        r.pool_length,
        s.name || ' ' || d.type || 'm'                AS event_label,
        EXTRACT(EPOCH FROM ar.final_time)::float      AS pb_sec,
        ar.fin_score                                  AS fin_score,
        co.start_date                                 AS comp_date,
        co."type"                                     AS comp_name,
        co.pdf_link,
        co.website_link
    FROM athletes a
    JOIN athlete_races ar ON ar.athlete_id = a.id      AND ar.is_deleted = FALSE
    JOIN races         r  ON r.id = ar.race_id         AND r.is_deleted  = FALSE
    JOIN competitions  co ON co.id = r.competition_id  AND co.is_deleted = FALSE
    JOIN race_events   re ON re.id = r.race_event_id   AND re.is_deleted = FALSE
    JOIN strokes       s  ON s.id  = re.stroke_id      AND s.is_deleted  = FALSE
    JOIN distances     d  ON d.id  = re.distance_id    AND d.is_deleted  = FALSE
    WHERE a.id = ANY(%s)
      AND ar.is_deleted  = FALSE
      AND ar.final_time IS NOT NULL
      AND re.is_relay    = FALSE
      AND co.start_date BETWEEN %s AND %s
    ORDER BY a.id, s.name, d.type, r.pool_length,
             EXTRACT(EPOCH FROM ar.final_time), co.start_date
) t
ORDER BY stroke, CAST(distance AS int), pool_length, pb_sec
"""

# Classifica di squadra: il miglior tempo di ogni atleta per specialita',
# vasca E STAGIONE. Ci sono dentro anche gli atleti non piu' attivi: il
# tempo resta un tempo della squadra, e chi ha smesso non sparisce dagli
# archivi. Nessun rischio di doppioni, in anagrafica non ci sono omonimi
# fra attivi e disattivati.
# La stagione serve perche' la categoria master cambia di anno in anno: un tempo del 2019 vale nella categoria di allora, non in
# quella di oggi. Chi filtra per categoria deve poter partire dalla riga
# giusta, e il filtro "tutte" si limita a prendere il minimo su tutte.
# La stagione si ricava dalla data: da settembre in poi e' quella che apre.
# %s: season_start, season_end
CLUB_RANKING_SQL = """
SELECT * FROM (
    SELECT DISTINCT ON (a.id, s.name, d.type, r.pool_length,
                        (CASE WHEN EXTRACT(MONTH FROM co.start_date) >= 9
                              THEN EXTRACT(YEAR FROM co.start_date)
                              ELSE EXTRACT(YEAR FROM co.start_date) - 1 END))
        a.id                                          AS athlete_id,
        btrim(a.last_name) || ' ' || btrim(a.first_name) AS full_name,
        CASE WHEN a.sex THEN 'M' ELSE 'F' END         AS sex,
        EXTRACT(YEAR FROM a.birth_date)::int          AS birth_year,
        s.name                                        AS stroke,
        d.type                                        AS distance,
        r.pool_length,
        s.name || ' ' || d.type || 'm'                AS event_label,
        (CASE WHEN EXTRACT(MONTH FROM co.start_date) >= 9
              THEN EXTRACT(YEAR FROM co.start_date)
              ELSE EXTRACT(YEAR FROM co.start_date) - 1 END)::int AS stagione,
        EXTRACT(EPOCH FROM ar.final_time)::float      AS pb_sec,
        co.start_date                                 AS comp_date,
        co."type"                                     AS comp_name,
        co.pdf_link,
        co.website_link,
        a.is_deleted                                  AS atleta_inattivo
    FROM athletes a
    JOIN athlete_races ar ON ar.athlete_id = a.id      AND ar.is_deleted = FALSE
    JOIN races         r  ON r.id = ar.race_id         AND r.is_deleted  = FALSE
    JOIN competitions  co ON co.id = r.competition_id  AND co.is_deleted = FALSE
    JOIN race_events   re ON re.id = r.race_event_id   AND re.is_deleted = FALSE
    JOIN strokes       s  ON s.id  = re.stroke_id      AND s.is_deleted  = FALSE
    JOIN distances     d  ON d.id  = re.distance_id    AND d.is_deleted  = FALSE
    WHERE ar.is_deleted  = FALSE
      AND ar.final_time IS NOT NULL
      AND re.is_relay    = FALSE
      AND co.start_date BETWEEN %s AND %s
    ORDER BY a.id, s.name, d.type, r.pool_length,
             (CASE WHEN EXTRACT(MONTH FROM co.start_date) >= 9
                   THEN EXTRACT(YEAR FROM co.start_date)
                   ELSE EXTRACT(YEAR FROM co.start_date) - 1 END),
             EXTRACT(EPOCH FROM ar.final_time), co.start_date
) t
ORDER BY stroke, CAST(distance AS int), pool_length, pb_sec
"""

# Punteggi FIN migliori della squadra in stagione.
# %s: season_start, season_end
FIN_LEADERBOARD_SQL = """
SELECT
    a.id                                          AS athlete_id,
    btrim(a.last_name) || ' ' || btrim(a.first_name) AS full_name,
    CASE WHEN a.sex THEN 'M' ELSE 'F' END         AS sex,
    s.name || ' ' || d.type || 'm'                AS event_label,
    r.pool_length,
    ar.fin_score,
    co.start_date                                 AS comp_date,
    EXTRACT(EPOCH FROM ar.final_time)::float      AS time_sec
FROM athletes a
JOIN athlete_races ar ON ar.athlete_id = a.id      AND ar.is_deleted = FALSE
JOIN races         r  ON r.id = ar.race_id         AND r.is_deleted  = FALSE
JOIN competitions  co ON co.id = r.competition_id  AND co.is_deleted = FALSE
JOIN race_events   re ON re.id = r.race_event_id   AND re.is_deleted = FALSE
JOIN strokes       s  ON s.id  = re.stroke_id      AND s.is_deleted  = FALSE
JOIN distances     d  ON d.id  = re.distance_id    AND d.is_deleted  = FALSE
WHERE a.is_deleted   = FALSE
  AND ar.is_deleted  = FALSE
  AND ar.fin_score IS NOT NULL
  AND re.is_relay    = FALSE
  AND co.start_date BETWEEN %s AND %s
ORDER BY ar.fin_score DESC
"""

# Stagioni disponibili a DB, per popolare il selettore.
SEASONS_SQL = """
SELECT DISTINCT
    CASE WHEN EXTRACT(MONTH FROM co.start_date) >= 9
         THEN EXTRACT(YEAR FROM co.start_date)::int
         ELSE EXTRACT(YEAR FROM co.start_date)::int - 1
    END AS season_start_year,
    COUNT(*) AS races
FROM athlete_races ar
JOIN races        r  ON r.id  = ar.race_id       AND r.is_deleted = FALSE
JOIN competitions co ON co.id = r.competition_id  AND co.is_deleted = FALSE
WHERE ar.is_deleted = FALSE
  AND ar.final_time IS NOT NULL
GROUP BY 1
ORDER BY 1 DESC
"""

# ══════════════════════════════════════════════════════════════════
# Anagrafica atleti (CRUD)
# ══════════════════════════════════════════════════════════════════
# Note sullo schema, verificate sul DB:
#   - creation_user_id e' NOT NULL con FK su users: gli inserimenti usano
#     l'utente tecnico (1 = system, 2 = devsupport), configurabile nei secrets
#   - sex e' un bool NOT NULL: TRUE = maschile
#   - is_deleted NON si cancella mai fisicamente, e' il flag "Attivo" al
#     contrario: TRUE significa atleta inattivo
#   - fin_code non ha vincolo di unicita' a DB, il controllo lo fa l'app

ATHLETES_ADMIN_SQL = """
SELECT
    a.id                        AS athlete_id,
    a.fin_code,
    btrim(a.first_name)         AS first_name,
    btrim(a.last_name)          AS last_name,
    a.sex,
    a.birth_date,
    a.email,
    a.is_deleted,
    a.is_athlete,
    a.is_staff,
    a.company_id,
    btrim(co_s.name)            AS team,
    (SELECT COUNT(*) FROM athlete_races ar
      WHERE ar.athlete_id = a.id AND ar.is_deleted = FALSE) AS n_gare
FROM athletes a
LEFT JOIN companies co_s ON co_s.id = a.company_id AND co_s.is_deleted = FALSE
ORDER BY btrim(a.last_name), btrim(a.first_name)
"""

# %s: fin_code, first_name, last_name, sex, birth_date, email, company_id, user_id
ATHLETE_INSERT_SQL = """
INSERT INTO athletes
    (fin_code, first_name, last_name, sex, birth_date, email,
     company_id, creation_user_id, is_deleted, is_athlete, is_staff)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, FALSE, %s, %s)
RETURNING id
"""

# %s: fin_code, first_name, last_name, sex, birth_date, email, user_id, athlete_id
ATHLETE_UPDATE_SQL = """
UPDATE athletes SET
    fin_code   = %s,
    first_name = %s,
    last_name  = %s,
    sex        = %s,
    birth_date = %s,
    email      = %s,
    is_athlete = %s,
    is_staff   = %s,
    last_modification_user_id = %s,
    last_modification_utc_date_time = (now() AT TIME ZONE 'utc')
WHERE id = %s
"""

# Soft delete. %s: user_id, athlete_id
ATHLETE_DEACTIVATE_SQL = """
UPDATE athletes SET
    is_deleted = TRUE,
    deletion_user_id = %s,
    deletion_utc_date_time = (now() AT TIME ZONE 'utc')
WHERE id = %s
"""

# Riattivazione. %s: user_id, athlete_id
ATHLETE_REACTIVATE_SQL = """
UPDATE athletes SET
    is_deleted = FALSE,
    deletion_user_id = NULL,
    deletion_utc_date_time = NULL,
    last_modification_user_id = %s,
    last_modification_utc_date_time = (now() AT TIME ZONE 'utc')
WHERE id = %s
"""

# Controllo duplicati sul codice FIN. %s: fin_code, athlete_id da escludere
ATHLETE_FIN_TAKEN_SQL = """
SELECT a.id, btrim(a.last_name) || ' ' || btrim(a.first_name) AS full_name
FROM athletes a
WHERE a.fin_code = %s AND a.id <> %s
LIMIT 1
"""

# Societa' per la tendina del form
COMPANIES_SQL = """
SELECT c.id AS company_id, btrim(c.name) AS name
FROM companies c
WHERE c.is_deleted = FALSE AND c.name IS NOT NULL
ORDER BY btrim(c.name)
"""

# ══════════════════════════════════════════════════════════════════
# Manifestazioni: agenda e anagrafica
# ══════════════════════════════════════════════════════════════════
# competitions.type e' il nome della manifestazione. A DB ci sono solo le
# manifestazioni dove abbiamo gareggiato, quindi l'agenda del futuro si
# popola a mano dall'anagrafica finche' lo scraper non prende i calendari.

# %s: season_start, season_end
AGENDA_SQL = """
WITH nostre AS (
    SELECT r.competition_id,
           COUNT(ar.id)                       AS nostre_gare,
           COUNT(DISTINCT ar.athlete_id)      AS nostri_atleti,
           STRING_AGG(DISTINCT r.pool_length::text, '/'
                      ORDER BY r.pool_length::text) AS vasche
    FROM races r
    JOIN athlete_races ar ON ar.race_id = r.id AND ar.is_deleted = FALSE
    WHERE r.is_deleted = FALSE
    GROUP BY r.competition_id
)
SELECT
    co.id                       AS comp_id,
    co.start_date,
    co.end_date,
    co."type"                   AS nome,
    co.timing,
    co.website_link,
    co.pdf_link,
    co.close_registration_date,
    btrim(org.name)             AS organizzatore,
    COALESCE(n.nostre_gare, 0)  AS nostre_gare,
    COALESCE(n.nostri_atleti, 0) AS nostri_atleti,
    n.vasche
FROM competitions co
LEFT JOIN nostre n   ON n.competition_id = co.id
LEFT JOIN companies org ON org.id = co.organizer_company_id AND org.is_deleted = FALSE
WHERE co.is_deleted = FALSE
  AND co.start_date BETWEEN %s AND %s
ORDER BY co.start_date DESC
"""

# Anagrafica completa, comprese le disattivate.
COMPETITIONS_ADMIN_SQL = """
SELECT
    co.id                       AS comp_id,
    co."type"                   AS nome,
    co.start_date,
    co.end_date,
    co.open_registration_date,
    co.close_registration_date,
    co.timing,
    co.website_link,
    co.pdf_link,
    co.max_races_per_athlete,
    co.is_deleted,
    (SELECT COUNT(*) FROM races r
      WHERE r.competition_id = co.id AND r.is_deleted = FALSE) AS n_gare
FROM competitions co
ORDER BY co.start_date DESC
"""

# %s: nome, start, end, apertura, chiusura, timing, sito, pdf, max_gare, user_id
COMPETITION_INSERT_SQL = """
INSERT INTO competitions
    ("type", start_date, end_date, open_registration_date,
     close_registration_date, timing, website_link, pdf_link,
     max_races_per_athlete, creation_user_id, is_deleted)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE)
RETURNING id
"""

# %s: nome, start, end, apertura, chiusura, timing, sito, pdf, max_gare,
#     user_id, comp_id
COMPETITION_UPDATE_SQL = """
UPDATE competitions SET
    "type"                  = %s,
    start_date              = %s,
    end_date                = %s,
    open_registration_date  = %s,
    close_registration_date = %s,
    timing                  = %s,
    website_link            = %s,
    pdf_link                = %s,
    max_races_per_athlete   = %s,
    last_modification_user_id = %s
WHERE id = %s
"""

# %s: user_id, comp_id
COMPETITION_DEACTIVATE_SQL = """
UPDATE competitions SET is_deleted = TRUE, deletion_user_id = %s WHERE id = %s
"""

# %s: user_id, comp_id
COMPETITION_REACTIVATE_SQL = """
UPDATE competitions SET is_deleted = FALSE, deletion_user_id = NULL,
       last_modification_user_id = %s
WHERE id = %s
"""

# Valori di cronometraggio gia' usati, per la tendina del form
TIMINGS_SQL = """
SELECT DISTINCT btrim(timing) AS timing
FROM competitions
WHERE timing IS NOT NULL AND btrim(timing) <> ''
ORDER BY 1
"""


# ══════════════════════════════════════════════════════════════════
# Registro accessi
# ══════════════════════════════════════════════════════════════════

# La tabella access_log tiene una riga per evento: entrata, uscita,
# tentativo fallito, svuotamento del registro. Segue le convenzioni dello
# schema (id seriale, creation_utc_date_time in UTC, creation_user_id), ma
# niente is_deleted: un registro si svuota, non si disattiva.
#
#   CREATE TABLE access_log (
#       id                     serial PRIMARY KEY,
#       creation_utc_date_time timestamp NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
#       creation_user_id       integer NOT NULL,
#       event_type             varchar(20) NOT NULL,
#       athlete_id             integer,
#       full_name              varchar(200),
#       fin_code               integer,
#       user_role              varchar(20),
#       via                    varchar(20),
#       note                   varchar(300)
#   );
#   CREATE INDEX ix_access_log_when ON access_log (creation_utc_date_time DESC);
#
# Nessuna foreign key su athlete_id: un log deve sopravvivere a tutto,
# anche a una riga di anagrafica che sparisce.

# %s: creation_user_id, event_type, athlete_id, full_name, fin_code,
#     user_role, via, note
ACCESS_LOG_INSERT_SQL = """
INSERT INTO access_log (creation_user_id, event_type, athlete_id, full_name,
                        fin_code, user_role, via, note)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

# Le date si girano in ora locale qui, cosi' la pagina non deve pensarci.
# %s: limite
ACCESS_LOG_SQL = """
SELECT
    id,
    (creation_utc_date_time AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Rome') AS quando,
    event_type, athlete_id, full_name, fin_code, user_role, via, note
FROM access_log
ORDER BY creation_utc_date_time DESC, id DESC
LIMIT %s
"""

ACCESS_LOG_STATS_SQL = """
SELECT
    count(*)                                                              AS righe,
    min(creation_utc_date_time AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Rome') AS dal,
    max(creation_utc_date_time AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Rome') AS al,
    count(*) FILTER (WHERE event_type = 'ACCESSO')                        AS accessi,
    count(*) FILTER (WHERE event_type = 'FALLITO')                        AS falliti
FROM access_log
"""

ACCESS_LOG_DELETE_SQL = "DELETE FROM access_log"


# ══════════════════════════════════════════════════════════════════
# Credenziali degli atleti (accesso con e-mail e password)
# ══════════════════════════════════════════════════════════════════

# L'e-mail resta una sola, quella di athletes: qui ci sono solo le
# credenziali, una riga per atleta.
#
#   CREATE TABLE athlete_credentials (
#       athlete_id                      integer PRIMARY KEY REFERENCES athletes(id),
#       creation_utc_date_time          timestamp NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
#       creation_user_id                integer NOT NULL,
#       last_modification_utc_date_time timestamp,
#       last_modification_user_id       integer,
#       password_hash                   varchar(300) NOT NULL,
#       must_change                     boolean NOT NULL DEFAULT false,
#       failed_attempts                 integer NOT NULL DEFAULT 0,
#       locked_until_utc                timestamp,
#       last_login_utc                  timestamp,
#       is_enabled                      boolean NOT NULL DEFAULT true
#   );
#   CREATE UNIQUE INDEX ux_athletes_email_attivi ON athletes (lower(btrim(email)))
#       WHERE is_deleted = FALSE AND email IS NOT NULL AND btrim(email) <> '';

# Login. %s: email normalizzata (minuscola, senza spazi)
LOGIN_BY_EMAIL_SQL = """
SELECT
    a.id                                            AS athlete_id,
    btrim(a.last_name) || ' ' || btrim(a.first_name) AS full_name,
    a.fin_code,
    btrim(a.email)                                  AS email,
    a.is_staff,
    a.is_athlete,
    c.password_hash,
    c.must_change,
    c.failed_attempts,
    c.is_enabled,
    (c.locked_until_utc > (now() AT TIME ZONE 'utc')) AS bloccato,
    (c.locked_until_utc AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Rome') AS bloccato_fino
FROM athletes a
LEFT JOIN athlete_credentials c ON c.athlete_id = a.id
WHERE a.is_deleted = FALSE
  AND lower(btrim(a.email)) = %s
LIMIT 1
"""

# Primo accesso: ci si riconosce con e-mail e data di nascita, che sono a
# database per tutti. Il codice FIN no, sette tesserati non ce l'hanno.
# %s: email normalizzata, data di nascita
ATHLETE_BY_EMAIL_BIRTH_SQL = """
SELECT a.id                                            AS athlete_id,
       btrim(a.last_name) || ' ' || btrim(a.first_name) AS full_name,
       a.fin_code,
       a.is_staff,
       (c.athlete_id IS NOT NULL)                      AS ha_password
FROM athletes a
LEFT JOIN athlete_credentials c ON c.athlete_id = a.id
WHERE a.is_deleted = FALSE
  AND lower(btrim(a.email)) = %s
  AND a.birth_date = %s
LIMIT 1
"""

# Crea o sostituisce la password. %s: athlete_id, user_id, hash, must_change,
#                                    user_id (per la modifica)
CREDENTIALS_UPSERT_SQL = """
INSERT INTO athlete_credentials (athlete_id, creation_user_id, password_hash,
                                 must_change, is_enabled)
VALUES (%s, %s, %s, %s, TRUE)
ON CONFLICT (athlete_id) DO UPDATE SET
    password_hash                   = EXCLUDED.password_hash,
    must_change                     = EXCLUDED.must_change,
    is_enabled                      = TRUE,
    failed_attempts                 = 0,
    locked_until_utc                = NULL,
    last_modification_utc_date_time = (now() AT TIME ZONE 'utc'),
    last_modification_user_id       = %s
"""

# %s: athlete_id
CREDENTIALS_OK_SQL = """
UPDATE athlete_credentials
   SET failed_attempts  = 0,
       locked_until_utc = NULL,
       last_login_utc   = (now() AT TIME ZONE 'utc')
 WHERE athlete_id = %s
"""

# Tentativo sbagliato: conta e, superata la soglia, blocca per qualche minuto.
# %s: soglia, minuti, athlete_id
CREDENTIALS_FAIL_SQL = """
UPDATE athlete_credentials
   SET failed_attempts  = failed_attempts + 1,
       locked_until_utc = CASE WHEN failed_attempts + 1 >= %s
                               THEN (now() AT TIME ZONE 'utc') + make_interval(mins => %s)
                               ELSE locked_until_utc END
 WHERE athlete_id = %s
RETURNING failed_attempts,
          (locked_until_utc AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Rome') AS bloccato_fino
"""

# %s: athlete_id
CREDENTIALS_DELETE_SQL = "DELETE FROM athlete_credentials WHERE athlete_id = %s"

# %s: is_enabled, user_id, athlete_id
CREDENTIALS_ENABLE_SQL = """
UPDATE athlete_credentials
   SET is_enabled                      = %s,
       failed_attempts                 = 0,
       locked_until_utc                = NULL,
       last_modification_utc_date_time = (now() AT TIME ZONE 'utc'),
       last_modification_user_id       = %s
 WHERE athlete_id = %s
"""

# Stato per l'anagrafica. %s: athlete_id
CREDENTIALS_STATE_SQL = """
SELECT c.athlete_id, c.must_change, c.failed_attempts, c.is_enabled,
       (c.locked_until_utc > (now() AT TIME ZONE 'utc'))                  AS bloccato,
       (c.locked_until_utc AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Rome') AS bloccato_fino,
       (c.last_login_utc   AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Rome') AS ultimo_accesso,
       (c.creation_utc_date_time AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Rome') AS creata_il
FROM athlete_credentials c
WHERE c.athlete_id = %s
"""

# Quante credenziali attive ci sono, per il riepilogo in Gestione.
CREDENTIALS_COUNT_SQL = """
SELECT count(*)                                  AS con_password,
       count(*) FILTER (WHERE is_enabled)        AS abilitate,
       count(*) FILTER (WHERE must_change)       AS da_cambiare
FROM athlete_credentials
"""


# ══════════════════════════════════════════════════════════════════
# Risultati di una manifestazione
# ══════════════════════════════════════════════════════════════════

# Tutte le nostre gare di una manifestazione, con gli iscritti e i tempi.
# Ci sono anche le staffette (una riga per frazionista, tutte con il tempo
# della squadra) e gli iscritti senza tempo, che in un elenco di gara sono
# un'informazione: squalificato, ritirato o non partito.
# L'ordine: prima le individuali, poi le staffette; dentro ogni gruppo per
# stile e distanza, e dentro la gara dal tempo migliore. La distanza va
# ordinata a numero, ma "4x50" non e' un numero: il CASE tiene separati i
# due casi, cosi' il cast non vede mai una stringa con la x.
# %s: comp_id
COMPETITION_RESULTS_SQL = """
SELECT
    s.name                                           AS stroke,
    d.type                                           AS distance,
    re.is_relay,
    CASE WHEN d.type ~ '^[0-9]+$' THEN (d.type)::int
         WHEN d.type ~ '^[0-9]+x[0-9]+$' THEN (split_part(d.type, 'x', 2))::int
         ELSE 999999 END                             AS dist_num,
    r.pool_length,
    a.id                                             AS athlete_id,
    btrim(a.last_name) || ' ' || btrim(a.first_name) AS full_name,
    CASE WHEN a.sex THEN 'M' ELSE 'F' END            AS sex,
    EXTRACT(YEAR FROM a.birth_date)::int             AS birth_year,
    EXTRACT(EPOCH FROM ar.final_time)::float         AS time_sec,
    ar.fin_score,
    co.start_date                                    AS comp_date
FROM athlete_races ar
JOIN races        r  ON r.id  = ar.race_id        AND r.is_deleted = FALSE
JOIN competitions co ON co.id = r.competition_id  AND co.is_deleted = FALSE
JOIN race_events  re ON re.id = r.race_event_id   AND re.is_deleted = FALSE
JOIN strokes      s  ON s.id  = re.stroke_id      AND s.is_deleted  = FALSE
JOIN distances    d  ON d.id  = re.distance_id    AND d.is_deleted  = FALSE
JOIN athletes     a  ON a.id  = ar.athlete_id
WHERE r.competition_id = %s
  AND ar.is_deleted   = FALSE
ORDER BY re.is_relay, s.name, dist_num, r.pool_length,
         EXTRACT(EPOCH FROM ar.final_time) NULLS LAST,
         btrim(a.last_name), btrim(a.first_name)
"""
