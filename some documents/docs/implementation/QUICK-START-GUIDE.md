# Quick Start Guide - Backend First Implementation

**Date**: March 13, 2026  
**Approach**: Backend + Database First  
**First FREQ**: FREQ-01 (Multi-role registration and login)

---

## 🚀 GETTING STARTED

### Prerequisites
```bash
# Install required tools
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL client (psql)
- Git
```

---

## 📋 STEP-BY-STEP IMPLEMENTATION

### WEEK 1: PROJECT SETUP

#### Day 1: Initialize Project
```bash
# Create project structure
mkdir bug-bounty-platform
cd bug-bounty-platform

# Initialize Git
git init
git remote add origin <your-repo-url>

# Create folder structure
mkdir -p backend/src/{core,domain,services,api,tasks,utils,data}
mkdir -p backend/tests/{unit,integration,e2e}
mkdir -p backend/migrations
mkdir -p frontend/src/{app,components,hooks,lib,store,types,styles}
mkdir -p docs/{architecture,api,database,deployment}
mkdir -p infrastructure/{terraform,kubernetes,monitoring}

# Copy hybrid structure as reference
cp project-structures/hybrid-structure.md STRUCTURE.md
```

#### Day 2: Docker Setup
```bash
# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: bugbounty
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

volumes:
  postgres_data:
  minio_data:
EOF

# Start services
docker-compose up -d

# Verify services
docker-compose ps
psql -h localhost -U postgres -d bugbounty -c "SELECT version();"
redis-cli ping
```

#### Day 3: Backend Setup
```bash
cd backend

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
redis==5.0.1
celery==5.3.4
boto3==1.29.7
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2
EOF

# Install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bugbounty
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
EOF

# Create main.py
cat > src/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Bug Bounty Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
EOF

# Test backend
python src/main.py
# Visit: http://localhost:8000/docs
```

---

### WEEK 2-3: FREQ-01 BACKEND

#### Day 1-2: Database Schema
```bash
# Initialize Alembic
cd backend
alembic init migrations

# Edit alembic.ini
# Set: sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/bugbounty

# Create migration
alembic revision --autogenerate -m "Create users tables"

# Edit migration file: migrations/versions/xxx_create_users_tables.py
```

```python
# migrations/versions/xxx_create_users_tables.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

def upgrade():
    # Users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    
    # Researchers table
    op.create_table(
        'researchers',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('country', sa.String(100)),
        sa.Column('bio', sa.Text),
        sa.Column('reputation_score', sa.Integer, default=0),
        sa.Column('rank', sa.String(50), default='Beginner'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
    )
    
    # Organizations table
    op.create_table(
        'organizations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('company_name', sa.String(255), nullable=False),
        sa.Column('website', sa.String(255)),
        sa.Column('industry', sa.String(100)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
    )

def downgrade():
    op.drop_table('organizations')
    op.drop_table('researchers')
    op.drop_table('users')
```

```bash
# Run migration
alembic upgrade head

# Verify tables
psql -h localhost -U postgres -d bugbounty -c "\dt"
```

#### Day 2-3: Models
```python
# backend/src/domain/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # researcher, organization, staff
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    researcher = relationship("Researcher", back_populates="user", uselist=False)
    organization = relationship("Organization", back_populates="user", uselist=False)

# backend/src/domain/models/researcher.py
class Researcher(Base):
    __tablename__ = "researchers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    full_name = Column(String(255), nullable=False)
    country = Column(String(100))
    bio = Column(Text)
    reputation_score = Column(Integer, default=0)
    rank = Column(String(50), default='Beginner')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="researcher")

# backend/src/domain/models/organization.py
class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    company_name = Column(String(255), nullable=False)
    website = Column(String(255))
    industry = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="organization")
```

#### Day 3-5: Services
```python
# backend/src/services/auth_service.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from ..domain.models.user import User
from ..domain.models.researcher import Researcher
from ..domain.models.organization import Organization

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db_session):
        self.db = db_session
    
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    def register_researcher(self, email: str, password: str, full_name: str, country: str):
        # Check if email exists
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        # Create user
        user = User(
            email=email,
            password_hash=self.hash_password(password),
            role="researcher"
        )
        self.db.add(user)
        self.db.flush()
        
        # Create researcher profile
        researcher = Researcher(
            user_id=user.id,
            full_name=full_name,
            country=country
        )
        self.db.add(researcher)
        self.db.commit()
        
        # TODO: Send verification email
        
        return user
    
    def login(self, email: str, password: str):
        # Find user
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError("Invalid credentials")
        
        # Verify password
        if not self.verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        
        # Check if verified
        if not user.is_verified:
            raise ValueError("Email not verified")
        
        # Generate token
        access_token = self.create_access_token(
            data={"sub": user.email, "role": user.role}
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
```

