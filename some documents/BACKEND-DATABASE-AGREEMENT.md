# Backend & Database Implementation Agreement

**Date**: March 15, 2026  
**Team**: Niway Tadesse, Abraham Asimamaw, Melkamu Tesfa  
**Status**: AGREED ✅

---

## 🎯 Core Agreements

### 1. Technology Stack (FINAL)
- **Backend Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Authentication**: JWT (python-jose)
- **Password Hashing**: Bcrypt (passlib)
- **Cache**: Redis 7.0+
- **Task Queue**: Celery 5.3+
- **Storage**: MinIO (local), S3 (production)

### 2. Architecture Pattern (FINAL)
```
Request → API Endpoint → Service Layer → Repository → Database
                ↓
         Pydantic Schema (validation)
```

**Layers**:
1. **API Layer** (`api/v1/endpoints/`) - HTTP endpoints, request/response
2. **Schema Layer** (`api/v1/schemas/`) - Pydantic models for validation
3. **Service Layer** (`services/`) - Business logic
4. **Repository Layer** (`domain/repositories/`) - Data access
5. **Model Layer** (`domain/models/`) - SQLAlchemy models
6. **Database Layer** - PostgreSQL

### 3. Security (FINAL)
- **OWASP Top 10**: All vulnerabilities addressed in code
- **RBAC**: Role-based access control for all endpoints
- **Input Validation**: Pydantic + custom sanitization
- **SQL Injection**: Prevented by SQLAlchemy ORM
- **XSS**: HTML sanitization on all user inputs
- **CSRF**: Token-based protection
- **Rate Limiting**: Implemented for all public endpoints
- **Audit Logging**: All security events logged

---

## 📊 Database Agreements

### 1. Naming Conventions
```sql
-- Tables: lowercase, plural, snake_case
users, researchers, organizations, programs, reports

-- Columns: lowercase, snake_case
user_id, created_at, is_verified, full_name

-- Primary Keys: id (UUID)
id UUID PRIMARY KEY DEFAULT gen_random_uuid()

-- Foreign Keys: {table}_id
user_id, program_id, organization_id

-- Timestamps: created_at, updated_at
created_at TIMESTAMP DEFAULT NOW()
updated_at TIMESTAMP DEFAULT NOW()

-- Boolean: is_{condition}, has_{condition}
is_active, is_verified, has_mfa_enabled

-- Indexes: idx_{table}_{column}
idx_users_email, idx_reports_status
```

### 2. Data Types
```sql
-- IDs: UUID (not SERIAL)
id UUID PRIMARY KEY DEFAULT gen_random_uuid()

-- Strings: VARCHAR with limits
email VARCHAR(255)
name VARCHAR(255)
description TEXT

-- Numbers: INTEGER, DECIMAL
reputation_score INTEGER
bounty_amount DECIMAL(10, 2)

-- Dates: TIMESTAMP (UTC)
created_at TIMESTAMP DEFAULT NOW()

-- Boolean: BOOLEAN (not TINYINT)
is_active BOOLEAN DEFAULT TRUE

-- JSON: JSONB (not JSON)
metadata JSONB
```

### 3. Constraints
```sql
-- Always use constraints
NOT NULL          -- Required fields
UNIQUE            -- Unique values (email, username)
CHECK             -- Value validation
FOREIGN KEY       -- Referential integrity
DEFAULT           -- Default values

-- Example
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('researcher', 'organization', 'staff', 'admin')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4. Indexes
```sql
-- Index all foreign keys
CREATE INDEX idx_reports_user_id ON reports(user_id);
CREATE INDEX idx_reports_program_id ON reports(program_id);

-- Index frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_programs_visibility ON programs(visibility);

-- Composite indexes for common queries
CREATE INDEX idx_reports_user_status ON reports(user_id, status);
```

### 5. Soft Deletes
```sql
-- Use soft deletes for important data
deleted_at TIMESTAMP NULL

-- Query active records
WHERE deleted_at IS NULL

