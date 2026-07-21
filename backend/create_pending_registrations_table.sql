-- Create enum for registration type
DO $$ BEGIN
    CREATE TYPE registrationtype AS ENUM ('researcher', 'organization');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create pending_registrations table
CREATE TABLE IF NOT EXISTS pending_registrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Basic info
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    registration_type registrationtype NOT NULL,
    
    -- Personal info
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    
    -- Organization-specific fields (nullable for researchers)
    company_name VARCHAR(200),
    phone_number VARCHAR(20),
    country VARCHAR(100),
    
    -- Verification
    verification_token VARCHAR(255) NOT NULL,
    verification_otp VARCHAR(10),
    otp_expires_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    verified_at TIMESTAMP,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Request info
    ip_address VARCHAR(45),
    user_agent TEXT
);

-- Create indexes
CREATE INDEX IF NOT EXISTS ix_pending_registrations_email ON pending_registrations(email);
CREATE INDEX IF NOT EXISTS ix_pending_registrations_verification_token ON pending_registrations(verification_token);
CREATE INDEX IF NOT EXISTS ix_pending_registrations_expires_at ON pending_registrations(expires_at);
CREATE INDEX IF NOT EXISTS ix_pending_registrations_created_at ON pending_registrations(created_at);

SELECT 'pending_registrations table created successfully' AS result;
