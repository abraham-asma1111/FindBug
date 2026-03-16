# OWASP Top 10 Implementation Guide

**Date**: March 15, 2026  
**Status**: Security controls implemented in code

---

## ✅ OWASP Top 10 2021 - Implementation Status

### A01:2021 - Broken Access Control ✅

**Implementation**: `backend/src/core/security.py` - `RBACPermission` class

**Controls**:
- ✅ Role-Based Access Control (RBAC)
- ✅ Permission matrix for all roles
- ✅ `@require_permission` decorator for endpoints
- ✅ Ownership validation (IDOR prevention)
- ✅ Program access validation (public/private)

**Usage Example**:
```python
from core.security import require_permission, RBACPermission

@router.post("/reports")
@require_permission("submit_reports")
async def submit_report(current_user: User):
    # Only users with "submit_reports" permission can access
    pass
```

**Business Logic Protection**:
```python
# Validate report ownership before access
if not BusinessLogicSecurity.validate_report_ownership(
    report.user_id, current_user.id, current_user.role
):
    raise HTTPException(status_code=403, detail="Access denied")
```

---

### A02:2021 - Cryptographic Failures ✅

**Implementation**: `PasswordSecurity` and `TokenSecurity` classes

**Controls**:
- ✅ Bcrypt password hashing (cost factor 12)
- ✅ Strong password requirements (8+ chars, mixed case, digits, special)
- ✅ JWT with expiration and unique JTI
- ✅ Secure token generation (`secrets` module)
- ✅ HMAC for token verification

**Usage Example**:
```python
from core.security import PasswordSecurity, TokenSecurity

# Hash password
hashed = PasswordSecurity.hash_password(plain_password)

# Validate password strength
is_valid, error = PasswordSecurity.validate_password_strength(password)
if not is_valid:
    raise ValueError(error)

# Create JWT token
token = TokenSecurity.create_access_token({"sub": user.email, "role": user.role})
```

---

### A03:2021 - Injection ✅

**Implementation**: `InputSanitization` class

**Controls**:
- ✅ HTML sanitization (XSS prevention)
- ✅ Email validation
- ✅ Filename sanitization (path traversal prevention)
- ✅ URL validation (SSRF prevention)
- ✅ SQLAlchemy ORM (SQL injection prevention)
- ✅ Pydantic validation (input validation)

**Usage Example**:
```python
from core.security import InputSanitization

# Sanitize HTML input
safe_html = InputSanitization.sanitize_html(user_input)

# Validate email
if not InputSanitization.validate_email(email):
    raise ValueError("Invalid email format")

# Sanitize filename
safe_filename = InputSanitization.sanitize_filename(uploaded_file.filename)

# Validate URL
if not InputSanitization.validate_url(webhook_url):
    raise ValueError("Invalid or unsafe URL")
```

**SQL Injection Prevention**:
```python
# ✅ GOOD: Using SQLAlchemy ORM
user = db.query(User).filter(User.email == email).first()

# ❌ BAD: Raw SQL with string formatting
# user = db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

---

### A04:2021 - Insecure Design ✅

**Implementation**: `BusinessLogicSecurity` class

**Controls**:
- ✅ Bounty amount validation (min/max, precision)
- ✅ Report ownership validation (IDOR prevention)
- ✅ Program access control (public/private)
- ✅ Commission calculation validation (30%)
- ✅ State transition validation

**Usage Example**:
```python
from core.security import BusinessLogicSecurity

# Validate bounty amount
is_valid, error = BusinessLogicSecurity.validate_bounty_amount(
    amount=1500.00,
    min_amount=50.00,
    max_amount=10000.00
)
if not is_valid:
    raise ValueError(error)

# Validate report access
if not BusinessLogicSecurity.validate_report_ownership(
    report.user_id, current_user.id, current_user.role
):
    raise HTTPException(status_code=403)
