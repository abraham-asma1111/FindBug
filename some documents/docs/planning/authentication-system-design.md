# Authentication & Authorization System Design
## Bug Bounty and Its Simulation Platform

---

## Overview

The platform implements a **unified authentication system** with **role-based access control (RBAC)** supporting multiple user types through a single login endpoint. Staff accounts are provisioned internally by administrators, not through public registration.

---

## Architecture Approach

### ✅ Chosen: Unified Login with Role-Based Routing

```
Single Login URL: https://platform.com/login
                        ↓
              JWT Token with Role Claims
                        ↓
                  Role Detection
                        ↓
        ┌───────────┬──────────┬─────────┬──────────┐
        ↓           ↓          ↓         ↓          ↓
   Researcher   Organization  Admin   Triage   Learning
   Dashboard     Dashboard   Panel   Dashboard Platform
```

### Key Benefits:
- Single authentication service
- Simplified session management
- Consistent security policies
- Easy SSO integration
- Unified audit logging

---

## User Roles & Access Levels

### 1. Public Users (Self-Registration)
- **RESEARCHER** - Security researchers, bug hunters
- **ORGANIZATION_MEMBER** - Company employees (invited by org owner)

### 2. Platform Staff (Internal Provisioning Only)
- **SUPER_ADMIN** - Full platform control, staff management
- **ADMIN** - User moderation, program oversight
- **TRIAGE_SPECIALIST** - Report validation, severity assignment
- **FINANCIAL_OFFICER** - Payment approvals, financial operations
- **SUPPORT_STAFF** - User support, documentation

### 3. Learning Platform Users
- Same users as above, different dashboard
- SSO authentication with main platform
- Role-based course access

---

## Staff Provisioning Process

### Method: Internal Employee Provisioning (Option 3)

#### Step 1: Super Admin Creates Staff Account
```
Super Admin → Admin Panel → Staff Management → "Add New Staff"

Form Fields:
- Email Address (required, unique)
- Full Name (required)
- Role (dropdown: Admin, Triage, Finance, Support)
- Department (optional)
- Access Level (Standard, Senior)
- Permissions (checkboxes for granular control)
```

#### Step 2: System Generates Invitation
```sql
-- Create user record
INSERT INTO users (
    user_id,
    email,
    full_name,
    role,
    is_staff,
    status,
    created_at
) VALUES (
    uuid_generate_v4(),
    '[email protected]',
    'John Doe',
    'TRIAGE_SPECIALIST',
    true,
    'PENDING',
    NOW()
);

-- Generate invitation token
INSERT INTO staff_invitations (
    invitation_id,
    user_id,
    invitation_token,
    expires_at,
    created_by,
    status
) VALUES (
    uuid_generate_v4(),
    <user_id>,
    encode(gen_random_bytes(32), 'hex'),
    NOW() + INTERVAL '48 hours',
    <super_admin_id>,
    'PENDING'
);
```

#### Step 3: Email Sent to Staff Member
```
Subject: Welcome to [Platform Name] Staff Team

Hi John,

You've been invited to join the [Platform Name] staff team as a Triage Specialist.

Your Role: Triage Specialist
Department: Security Operations
Access Level: Standard

To activate your account:
1. Click the link below (valid for 48 hours)
2. Set your secure password
3. Complete your profile

Activation Link: https://platform.com/staff/activate?token=<invitation_token>

Need help? Contact: [email protected]

Best regards,
Platform Team
```

#### Step 4: Staff Member Activates Account
```
1. Click invitation link
2. System verifies token (not expired, not used)
3. Display password setup form
4. Staff enters new password (must meet policy)
5. System validates password strength
6. Password hashed with bcrypt
7. Account status changed to ACTIVE
8. Invitation token deleted
9. JWT token generated
10. Redirect to role-specific dashboard
```

---

## Authentication Flows

### 1. Staff Login (Standard)

```
POST /api/auth/login
Content-Type: application/json

{
  "email": "[email protected]",
  "password": "SecurePassword123!",
  "remember_me": false
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "user_id": "uuid",
    "email": "[email protected]",
    "full_name": "John Doe",
    "role": "TRIAGE_SPECIALIST",
    "is_staff": true,
    "permissions": ["validate_reports", "assign_severity", "add_comments"]
  }
}
```

### 2. Staff Login with MFA