-- Soft delete
UPDATE users SET deleted_at = NOW() WHERE id = ?
```

---

## 🏗️ Backend Agreements

### 1. File Structure (FINAL)
```
backend/src/
├── core/                    # Core utilities
│   ├── config.py           # Configuration
│   ├── database.py         # Database connection
│   ├── security.py         # Security utilities
│   ├── dependencies.py     # FastAPI dependencies
│   └── exceptions.py       # Custom exceptions
│
├── domain/                  # Domain layer
│   ├── models/             # SQLAlchemy models (one file per model)
│   │   ├── user.py
│   │   ├── researcher.py
│   │   ├── organization.py
│   │   └── ...
│   └── repositories/       # Data access (one file per model)
│       ├── user_repository.py
│       ├── program_repository.py
│       └── ...
│
├── services/               # Business logic (one file per domain)
│   ├── auth_service.py
│   ├── user_service.py
│   ├── program_service.py
│   └── ...
│
├── api/v1/                 # API layer
│   ├── endpoints/          # Route handlers
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── ...
│   ├── schemas/            # Pydantic models
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── ...
│   └── middlewares/        # Custom middleware
│       ├── auth.py
│       └── rate_limit.py
│
└── main.py                 # Application entry point
```

### 2. Naming Conventions

**Files**: `snake_case.py`
```python
user_service.py
auth_service.py
program_repository.py
```

**Classes**: `PascalCase`
```python
class UserService:
class ProgramRepository:
class AuthSchema:
```

**Functions/Methods**: `snake_case`
```python
def create_user():
def get_program_by_id():
def validate_password():
```

**Constants**: `UPPER_SNAKE_CASE`
```python
MAX_FILE_SIZE = 10 * 1024 * 1024
DEFAULT_PAGE_SIZE = 20
```

**Private**: `_leading_underscore`
```python
def _internal_helper():
_cache = {}
```

### 3. Code Structure Pattern

**Model** (SQLAlchemy):
```python
# domain/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

**Repository** (Data Access):
```python
# domain/repositories/user_repository.py
from sqlalchemy.orm import Session
from typing import Optional
from ..models.user import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user
```

**Service** (Business Logic):
```python
# services/auth_service.py
from core.security import PasswordSecurity, TokenSecurity
from domain.repositories.user_repository import UserRepository
from domain.models.user import User

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def register_researcher(self, email: str, password: str, full_name: str) -> User:
        # Validate password strength
        is_valid, error = PasswordSecurity.validate_password_strength(password)
        if not is_valid:
            raise ValueError(error)
        
        # Check if email exists
        if self.user_repo.get_by_email(email):
            raise ValueError("Email already registered")
        
        # Create user
        user = User(
            email=email,
            password_hash=PasswordSecurity.hash_password(password),
            role="researcher"
        )
        
        return self.user_repo.create(user)
    
    def login(self, email: str, password: str) -> dict:
        # Get user
        user = self.user_repo.get_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")
        
        # Verify password
        if not PasswordSecurity.verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        
        # Generate token
        token = TokenSecurity.create_access_token(
            {"sub": user.email, "role": user.role}
        )
        
        return {"access_token": token, "token_type": "bearer"}
```

**Schema** (Pydantic):
```python
# api/v1/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field

class RegisterResearcherSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)
    country: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
```

**Endpoint** (FastAPI):
```python
# api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import require_permission, SecurityAudit
from services.auth_service import AuthService
from domain.repositories.user_repository import UserRepository
from ..schemas.auth import RegisterResearcherSchema, LoginSchema, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register/researcher", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_researcher(
    data: RegisterResearcherSchema,
    db: Session = Depends(get_db)
):
    """Register a new researcher"""
    try:
        # Create service
        user_repo = UserRepository(db)
        auth_service = AuthService(user_repo)
        
        # Register user
        user = auth_service.register_researcher(
            email=data.email,
            password=data.password,
            full_name=data.full_name
        )
        
        return {
            "message": "Registration successful",
            "user_id": str(user.id)
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginSchema,
    db: Session = Depends(get_db)
):
    """User login"""
    try:
        user_repo = UserRepository(db)
        auth_service = AuthService(user_repo)
        
        token_data = auth_service.login(data.email, data.password)
        return token_data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
```

