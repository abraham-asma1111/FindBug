-- Fix role capitalization inconsistency
-- Convert all uppercase role values to lowercase

BEGIN;

-- Show current state
SELECT 
    role,
    COUNT(*) as count
FROM users
GROUP BY role
ORDER BY role;

-- Update RESEARCHER to researcher
UPDATE users 
SET role = 'researcher'::userrole
WHERE role::text = 'RESEARCHER';

-- Update ORGANIZATION to organization  
UPDATE users
SET role = 'organization'::userrole
WHERE role::text = 'ORGANIZATION';

-- Show final state
SELECT 
    role,
    COUNT(*) as count
FROM users
GROUP BY role
ORDER BY role;

COMMIT;