```
Step 1: Submit credentials
POST /api/auth/login
{
  "email": "[email protected]",
  "password": "SecurePassword123!"
}

Response (200 OK):
{
  "mfa_required": true,
  "mfa_token": "temp_token_for_mfa",
  "mfa_methods": ["totp", "sms"]
}

Step 2: Submit MFA code
POST /api/auth/mfa/verify
{
  "mfa_token": "temp_token_for_mfa",
  "mfa_code": "123456",
  "method": "totp"
}

Response (200 OK):
{
  "access_token": "...",
  "refresh_token": "...",
  ...
}
```

### 3. SSO Login (Optional for Organizations)

```
Step 1: Initiate SSO
GET /api/auth/sso/initiate?provider=okta

Response: Redirect to Identity Provider

Step 2: User authenticates with IDP
(Handled by Okta/Azure AD/Google)

Step 3: SAML Response
POST /api/auth/sso/callback
(SAML assertion with user attributes)

Step 4: System validates and creates session
- Verify SAML signature
- Extract user email
- Lookup user in database (must have is_staff=true)
- Generate JWT token
- Redirect to dashboard
```

---

## JWT Token Structure

### Access Token Claims
```json
{
  "sub": "user_id",
  "email": "[email protected]",
  "role": "TRIAGE_SPECIALIST",
  "is_staff": true,
  "permissions": [
    "validate_reports",
    "assign_severity",
    "add_comments",
    "view_analytics"
  ],
  "iat": 1678901234,
  "exp": 1678904834,
  "iss": "platform.com",
  "aud": "platform-api"
}
```

### Token Validation on Every Request
```
1. Extract token from Authorization header
2. Verify signature (HMAC-SHA256 or RSA)
3. Check expiration (exp claim)
4. Check issuer (iss claim)
5. Check audience (aud claim)
6. Check if token is blacklisted (Redis)
7. Extract user context (role, permissions)
8. Proceed with request
```

---

## Permission System

### Granular Permissions

```python
# Permission format: <action>_<resource>

PERMISSIONS = {
    "SUPER_ADMIN": ["*"],  # All permissions
    
    "ADMIN": [
        "view_users",
        "suspend_users",
        "view_programs",
        "moderate_programs",
        "view_reports",
        "view_analytics",
        "manage_staff",  # Can manage non-super-admin staff
    ],
    
    "TRIAGE_SPECIALIST": [
        "view_reports",
        "validate_reports",
        "assign_severity",
        "add_comments",
        "mark_duplicate",
        "request_info",
    ],
    
    "FINANCIAL_OFFICER": [
        "view_payments",
        "approve_payments",
        "process_payouts",
        "view_financials",
        "generate_reports",
    ],
    
    "SUPPORT_STAFF": [
        "view_tickets",
        "respond_tickets",
        "view_users",
        "view_programs",
        "view_documentation",
    ],
}
```

### Permission Check Middleware

```python
@require_permission("validate_reports")
async def validate_report(report_id: UUID, user: User):
    # Permission already checked by decorator
    # Proceed with validation logic
    pass
```

---

## Database Schema

### users table
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(60) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN (
        'SUPER_ADMIN', 'ADMIN', 'TRIAGE_SPECIALIST', 
        'FINANCIAL_OFFICER', 'SUPPORT_STAFF', 
        'RESEARCHER', 'ORGANIZATION_MEMBER'
    )),
    is_staff BOOLEAN DEFAULT false,
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN (
        'PENDING', 'ACTIVE', 'SUSPENDED', 'BANNED', 'REMOVED'
    )),
    email_verified BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_staff ON users(is_staff);
```

### staff_invitations table
```sql
CREATE TABLE staff_invitations (
    invitation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id),
    created_by UUID NOT NULL REFERENCES users(user_id),
    invitation_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN (
        'PENDING', 'ACCEPTED', 'EXPIRED', 'REVOKED'
    )),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_invitations_token ON staff_invitations(invitation_token);
CREATE INDEX idx_invitations_user ON staff_invitations(user_id);
```

### staff_permissions table
```sql
CREATE TABLE staff_permissions (
    permission_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id),
    permission_name VARCHAR(100) NOT NULL,
    resource VARCHAR(100),
    granted_by UUID NOT NULL REFERENCES users(user_id),
    granted_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_permissions_user ON staff_permissions(user_id);
```

### admin_sessions table
```sql
CREATE TABLE admin_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id),
    jwt_token_hash VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sessions_user ON admin_sessions(user_id);
