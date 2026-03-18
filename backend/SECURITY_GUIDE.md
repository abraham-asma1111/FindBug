# Security Guide: Implementing PUT and DELETE Methods

## Overview

This guide explains how to safely implement PUT and DELETE HTTP methods in the FindBug platform, addressing the security concerns raised by using these methods.

## Security Concerns Summary

### 1. CSRF (Cross-Site Request Forgery)
**Risk**: Attacker tricks authenticated user into making unwanted requests  
**Impact**: Data modification, deletion, unauthorized actions  
**Mitigation**: JWT tokens + CSRF tokens for cookie-based auth

### 2. IDOR (Insecure Direct Object References)
**Risk**: Users accessing resources they don't own by changing IDs  
**Impact**: Unauthorized data access/modification  
**Mitigation**: Resource ownership validation

### 3. Server Misconfiguration
**Risk**: Web server allows direct file operations  
**Impact**: File upload/deletion on server filesystem  
**Mitigation**: Proper server configuration

### 4. Lack of Authorization
**Risk**: Insufficient permission checks  
**Impact**: Privilege escalation  
**Mitigation**: Role-based + resource-level authorization

---

## Current Security Measures

### ✅ Already Implemented

1. **JWT Authentication** (`src/core/security.py`)
   - Stateless tokens
   - Implicit CSRF protection (tokens can't be read cross-domain)
   - Token expiration

2. **Role-Based Access Control** (`src/api/v1/middlewares/auth.py`)
   - `get_current_user()` - Validates JWT
   - `require_organization()` - Ensures user is organization
   - `require_researcher()` - Ensures user is researcher

3. **Security Audit Logging** (`src/core/security.py`)
   - All security events logged
   - IP tracking
   - User action tracking

4. **Input Validation** (`src/api/v1/schemas/`)
   - Pydantic schemas validate all inputs
   - Type checking
   - Field validation

### 🆕 New Security Additions

1. **CSRF Protection Middleware** (`src/api/v1/middlewares/csrf.py`)
   - Token generation and validation
   - Automatic protection for state-changing methods
   - JWT provides implicit CSRF protection

2. **Resource Authorization** (`src/core/authorization.py`)
   - Ownership validation
   - Access control checks
   - IDOR prevention

---

## How to Safely Implement PUT and DELETE

### Step 1: Enable CSRF Protection (Optional for JWT)

Since we use JWT tokens, CSRF protection is already built-in. JWT tokens are stored in headers (not cookies), so they can't be read by malicious sites.

**If you want additional CSRF protection:**

```python
# In src/main.py
from src.api/v1/middlewares.csrf import csrf_protect

app.middleware("http")(csrf_protect)
```

### Step 2: Always Validate Resource Ownership

**Example: Update Program Endpoint**

```python
from src.core.authorization import ResourceAuthorization

@router.put("/{program_id}", response_model=ProgramResponse)
def update_program(
    program_id: UUID,
    program_data: ProgramUpdate,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """Update a program - SECURE VERSION"""
    service = ProgramService(db)
    
    # 1. Get the resource
    program = service.get_program(program_id)
    
    # 2. CRITICAL: Verify ownership
    ResourceAuthorization.verify_program_ownership(
        program, current_user, action="modify"
    )
    
    # 3. Perform the update
    updates = program_data.dict(exclude_unset=True)
    program = service.update_program(
        program_id,
        current_user.organization.id,
        **updates
    )
    
    return program
```

### Step 3: Implement DELETE with Soft Delete

**Example: Delete Program Endpoint**

```python
@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program(
    program_id: UUID,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """Delete a program - SECURE VERSION"""
    service = ProgramService(db)
    
    # 1. Get the resource
    program = service.get_program(program_id)
    
    # 2. CRITICAL: Verify ownership
    ResourceAuthorization.verify_program_ownership(
        program, current_user, action="delete"
    )
    
    # 3. Soft delete (don't actually delete from database)
    service.soft_delete_program(program_id)
    
    # 4. Log the action
    SecurityAudit.log_security_event(
        "PROGRAM_DELETED",
        str(current_user.id),
        {"program_id": str(program_id), "program_name": program.name},
        request
    )
    
    return None
```

### Step 4: Configure CORS Properly

```python
# In src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://findbug.com",  # Production
        "http://localhost:3000"  # Development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-CSRF-Token"]
)
```

---

## Security Checklist for PUT/DELETE Endpoints

Before deploying any PUT or DELETE endpoint, verify:

- [ ] **Authentication**: User is authenticated (JWT token validated)
- [ ] **Authorization**: User has permission for this action (role check)
- [ ] **Ownership**: User owns the resource being modified (IDOR prevention)
- [ ] **Input Validation**: All inputs are validated with Pydantic schemas
- [ ] **Audit Logging**: Action is logged for security audit trail
- [ ] **Soft Delete**: DELETE uses soft delete (sets deleted_at timestamp)
- [ ] **CORS**: Only allowed origins can make requests
- [ ] **Rate Limiting**: Endpoint has rate limiting to prevent abuse

---

## Example: Complete Secure Endpoint

```python
from fastapi import APIRouter, Depends, HTTPException, status, Request
from src.api.v1.middlewares.auth import require_organization
from src.core.authorization import ResourceAuthorization
from src.core.security import SecurityAudit

@router.put("/{program_id}", response_model=ProgramResponse)
async def update_program(
    program_id: UUID,
    program_data: ProgramUpdate,
    request: Request,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Update a program - PRODUCTION-READY SECURE VERSION
    
    Security measures:
    - JWT authentication (implicit CSRF protection)
    - Role-based authorization (organization only)
    - Resource ownership validation (IDOR prevention)
    - Input validation (Pydantic schemas)
    - Audit logging
    """
    service = ProgramService(db)
    
    # Get resource
    program = service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    # Verify ownership (IDOR prevention)
    ResourceAuthorization.verify_program_ownership(
        program, current_user, action="modify"
    )
    
    # Validate and sanitize inputs (already done by Pydantic)
    updates = program_data.dict(exclude_unset=True)
    
    # Perform update
    updated_program = service.update_program(
        program_id,
        current_user.organization.id,
        **updates
    )
    
    # Log security event
    SecurityAudit.log_security_event(
        "PROGRAM_UPDATED",
        str(current_user.id),
        {
            "program_id": str(program_id),
            "fields_updated": list(updates.keys())
        },
        request
    )
    
    return updated_program


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program(
    program_id: UUID,
    request: Request,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db)
):
    """
    Delete a program - PRODUCTION-READY SECURE VERSION
    
    Uses soft delete to maintain data integrity
    """
    service = ProgramService(db)
    
    # Get resource
    program = service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    # Verify ownership
    ResourceAuthorization.verify_program_ownership(
        program, current_user, action="delete"
    )
    
    # Soft delete
    service.soft_delete_program(program_id)
    
    # Log security event
    SecurityAudit.log_security_event(
        "PROGRAM_DELETED",
        str(current_user.id),
        {
            "program_id": str(program_id),
            "program_name": program.name
        },
        request
    )
    
    return None
```

---

## Testing Security

### Test for IDOR Vulnerability

```python
# Test: User A tries to modify User B's program
def test_idor_protection():
    # User A creates a program
    program_a = create_program(user_a_token)
    
    # User B tries to modify User A's program
    response = requests.put(
        f"/api/v1/programs/{program_a.id}",
        headers={"Authorization": f"Bearer {user_b_token}"},
        json={"name": "Hacked!"}
    )
    
    # Should return 403 Forbidden
    assert response.status_code == 403
```

### Test for CSRF Protection

```python
# Test: Request without JWT token should fail
def test_csrf_protection():
    response = requests.delete(
        "/api/v1/programs/123",
        # No Authorization header
    )
    
    # Should return 401 Unauthorized
    assert response.status_code == 401
```

---

## Migration Plan: GET/POST → PUT/DELETE

### Phase 1: Add Security Infrastructure (✅ Done)
- CSRF middleware
- Resource authorization
- Audit logging

### Phase 2: Implement PUT/DELETE Endpoints
- Add PUT/DELETE decorators alongside POST/GET
- Keep both methods working during transition
- Test thoroughly

### Phase 3: Update Frontend
- Update API client to use PUT/DELETE
- Add CSRF token handling (if needed)
- Test all operations

### Phase 4: Deprecate POST for Updates
- Add deprecation warnings
- Monitor usage
- Remove POST methods after migration period

---

## Conclusion

Your platform is already well-secured with JWT authentication and role-based access control. The main additions needed for PUT/DELETE are:

1. **Resource ownership validation** (IDOR prevention) ✅ Added
2. **CSRF protection** (already handled by JWT) ✅ Built-in
3. **Audit logging** (already implemented) ✅ Exists
4. **Proper CORS configuration** ⚠️ Review

You can safely implement PUT and DELETE methods by following the patterns in this guide.

---

## Questions?

If you have questions about implementing specific endpoints securely, refer to:
- `src/core/authorization.py` - Resource ownership validation
- `src/api/v1/middlewares/csrf.py` - CSRF protection
- `src/core/security.py` - General security utilities
