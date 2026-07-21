-- Check admin user details
SELECT 
    id,
    email,
    role,
    is_active,
    password_hash IS NOT NULL as has_password,
    email_verified_at IS NOT NULL as email_verified,
    created_at
FROM users 
WHERE email = 'remainsecure@findbug.com';
