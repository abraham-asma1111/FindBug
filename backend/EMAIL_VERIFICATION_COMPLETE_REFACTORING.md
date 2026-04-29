# Email Verification Complete Refactoring

## Database Changes ✅ COMPLETE

All columns renamed from `phone_*` to `email_*`:
- `phone_number` → `email_address` (VARCHAR(255))
- `phone_verified` → `email_verified`
- `phone_verification_code` → `email_verification_code` (VARCHAR(255))
- `phone_verification_code_expires` → `email_verification_code_expires`
- `phone_verification_attempts` → `email_verification_attempts`
- `phone_verified_at` → `email_verified_at`

## Backend Updates Required

### 1. Model (backend/src/domain/models/kyc.py) ✅ DONE
- Updated all field names to use `email_*` prefix

### 2. Service (backend/src/services/kyc_service.py)
- Rename `send_phone_verification()` → `send_email_verification()`
- Rename `verify_phone_code()` → `verify_email_code()`
- Rename `get_phone_verification_status()` → `get_email_verification_status()`
- Update all internal references to use `email_*` fields

### 3. API Endpoints (backend/src/api/v1/endpoints/kyc.py)
- Rename `/kyc/phone/send` → `/kyc/email/send`
- Rename `/kyc/phone/verify` → `/kyc/email/verify`
- Rename `/kyc/phone/status` → `/kyc/email/status`
- Update all function names and references

## Frontend Updates Required

### 1. EmailVerification Component
- Update API calls to use `/kyc/email/*` endpoints
- Update state variable names from `phoneNumber` to `emailAddress`

### 2. TwoStepKYCVerification Component
- Update API calls
- Update prop names

### 3. CompleteVerification Component (if still used)
- Update all phone references to email

## Testing
- Test email sending
- Test code verification
- Test rate limiting
- Test expiration
