-- Keep one published challenge per vulnerability_type (newest wins).
-- Run: psql "$DATABASE_URL" -f backend/scripts/dedupe_simulation_challenges.sql

WITH ranked AS (
  SELECT
    id,
    vulnerability_type,
    ROW_NUMBER() OVER (
      PARTITION BY LOWER(TRIM(vulnerability_type))
      ORDER BY created_at DESC NULLS LAST, id DESC
    ) AS rn
  FROM simulation_challenges
  WHERE is_published IS TRUE
    AND (is_active IS TRUE OR is_active IS NULL)
),
keepers AS (SELECT id FROM ranked WHERE rn = 1)
UPDATE simulation_challenges c
SET is_active = FALSE, is_published = FALSE
WHERE c.is_published IS TRUE
  AND c.id NOT IN (SELECT id FROM keepers);
