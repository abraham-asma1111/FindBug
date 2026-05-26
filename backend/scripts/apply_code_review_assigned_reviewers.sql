-- Run if Alembic migration is not applied yet
ALTER TABLE code_review_engagements
  ADD COLUMN IF NOT EXISTS assigned_reviewer_ids JSON;

UPDATE code_review_engagements
SET assigned_reviewer_ids = json_build_array(reviewer_id::text)
WHERE reviewer_id IS NOT NULL
  AND (assigned_reviewer_ids IS NULL OR assigned_reviewer_ids::text = 'null');
