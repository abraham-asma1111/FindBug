-- Fix userrole enum to accept both uppercase and lowercase values
-- This permanently fixes the "invalid input value for enum userrole: 'researcher'" error

-- Add lowercase values to the enum
ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'researcher';
ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'organization';
ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'staff';
ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'admin';
ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'super_admin';
ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'triage_specialist';
ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'finance_officer';
