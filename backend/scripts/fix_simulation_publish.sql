-- Fix challenges not showing in catalog (is_active was NULL).
UPDATE simulation_challenges
SET is_active = true, is_published = true
WHERE is_active IS NULL OR is_published IS NULL;
