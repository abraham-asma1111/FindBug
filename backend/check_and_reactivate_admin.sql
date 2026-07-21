-- Check all admin users and their status
SELECT 
    id,
    email,
    role,
    is_active,
    created_at,
    last_login_at
FROM users
WHERE role = 'admin'
ORDER BY is_active DESC, created_at;

-- To reactivate a specific admin by email, uncomment and replace the email:
-- UPDATE users SET is_active = true WHERE email = 'your-admin@example.com' AND role = 'admin';

-- To reactivate ALL inactive admins:
-- UPDATE users SET is_active = true WHERE role = 'admin' AND is_active = false;
