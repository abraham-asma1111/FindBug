-- Optional: align existing challenges with 2 free + 2 paid hints (re-run seed is preferred for full text).
-- Example for SQLi-style challenges: set index 0,1 free and 2,3 paid.

UPDATE simulation_challenges
SET hint_costs = '{"0": 0, "1": 0, "2": 10, "3": 15}'::jsonb
WHERE vulnerability_type = 'sql_injection';

UPDATE simulation_challenges
SET hint_costs = '{"0": 0, "1": 0, "2": 10, "3": 15}'::jsonb
WHERE vulnerability_type = 'xss';

UPDATE simulation_challenges
SET hint_costs = '{"0": 0, "1": 0, "2": 15, "3": 20}'::jsonb
WHERE vulnerability_type IN ('jwt_attack', 'ssrf');

UPDATE simulation_challenges
SET hint_costs = '{"0": 0, "1": 0, "2": 20, "3": 25}'::jsonb
WHERE vulnerability_type IN ('oauth_abuse', 'race_condition');