```

**Business Logic Flaws to Prevent**:
1. ❌ Negative bounty amounts
2. ❌ Unrealistic bounty amounts (> $100k)
3. ❌ Accessing other users' reports
4. ❌ Bypassing program visibility
5. ❌ Double payment
6. ❌ Commission manipulation

---

### A05:2021 - Security Misconfiguration ✅

**Implementation**: `SecurityHeaders` class

**Controls**:
- ✅ Security headers (X-Frame-Options, CSP, etc.)
- ✅ HTTPS enforcement (HSTS)
- ✅ Secure cookie settings
- ✅ CORS configuration
- ✅ Error handling (no stack traces in production)

**Usage Example**:
```python
from core.security import SecurityHeaders

# Add security headers to response
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    headers = SecurityHeaders.get_security_headers()
    for key, value in headers.items():
        response.headers[key] = value
    return response
```

**Configuration Checklist**:
- [ ] DEBUG=False in production
- [ ] Remove default credentials
- [ ] Disable directory listing
- [ ] Remove unnecessary features
- [ ] Update dependencies regularly
- [ ] Secure error messages

---

### A06:2021 - Vulnerable and Outdated Components ✅

**Controls**:
- ✅ Pin dependency versions in requirements.txt
- ✅ Regular dependency updates
- ✅ Automated vulnerability scanning (Dependabot)

**Maintenance**:
```bash
# Check for vulnerabilities
pip install safety
safety check

# Update dependencies
pip list --outdated
pip install --upgrade package-name
```

---

### A07:2021 - Identification and Authentication Failures ✅

**Implementation**: `AuthenticationSecurity` class

**Controls**:
- ✅ Strong password requirements
- ✅ Account lockout (5 failed attempts, 30 min lockout)
- ✅ Session timeout (30 minutes idle, 8 hours absolute)
- ✅ Secure token generation
- ✅ MFA support (TOTP)
- ✅ Password reset with secure tokens

**Usage Example**:
```python
from core.security import AuthenticationSecurity

# Generate secure token for password reset
reset_token = AuthenticationSecurity.generate_secure_token(32)
token_hash = AuthenticationSecurity.hash_token(reset_token)

# Store token_hash in database, send reset_token to user

# Verify token
if AuthenticationSecurity.verify_token_hash(provided_token, stored_hash):
    # Allow password reset
    pass
```

**Account Lockout Logic**:
```python
# Track failed login attempts
if failed_attempts >= AuthenticationSecurity.MAX_LOGIN_ATTEMPTS:
    user.locked_until = datetime.utcnow() + timedelta(
        minutes=AuthenticationSecurity.LOCKOUT_DURATION_MINUTES
    )
    db.commit()
    raise HTTPException(status_code=429, detail="Account locked")
```

---

### A08:2021 - Software and Data Integrity Failures ✅

**Implementation**: `DataIntegrity` class

**Controls**:
- ✅ File checksum validation (SHA-256)
- ✅ Signed JWTs
- ✅ Database constraints
- ✅ Audit logging

**Usage Example**:
```python
from core.security import DataIntegrity

# Calculate checksum for uploaded file
checksum = DataIntegrity.calculate_checksum(file_content)

# Store checksum with file metadata
file_record.checksum = checksum
db.commit()

# Verify file integrity later
if not DataIntegrity.verify_checksum(file_content, file_record.checksum):
    raise ValueError("File integrity check failed")
```

---

### A09:2021 - Security Logging and Monitoring Failures ✅

**Implementation**: `SecurityAudit` class

**Controls**:
- ✅ Security event logging
- ✅ Failed login tracking
- ✅ Permission denial logging
- ✅ Data access logging
- ✅ Admin action logging

**Usage Example**:
```python
from core.security import SecurityAudit

# Log security event
SecurityAudit.log_security_event(
    event_type="LOGIN_SUCCESS",
    user_id=user.id,
    details={"email": user.email},
    request=request
)

