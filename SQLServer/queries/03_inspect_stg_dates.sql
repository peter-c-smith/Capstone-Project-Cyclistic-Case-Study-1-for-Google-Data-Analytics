-- ============================================================
-- 03_inspect_stg_dates.sql
-- Inspects raw date values in stg.Trips to diagnose why
-- TRY_CAST to DATETIME2 is returning NULL for all rows.
-- ============================================================

USE CyclisticCaseStudy;
GO

SELECT TOP 10
    started_at,
    ended_at,
    LEN(started_at)                             AS started_at_len,
    ASCII(LEFT(started_at, 1))                  AS first_char_ascii,
    TRY_CAST(started_at AS DATETIME2)           AS started_at_cast,
    TRY_CAST(LTRIM(RTRIM(started_at))
             AS DATETIME2)                      AS started_at_trimmed_cast
FROM stg.Trips;
GO
