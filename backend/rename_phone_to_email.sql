-- Rename phone columns to email columns in kyc_verifications table

-- 1. Rename phone_number to email_address and increase length
ALTER TABLE kyc_verifications 
  ALTER COLUMN phone_number TYPE VARCHAR(255);

ALTER TABLE kyc_verifications 
  RENAME COLUMN phone_number TO email_address;

-- 2. Rename phone_verified to email_verified
ALTER TABLE kyc_verifications 
  RENAME COLUMN phone_verified TO email_verified;

-- 3. Rename phone_verification_code to email_verification_code and increase length
ALTER TABLE kyc_verifications 
  ALTER COLUMN phone_verification_code TYPE VARCHAR(255);

ALTER TABLE kyc_verifications 
  RENAME COLUMN phone_verification_code TO email_verification_code;

-- 4. Rename phone_verification_code_expires to email_verification_code_expires
ALTER TABLE kyc_verifications 
  RENAME COLUMN phone_verification_code_expires TO email_verification_code_expires;

-- 5. Rename phone_verification_attempts to email_verification_attempts
ALTER TABLE kyc_verifications 
  RENAME COLUMN phone_verification_attempts TO email_verification_attempts;

-- 6. Rename phone_verified_at to email_verified_at
ALTER TABLE kyc_verifications 
  RENAME COLUMN phone_verified_at TO email_verified_at;