# Log suspicious activity
SecurityAudit.log_security_event(
    event_type="SUSPICIOUS_ACTIVITY",
    user_id=user.id,
    details={"action": "multiple_failed_logins", "count": 5},
    request=request
)
```

**Events to Log**:
- ✅ Authentication (login, logout, failures)
- ✅ Authorization (permission denied)
- ✅ Data access (sensitive data viewed)
- ✅ Data modification (create, update, delete)
- ✅ Admin actions
- ✅ Security events (account locked, password reset)

---

### A10:2021 - Server-Side Request Forgery (SSRF) ✅

**Implementation**: `SSRFProtection` class

**Controls**:
- ✅ URL validation
- ✅ Blocked internal IPs (localhost, 127.0.0.1, 169.254.169.254)
- ✅ Blocked private networks (10.x, 172.16.x, 192.168.x)
- ✅ Whitelist approach for external requests

**Usage Example**:
```python
from core.security import SSRFProtection

# Validate URL before making request
if not SSRFProtection.is_safe_url(webhook_url):
    raise ValueError("Unsafe URL detected")

# Make external request
response = httpx.get(webhook_url, timeout=5)
```

---

## 🛡️ Additional Security Controls

### Rate Limiting ✅

**Implementation**: `RateLimiter` class

```python
from core.security import RateLimiter

# Check rate limit
is_allowed, remaining = RateLimiter.check_rate_limit(
    identifier=f"login:{request.client.host}",
    max_requests=5,
    window_seconds=300  # 5 minutes
)

if not is_allowed:
    raise HTTPException(status_code=429, detail="Too many requests")
```

### File Upload Security ✅

**Implementation**: `FileUploadSecurity` class

```python
from core.security import FileUploadSecurity

# Validate file
if not FileUploadSecurity.validate_file_extension(filename, ['image', 'document']):
    raise ValueError("File type not allowed")

if not FileUploadSecurity.validate_file_size(file.size):
    raise ValueError("File too large")

if not FileUploadSecurity.scan_file_content(file_content):
    raise ValueError("Suspicious file content detected")

# Sanitize filename
safe_filename = InputSanitization.sanitize_filename(filename)
```

---

## 📋 Security Testing Checklist

### Authentication Testing
- [ ] Test password strength validation
- [ ] Test account lockout after failed attempts
- [ ] Test session timeout
- [ ] Test JWT expiration
- [ ] Test MFA bypass attempts
- [ ] Test password reset flow

### Authorization Testing
- [ ] Test RBAC permissions for each role
- [ ] Test horizontal privilege escalation (IDOR)
- [ ] Test vertical privilege escalation
- [ ] Test accessing other users' data
- [ ] Test bypassing program visibility

### Input Validation Testing
- [ ] Test SQL injection (should be prevented by ORM)
- [ ] Test XSS (should be sanitized)
- [ ] Test path traversal in file uploads
- [ ] Test SSRF in webhook URLs
- [ ] Test command injection

### Business Logic Testing
- [ ] Test negative bounty amounts
- [ ] Test unrealistic bounty amounts
- [ ] Test double payment
- [ ] Test commission manipulation
- [ ] Test state transition bypasses

### Rate Limiting Testing
- [ ] Test login rate limiting
- [ ] Test API rate limiting
- [ ] Test file upload rate limiting

---

## 🚀 Implementation Workflow

### For Each Endpoint:

1. **Input Validation**
   ```python
   # Validate and sanitize all inputs
   email = InputSanitization.sanitize_html(data.email)
   if not InputSanitization.validate_email(email):
       raise ValueError("Invalid email")
   ```

2. **Authentication**
   ```python
   # Verify JWT token
   payload = TokenSecurity.verify_token(token)
   if not payload:
       raise HTTPException(status_code=401)
   ```

3. **Authorization**
   ```python
   # Check permissions
   @require_permission("submit_reports")
   async def submit_report(current_user: User):
       pass
   ```

4. **Business Logic Validation**
   ```python
   # Validate business rules
   is_valid, error = BusinessLogicSecurity.validate_bounty_amount(amount)
   if not is_valid:
       raise ValueError(error)
   ```

5. **Security Logging**
   ```python
   # Log security event
   SecurityAudit.log_security_event("DATA_ACCESS", user.id, {...}, request)
   ```

---

**All OWASP Top 10 vulnerabilities are now addressed in the codebase! ✅**

