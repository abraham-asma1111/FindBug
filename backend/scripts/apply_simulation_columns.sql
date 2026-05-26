-- Apply simulation gamification columns if Alembic cannot run (idempotent).
-- Run: psql $DATABASE_URL -f scripts/apply_simulation_columns.sql

ALTER TABLE simulation_reports ADD COLUMN IF NOT EXISTS score INTEGER DEFAULT 0;
ALTER TABLE simulation_reports ADD COLUMN IF NOT EXISTS remediation TEXT;

ALTER TABLE simulation_leaderboard ADD COLUMN IF NOT EXISTS rank_title VARCHAR(64) DEFAULT 'Newbie';
ALTER TABLE simulation_leaderboard ADD COLUMN IF NOT EXISTS current_streak INTEGER DEFAULT 0;

ALTER TABLE simulation_progress ADD COLUMN IF NOT EXISTS hints_unlocked JSONB DEFAULT '[]'::jsonb;