#### Day 5-7: API Endpoints
```python
# backend/src/api/v1/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field

class ResearcherRegisterSchema(BaseModel):
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

# backend/src/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...schemas.auth import *
from ....services.auth_service import AuthService
from ....core.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register/researcher", response_model=dict)
async def register_researcher(
    data: ResearcherRegisterSchema,
    db: Session = Depends(get_db)
):
    try:
        auth_service = AuthService(db)
        user = auth_service.register_researcher(
            email=data.email,
            password=data.password,
            full_name=data.full_name,
            country=data.country
        )
        return {
            "message": "Registration successful. Please verify your email.",
            "user_id": str(user.id)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginSchema,
    db: Session = Depends(get_db)
):
    try:
        auth_service = AuthService(db)
        token_data = auth_service.login(data.email, data.password)
        return token_data
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
```

#### Day 7: Testing
```bash
# Test with curl
curl -X POST http://localhost:8000/api/v1/auth/register/researcher \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#",
    "full_name": "Test User",
    "country": "Ethiopia"
  }'

curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#"
  }'

# Run pytest
pytest tests/unit/test_auth_service.py -v
pytest tests/integration/test_auth_api.py -v
pytest --cov=src tests/
```

---

### WEEK 3-4: FREQ-01 FRONTEND

#### Day 1: Frontend Setup
```bash
cd frontend

# Create Next.js app
npx create-next-app@latest . --typescript --tailwind --app

# Install dependencies
npm install axios react-hook-form zod @hookform/resolvers

# Create API client
mkdir -p src/lib
```

```typescript
// frontend/src/lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function registerResearcher(data: {
  email: string;
  password: string;
  full_name: string;
  country: string;
}) {
  const response = await api.post('/auth/register/researcher', data);
  return response.data;
}

export async function login(data: { email: string; password: string }) {
  const response = await api.post('/auth/login', data);
  return response.data;
}

export default api;
```

#### Day 2-5: Build UI
```typescript
// frontend/src/app/(auth)/register/page.tsx
'use client';

import { useForm } from 'react-hook-form';
import { registerResearcher } from '@/lib/api';
import { useRouter } from 'next/navigation';

export default function RegisterPage() {
  const router = useRouter();
  const { register, handleSubmit, formState: { errors } } = useForm();

  const onSubmit = async (data: any) => {
    try {
      await registerResearcher(data);
      alert('Registration successful! Please check your email.');
      router.push('/login');
    } catch (error) {
      alert('Registration failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <form onSubmit={handleSubmit(onSubmit)} className="w-full max-w-md space-y-4">
        <h1 className="text-2xl font-bold">Register as Researcher</h1>
        
        <input
          {...register('email', { required: true })}
          type="email"
          placeholder="Email"
          className="w-full px-4 py-2 border rounded"
        />
        
        <input
          {...register('password', { required: true, minLength: 8 })}
          type="password"
          placeholder="Password"
          className="w-full px-4 py-2 border rounded"
        />
        
        <input
          {...register('full_name', { required: true })}
          placeholder="Full Name"
          className="w-full px-4 py-2 border rounded"
        />
        
        <input
          {...register('country', { required: true })}
          placeholder="Country"
          className="w-full px-4 py-2 border rounded"
        />
        
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
        >
          Register
        </button>
      </form>
    </div>
  );
}
```

#### Day 6-7: Integration Testing
```bash
# Start backend
cd backend
python src/main.py

# Start frontend
cd frontend
npm run dev

# Test full flow
1. Visit http://localhost:3000/register
2. Fill form and submit
3. Check database: psql -d bugbounty -c "SELECT * FROM users;"
4. Test login at http://localhost:3000/login
```

---

## ✅ FREQ-01 COMPLETE CHECKLIST

### Backend
- [ ] Database tables created (users, researchers, organizations)
- [ ] Models implemented
- [ ] Auth service implemented
- [ ] API endpoints working
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Postman tests passing
- [ ] API documented

### Frontend
- [ ] Registration form working
- [ ] Login form working
- [ ] API integration working
- [ ] Error handling implemented
- [ ] Success messages working
- [ ] Responsive design
- [ ] User flow tested

### Integration
- [ ] Full registration flow works
- [ ] Full login flow works
- [ ] JWT token works
- [ ] No critical bugs

---

## 🚀 NEXT STEPS

After FREQ-01 is complete:
1. Move to FREQ-02 (Email verification, MFA)
2. Follow same backend-first approach
3. Continue through all 48 FREQs

**You're ready to start building!**