CREATE INDEX idx_sessions_token ON admin_sessions(jwt_token_hash);
```

---

## Security Measures

### 1. Password Policy
- Minimum 12 characters
- Must contain: uppercase, lowercase, number, symbol
- Cannot be in common password list (10k most common)
- Cannot contain user's name or email
- Must be changed every 90 days (for staff)

### 2. Multi-Factor Authentication
- Required for all staff accounts
- Optional for researchers (encouraged)
- Supported methods: TOTP (Google Authenticator), SMS
- Backup codes provided (10 single-use codes)

### 3. Session Management
- Access token: 1 hour expiration
- Refresh token: 7 days expiration
- Tokens stored in httpOnly cookies (web) or secure storage (mobile)
- Token blacklist in Redis for logout
- Concurrent session limit: 3 per user

### 4. Rate Limiting
- Login attempts: 5 per 15 minutes per IP
- API requests: 100 per minute per user
- Staff API: 1000 per minute per user

### 5. Audit Logging
- All staff actions logged
- Login/logout events
- Permission changes
- User modifications
- Financial operations
- Retention: 7 years

---

## Dashboard Routing

### After Successful Authentication

```javascript
// Frontend routing logic
function routeToDashboard(user) {
    if (user.is_staff) {
        switch (user.role) {
            case 'SUPER_ADMIN':
            case 'ADMIN':
                return '/admin/dashboard';
            case 'TRIAGE_SPECIALIST':
                return '/triage/dashboard';
            case 'FINANCIAL_OFFICER':
                return '/finance/dashboard';
            case 'SUPPORT_STAFF':
                return '/support/dashboard';
        }
    } else {
        switch (user.role) {
            case 'RESEARCHER':
                return '/researcher/dashboard';
            case 'ORGANIZATION_MEMBER':
                return '/organization/dashboard';
        }
    }
}
```

### Learning Platform SSO

```
User logged in to main platform
    ↓
Click "Go to Learning Platform"
    ↓
System generates SSO token (short-lived, 5 min)
    ↓
Redirect to: https://learn.platform.com/sso?token=<sso_token>
    ↓
Learning platform validates token
    ↓
Creates session for learning platform
    ↓
Redirect to learning dashboard
```

---

## Implementation Checklist

### Phase 1: Core Authentication
- [ ] User model with role and is_staff fields
- [ ] Password hashing (bcrypt)
- [ ] JWT token generation and validation
- [ ] Login/logout endpoints
- [ ] Session management

### Phase 2: Staff Provisioning
- [ ] Staff invitation system
- [ ] Email templates
- [ ] Account activation flow
- [ ] Permission management
- [ ] Admin panel UI

### Phase 3: Security Features
- [ ] MFA implementation (TOTP)
- [ ] Rate limiting
- [ ] Token blacklist (Redis)
- [ ] Audit logging
- [ ] Password policy enforcement

### Phase 4: Advanced Features
- [ ] SSO integration (SAML/OAuth)
- [ ] Learning platform SSO
- [ ] Concurrent session management
- [ ] IP whitelisting for staff
- [ ] Security alerts

---

## API Endpoints

### Authentication
```
POST   /api/auth/login                 # Login
POST   /api/auth/logout                # Logout
POST   /api/auth/refresh               # Refresh token
POST   /api/auth/forgot-password       # Request password reset
POST   /api/auth/reset-password        # Reset password
GET    /api/auth/me                    # Get current user
```

### Staff Management (Super Admin Only)
```
POST   /api/admin/staff                # Create staff account
GET    /api/admin/staff                # List all staff
GET    /api/admin/staff/:id            # Get staff details
PATCH  /api/admin/staff/:id            # Update staff
DELETE /api/admin/staff/:id            # Remove staff
POST   /api/admin/staff/:id/suspend    # Suspend staff
POST   /api/admin/staff/:id/reactivate # Reactivate staff
```

### Staff Activation
```
GET    /api/staff/activate/:token      # Verify invitation token
POST   /api/staff/activate             # Activate account with password
```

### MFA
```
POST   /api/auth/mfa/setup             # Setup MFA
POST   /api/auth/mfa/verify            # Verify MFA code
POST   /api/auth/mfa/disable           # Disable MFA
GET    /api/auth/mfa/backup-codes      # Get backup codes
```

---

## Conclusion

This authentication system provides:
- ✅ Secure internal staff provisioning
- ✅ Unified login for all user types
- ✅ Role-based access control
- ✅ Granular permissions
- ✅ MFA support
- ✅ SSO integration ready
- ✅ Comprehensive audit logging
- ✅ Learning platform SSO

The system is production-ready, scalable, and follows industry best practices used by HackerOne, Bugcrowd, and YesWeHack.
