-- Fix reputation scores for all researchers based on their reports
-- Run this with: psql -U postgres -d bug_bounty_production -f fix_reputation_scores.sql

-- First, reset all reputation scores to 0
UPDATE researchers SET reputation_score = 0;

-- Update reputation for researchers with VALID reports
-- Critical: +50, High: +30, Medium: +20, Low: +10
UPDATE researchers r
SET reputation_score = reputation_score + COALESCE(
    (SELECT 
        SUM(CASE 
            WHEN vr.assigned_severity = 'critical' THEN 50
            WHEN vr.assigned_severity = 'high' THEN 30
            WHEN vr.assigned_severity = 'medium' THEN 20
            WHEN vr.assigned_severity = 'low' THEN 10
            ELSE 0
        END)
    FROM vulnerability_reports vr
    WHERE vr.researcher_id = r.id
    AND vr.status IN ('valid', 'resolved')
    AND vr.assigned_severity IS NOT NULL
    ), 0
);

-- Update reputation for ORIGINAL reports that others duplicated (they get 100% even if marked as duplicate)
-- If report was submitted FIRST and has assigned_severity, they are the original and get full points
UPDATE researchers r
SET reputation_score = reputation_score + COALESCE(
    (SELECT 
        SUM(CASE 
            WHEN vr.assigned_severity = 'critical' THEN 50
            WHEN vr.assigned_severity = 'high' THEN 30
            WHEN vr.assigned_severity = 'medium' THEN 20
            WHEN vr.assigned_severity = 'low' THEN 10
            ELSE 0
        END)
    FROM vulnerability_reports vr
    LEFT JOIN vulnerability_reports orig ON vr.duplicate_of = orig.id
    WHERE vr.researcher_id = r.id
    AND vr.status = 'duplicate'
    AND vr.assigned_severity IS NOT NULL
    -- They are the original if they submitted before the "original" or if no duplicate_of link
    AND (orig.id IS NULL OR vr.submitted_at < orig.submitted_at)
    ), 0
);

-- Update reputation for researchers with DUPLICATE reports within 24h (submitted AFTER original)
-- They get 25% of the original severity points
UPDATE researchers r
SET reputation_score = reputation_score + COALESCE(
    (SELECT 
        SUM(CASE 
            WHEN orig.assigned_severity = 'critical' THEN 12.5  -- 25% of 50
            WHEN orig.assigned_severity = 'high' THEN 7.5       -- 25% of 30
            WHEN orig.assigned_severity = 'medium' THEN 5       -- 25% of 20
            WHEN orig.assigned_severity = 'low' THEN 2.5        -- 25% of 10
            ELSE 0
        END)
    FROM vulnerability_reports vr
    JOIN vulnerability_reports orig ON vr.duplicate_of = orig.id
    WHERE vr.researcher_id = r.id
    AND vr.status = 'duplicate'
    AND vr.submitted_at > orig.submitted_at  -- They submitted AFTER the original
    AND (EXTRACT(EPOCH FROM (vr.submitted_at - orig.submitted_at)) <= 86400)  -- within 24 hours
    AND orig.assigned_severity IS NOT NULL
    ), 0
);

-- Invalid reports: 0 points (no change)
-- Duplicate reports after 24h: 0 points (no change)

-- Update rankings based on reputation scores
WITH ranked_researchers AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (ORDER BY reputation_score DESC, id) as new_rank
    FROM researchers
)
UPDATE researchers r
SET rank = rr.new_rank
FROM ranked_researchers rr
WHERE r.id = rr.id;

-- Show results
SELECT 
    r.username,
    u.email,
    r.reputation_score,
    r.rank,
    COUNT(vr.id) as total_reports,
    COUNT(CASE WHEN vr.status IN ('valid', 'resolved') THEN 1 END) as valid_reports,
    COUNT(CASE WHEN vr.status = 'invalid' THEN 1 END) as invalid_reports,
    COUNT(CASE WHEN vr.status = 'duplicate' THEN 1 END) as duplicate_reports
FROM researchers r
JOIN users u ON r.user_id = u.id
LEFT JOIN vulnerability_reports vr ON vr.researcher_id = r.id
GROUP BY r.id, r.username, u.email, r.reputation_score, r.rank
ORDER BY r.reputation_score DESC;
