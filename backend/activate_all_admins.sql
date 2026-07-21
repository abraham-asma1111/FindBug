-- Activate all admin and super_admin users
-- This script sets is_active = true for all users with admin or super_admin role

-- First, check current admin status
SELECT 
    id,
    email,
    role,
    is_active,
    created_at
FROM users
WHERE role IN ('admin', 'super_admin')
ORDER BY role, email;

-- Activate all admin and super_admin users
UPDATE users 
SET is_active = true 
WHERE role IN ('admin', 'super_admin') 
  AND is_active = false;

-- Verify the update
SELECT 
    id,
    email,
    role,
    is_active,
    created_at
FROM users
WHERE role IN ('admin', 'super_admin')
ORDER BY role, email;

-- Show summary
SELECT 
    role,
    COUNT(*) as total_count,
    SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active_count,
    SUM(CASE WHEN NOT is_active THEN 1 ELSE 0 END) as inactive_count
FROM users
WHERE role IN ('admin', 'super_admin')
GROUP BY role;