---

## 📋 Development Workflow Agreement

### 1. For Each FREQ:

**Week 1: Backend**
```
Day 1-2: Database
├── Read ERD diagram
├── Create Alembic migration
├── Run migration
└── Verify schema

Day 2-3: Models
├── Create SQLAlchemy model
├── Create repository
└── Write unit tests

Day 3-5: Services
├── Implement business logic
├── Add security controls
└── Write unit tests

Day 5-6: API
├── Create Pydantic schemas
├── Create endpoints
├── Add authentication/authorization
└── Write integration tests

Day 7: Testing
├── Test with Postman
├── Run pytest
└── Fix bugs
```

**Week 2: Frontend** (after backend is stable)

### 2. Testing Requirements

**Unit Tests** (pytest):
```python
# tests/unit/test_auth_service.py
def test_register_researcher_success():
    # Test successful registration
    pass

def test_register_researcher_duplicate_email():
    # Test duplicate email error
    pass

def test_login_success():
    # Test successful login
    pass

def test_login_invalid_credentials():
    # Test invalid credentials
    pass
```

**Integration Tests**:
```python
# tests/integration/test_auth_api.py
def test_register_endpoint():
    response = client.post("/api/v1/auth/register/researcher", json={...})
    assert response.status_code == 201
```

**Coverage Requirement**: Minimum 80%

### 3. Code Review Checklist

Before merging:
- [ ] All tests passing
- [ ] Code coverage > 80%
- [ ] Security controls applied
- [ ] Input validation implemented
- [ ] Error handling implemented
- [ ] Logging added
- [ ] Documentation updated
- [ ] No hardcoded secrets
- [ ] Follows naming conventions
- [ ] Postman collection updated

---

## 🔒 Security Requirements (MANDATORY)

### Every Endpoint Must Have:

1. **Input Validation** (Pydantic)
```python
class CreateProgramSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., max_length=5000)
```

2. **Authentication** (JWT)
```python
@router.post("/programs")
async def create_program(current_user: User = Depends(get_current_user)):
    pass
```

3. **Authorization** (RBAC)
```python
@router.post("/programs")
@require_permission("create_programs")
async def create_program(current_user: User):
    pass
```

4. **Input Sanitization**
```python
from core.security import InputSanitization

safe_description = InputSanitization.sanitize_html(data.description)
```

5. **Security Logging**
```python
from core.security import SecurityAudit

SecurityAudit.log_security_event("DATA_MODIFICATION", user.id, {...}, request)
```

---

## 📊 Database Migration Agreement

### Migration Naming
```
{timestamp}_{action}_{table}.py

Examples:
2026_03_15_create_users_table.py
2026_03_16_add_mfa_to_users.py
2026_03_17_create_programs_table.py
```

### Migration Template
```python
"""Create users table

Revision ID: abc123
Revises: 
Create Date: 2026-03-15 10:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
    )
    
    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade():
    op.drop_index('idx_users_email')
    op.drop_table('users')
```

---

## ✅ Agreement Checklist

### We Agree On:
- [x] Technology stack (FastAPI, PostgreSQL, SQLAlchemy, Alembic)
- [x] Architecture pattern (API → Service → Repository → Model)
- [x] File structure (separate files for models, services, endpoints)
- [x] Naming conventions (snake_case, PascalCase, UPPER_CASE)
- [x] Database conventions (UUID, snake_case, timestamps)
- [x] Security requirements (OWASP Top 10, RBAC, input validation)
- [x] Testing requirements (80% coverage, unit + integration)
- [x] Code review process
- [x] Migration naming and structure
- [x] Development workflow (backend first, week 1 backend, week 2 frontend)

---

## 🚀 Ready to Start

**This agreement is final. We will follow these patterns for all 48 FREQs.**

**Next Step**: Begin FREQ-01 implementation following this agreement.

---

**Signed**: Team agrees to follow this document ✅

