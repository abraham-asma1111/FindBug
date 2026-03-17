# FindBug - Project Structure Documentation

**Project**: FindBug - Bug Bounty and Simulation Platform  
**Architecture**: Microservices  
**Team**: Niway Tadesse, Abraham Asimamaw, Melkamu Tesfa  
**Institution**: Bahir Dar University - BSc Cyber Security

---

## Root Directory Structure

```
FindBug/
├── backend/              # Authentication & API Microservice (Python/FastAPI)
├── frontend/             # Web Application (React/Next.js)
├── simulation/           # Challenge Simulation Engine
├── infrastructure/       # DevOps & Deployment
├── some documents/       # Project Documentation
├── docker-compose.yml    # Docker services configuration
└── README.md            # Project overview
```

---

## 1. Backend (Authentication Microservice)

**Technology**: Python 3.13, FastAPI, PostgreSQL, SQLAlchemy  
**Port**: 8001  
**Branch**: `auth-service`

### Directory Structure

```
backend/
├── src/
│   ├── api/                    # API Layer
│   │   └── v1/
│   │       ├── endpoints/      # API Endpoints (Controllers)
│   │       │   ├── auth.py     # Authentication endpoints (register, login, MFA, etc.)
│   │       │   ├── profile.py  # User profile endpoints
│   │       │   ├── domain.py   # Domain verification endpoints (organizations)
│   │       │   └── sso.py      # SSO endpoints (SAML 2.0)
│   │       ├── middlewares/    # Middleware Components
│   │       │   ├── auth.py     # JWT authentication middleware
│   │       │   └── rate_limit.py # Rate limiting middleware
│   │       └── schemas/        # Pydantic Schemas (Request/Response)
│   │           └── auth.py     # Auth-related schemas
│   │
│   ├── core/                   # Core Services & Utilities
│   │   ├── database.py         # Database connection & session management
│   │   ├── security.py         # Security utilities (password, JWT, tokens)
│   │   ├── email_service.py    # Email service (verification, password reset)
│   │   ├── ninja_service.py    # Ninja email generation & skills validation
│   │   ├── kyc_service.py      # Persona KYC integration
│   │   ├── sso_service.py      # SAML 2.0 SSO service
│   │   └── domain_verification.py # Domain verification (DNS, file, email)
│   │
│   ├── domain/                 # Domain Layer (Business Logic)
│   │   ├── models/             # SQLAlchemy Models (Database Tables)
│   │   │   ├── user.py         # User model (authentication)
│   │   │   ├── researcher.py   # Researcher profile model
│   │   │   ├── organization.py # Organization profile model
│   │   │   └── staff.py        # Staff model
│   │   └── repositories/       # Data Access Layer
│   │       ├── user_repository.py         # User CRUD operations
│   │       ├── researcher_repository.py   # Researcher CRUD operations
│   │       └── organization_repository.py # Organization CRUD operations
│   │
│   ├── services/               # Application Services
│   │   └── auth_service.py     # Authentication business logic
│   │
│   ├── tasks/                  # Background Tasks (Celery)
│   ├── utils/                  # Utility Functions
│   └── main.py                 # FastAPI Application Entry Point
│
├── migrations/                 # Alembic Database Migrations
│   └── versions/               # Migration Files
│       ├── 2026_03_15_2238_create_users_and_profiles_tables.py
│       ├── 2026_03_16_1346_align_with_extended_erd.py
│       ├── 2026_03_16_1505_add_email_verification_and_mfa_fields.py
│       ├── 2026_03_16_2028_add_bugcrowd_2026_enhancements.py
│       └── 2026_03_16_2045_add_refresh_tokens_and_password_reset.py
│
├── tests/                      # Test Suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── e2e/                    # End-to-end tests
│
├── scripts/                    # Utility Scripts
│   └── generate-secrets.sh     # Generate secret keys
│
├── venv/                       # Python Virtual Environment
├── requirements.txt            # Python Dependencies
├── alembic.ini                # Alembic Configuration
├── run_dev.py                 # Development Server Runner
├── .env.example               # Environment Variables Template
├── AUTH_SERVICE_STATUS.md     # Implementation Status
└── KYC_INTEGRATION.md         # Persona KYC Guide
```

### Key Files Explained

**Entry Points**:
- `src/main.py` - FastAPI application, router registration, CORS, startup/shutdown events
- `run_dev.py` - Development server with auto-reload

**API Layer**:
- `src/api/v1/endpoints/auth.py` - 16 authentication endpoints (register, login, MFA, password reset, etc.)
- `src/api/v1/endpoints/profile.py` - User profile endpoints (get profile by role)
- `src/api/v1/endpoints/domain.py` - Domain verification for organizations (DNS, file, email)
- `src/api/v1/endpoints/sso.py` - Enterprise SSO (SAML 2.0) for organizations

**Core Services**:
- `src/core/security.py` - Password hashing, JWT tokens, input sanitization, audit logging
- `src/core/email_service.py` - Email verification, password reset emails
- `src/core/ninja_service.py` - Generate ninja emails (`username@findbugninja.com`), validate skills
- `src/core/kyc_service.py` - Persona API integration for biometric KYC
- `src/core/sso_service.py` - SAML 2.0 request/response handling
- `src/core/domain_verification.py` - DNS TXT, file-based, email verification

**Domain Models**:
- `src/domain/models/user.py` - User authentication (email, password, MFA, tokens)
- `src/domain/models/researcher.py` - Researcher profile (ninja email, skills, KYC)
- `src/domain/models/organization.py` - Organization profile (domain verification, SSO)

**Repositories**:
- Data access layer with CRUD operations for each model
- Query methods (get_by_email, get_by_username, get_by_refresh_token, etc.)

---

## 2. Frontend (Web Application)

**Technology**: React/Next.js, TypeScript, Tailwind CSS  
**Port**: 3000  
**Branch**: `frontend` (to be created)

### Directory Structure

```
frontend/
├── public/                     # Static Assets
│   ├── icons/                  # App icons, favicons
│   ├── images/                 # Static images, logos
│   └── locales/                # Internationalization (i18n)
│       ├── en/                 # English translations
│       └── am/                 # Amharic translations
│
└── src/                        # Source Code
    ├── app/                    # Next.js App Router (Pages)
    │   ├── (auth)/             # Authentication pages group
    │   │   ├── login/          # Login page
    │   │   ├── register/       # Registration pages
    │   │   │   ├── researcher/ # Researcher registration
    │   │   │   └── organization/ # Organization registration
    │   │   ├── verify-email/   # Email verification page
    │   │   ├── forgot-password/ # Forgot password page
    │   │   └── reset-password/ # Reset password page
    │   │
    │   ├── (researcher)/       # Researcher portal
    │   │   ├── dashboard/      # Researcher dashboard
    │   │   ├── programs/       # Available bug bounty programs
    │   │   ├── submissions/    # Bug submissions
    │   │   ├── earnings/       # Earnings & payouts
    │   │   └── profile/        # Researcher profile
    │   │
    │   ├── (organization)/     # Organization portal
    │   │   ├── dashboard/      # Organization dashboard
    │   │   ├── programs/       # Manage programs
    │   │   ├── reports/        # Bug reports
    │   │   ├── team/           # Team management
    │   │   └── settings/       # Organization settings
    │   │
    │   └── (simulation)/       # Simulation environment
    │       ├── challenges/     # CTF-style challenges
    │       └── labs/           # Practice labs
    │
    ├── components/             # React Components
    │   ├── common/             # Shared components
    │   │   ├── Button.tsx      # Button component
    │   │   ├── Input.tsx       # Input component
    │   │   ├── Modal.tsx       # Modal component
    │   │   └── Toast.tsx       # Toast notifications
    │   │
    │   ├── features/           # Feature-specific components
    │   │   ├── auth/           # Auth components (LoginForm, RegisterForm, MFASetup)
    │   │   ├── profile/        # Profile components
    │   │   └── programs/       # Program components
    │   │
    │   ├── layout/             # Layout components
    │   │   ├── Header.tsx      # App header
    │   │   ├── Sidebar.tsx     # Navigation sidebar
    │   │   └── Footer.tsx      # App footer
    │   │
    │   └── ui/                 # UI primitives (shadcn/ui)
    │
    ├── hooks/                  # Custom React Hooks
    │   ├── useAuth.ts          # Authentication hook
    │   ├── useProfile.ts       # Profile management hook
    │   └── useAPI.ts           # API client hook
    │
    ├── lib/                    # Utility Libraries
    │   ├── api.ts              # API client (axios/fetch)
    │   ├── auth.ts             # Auth utilities (token storage)
    │   └── utils.ts            # Helper functions
    │
    ├── store/                  # State Management (Zustand/Redux)
    │   ├── authStore.ts        # Authentication state
    │   └── userStore.ts        # User profile state
    │
    ├── styles/                 # Global Styles
    │   └── globals.css         # Tailwind CSS imports
    │
    └── types/                  # TypeScript Type Definitions
        ├── auth.ts             # Auth types
        ├── user.ts             # User types
        └── api.ts              # API response types
```

### Frontend Folder Purposes

**public/**:
- Static files served directly by the web server
- Icons, images, fonts that don't need processing
- Localization files for multi-language support (English, Amharic)

**src/app/**:
- Next.js 13+ App Router pages
- Route groups: `(auth)`, `(researcher)`, `(organization)`, `(simulation)`
- Each folder = a route (e.g., `app/login/page.tsx` → `/login`)

**src/components/**:
- `common/` - Reusable UI components (buttons, inputs, modals)
- `features/` - Feature-specific components (LoginForm, ProgramCard)
- `layout/` - Page layout components (Header, Sidebar, Footer)
- `ui/` - Base UI primitives (shadcn/ui library)

**src/hooks/**:
- Custom React hooks for reusable logic
- `useAuth()` - Login, logout, token management
- `useProfile()` - Fetch and update user profile

**src/lib/**:
- Utility libraries and helper functions
- `api.ts` - Axios/fetch wrapper for API calls
- `auth.ts` - Token storage, JWT decode, auth helpers

**src/store/**:
- Global state management (Zustand or Redux)
- Authentication state, user profile, app settings

**src/types/**:
- TypeScript type definitions
- Interfaces for API requests/responses

---

## 3. Simulation (Challenge Engine)

**Technology**: Python, Docker, Kubernetes  
**Purpose**: CTF-style challenges and vulnerable applications

### Directory Structure

```
simulation/
└── src/
    ├── api/                    # Simulation API
    ├── challenges/             # Challenge Definitions
    │   ├── beginner/           # Easy challenges (XSS, SQL injection basics)
    │   ├── intermediate/       # Medium challenges (CSRF, IDOR)
    │   └── advanced/           # Hard challenges (RCE, deserialization)
    │
    ├── targets/                # Vulnerable Applications
    │   ├── web/                # Vulnerable web apps
    │   ├── api/                # Vulnerable APIs
    │   └── mobile/             # Vulnerable mobile backends
    │
    ├── isolation/              # Container Isolation
    │   └── docker/             # Docker configs for isolated environments
    │
    └── scoring/                # Scoring Engine
        └── validators/         # Challenge solution validators
```

### Simulation Folder Purposes

**challenges/**:
- CTF-style security challenges organized by difficulty
- Each challenge has: description, hints, flag, solution validator
- Researchers practice skills before hunting real bugs

**targets/**:
- Intentionally vulnerable applications for practice
- Isolated Docker containers for each target
- Researchers test without affecting production systems

**isolation/**:
- Container orchestration for challenge environments
- Network isolation between researchers
- Automatic cleanup after session ends

**scoring/**:
- Validates challenge solutions
- Awards points and reputation
- Tracks researcher progress

---

## 4. Infrastructure (DevOps)

**Technology**: Terraform, Kubernetes, Docker, Monitoring

### Directory Structure

```
infrastructure/
├── terraform/                  # Infrastructure as Code
│   ├── modules/                # Reusable Terraform modules
│   │   ├── vpc/                # Network configuration
│   │   ├── eks/                # Kubernetes cluster
│   │   ├── rds/                # PostgreSQL database
│   │   └── s3/                 # Object storage
│   └── environments/           # Environment-specific configs
│       ├── dev/                # Development environment
│       ├── staging/            # Staging environment
│       └── production/         # Production environment
│
├── kubernetes/                 # Kubernetes Manifests
│   ├── deployments/            # Application deployments
│   ├── services/               # Service definitions
│   ├── ingress/                # Ingress rules
│   └── configmaps/             # Configuration maps
│
├── monitoring/                 # Monitoring & Observability
│   ├── prometheus/             # Metrics collection
│   ├── grafana/                # Dashboards
│   └── alerts/                 # Alert rules
│
└── scripts/                    # Deployment Scripts
    ├── deploy.sh               # Deployment automation
    └── backup.sh               # Database backup
```

### Infrastructure Folder Purposes

**terraform/**:
- Infrastructure as Code (IaC)
- Provisions AWS/cloud resources
- Separate configs for dev/staging/production

**kubernetes/**:
- Container orchestration
- Deployment manifests for microservices
- Auto-scaling, load balancing, health checks

**monitoring/**:
- Prometheus for metrics collection
- Grafana for visualization
- Alert rules for incidents

---

## 5. Documentation

```
some documents/
├── docs/
│   ├── design/                 # Design Documents
│   │   ├── database-erd/       # Database ERD diagrams
│   │   ├── architecture/       # System architecture
│   │   └── api/                # API specifications
│   │
│   ├── requirements/           # Requirements Documents
│   │   ├── functional/         # Functional requirements
│   │   └── non-functional/     # Non-functional requirements
│   │
│   └── guides/                 # User Guides
│       ├── researcher/         # Researcher onboarding
│       └── organization/       # Organization onboarding
│
└── README.md                   # Documentation index
```

---

## Backend Architecture Layers

### 1. API Layer (`src/api/`)
**Purpose**: HTTP request handling, routing, validation  
**Components**:
- Endpoints (controllers)
- Middlewares (auth, rate limiting)
- Schemas (request/response validation)

### 2. Core Layer (`src/core/`)
**Purpose**: Shared services and utilities  
**Components**:
- Database connection
- Security utilities
- Email service
- Third-party integrations (Persona, SAML)

### 3. Domain Layer (`src/domain/`)
**Purpose**: Business logic and data models  
**Components**:
- Models (database tables)
- Repositories (data access)
- Business rules

### 4. Service Layer (`src/services/`)
**Purpose**: Application business logic  
**Components**:
- AuthService (registration, login, password management)
- Future: ProgramService, SubmissionService, PaymentService

---

## Frontend Architecture (Planned)

### App Router Structure (`src/app/`)

**Route Groups** (folders with parentheses):
- `(auth)/` - Public authentication pages (no layout)
- `(researcher)/` - Researcher portal (researcher layout)
- `(organization)/` - Organization portal (organization layout)
- `(simulation)/` - Simulation environment (simulation layout)

**Why Route Groups?**
- Different layouts for different user types
- Shared authentication logic
- Clean URL structure (parentheses don't appear in URL)

### Component Structure (`src/components/`)

**common/**:
- Reusable UI components used across the app
- Examples: Button, Input, Card, Modal, Toast

**features/**:
- Feature-specific components
- Examples: LoginForm, ProgramCard, SubmissionList

**layout/**:
- Page structure components
- Examples: Header (navigation), Sidebar (menu), Footer

**ui/**:
- Base UI primitives (shadcn/ui)
- Unstyled, accessible components

---

## Microservices Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     API Gateway                          │
│                  (nginx/Kong)                            │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼────────┐ ┌──────▼──────┐ ┌───────▼────────┐
│  Auth Service  │ │   Program   │ │  Submission    │
│  (Port 8001)   │ │   Service   │ │   Service      │
│                │ │  (Port 8002)│ │  (Port 8003)   │
└────────────────┘ └─────────────┘ └────────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                ┌─────────▼──────────┐
                │   PostgreSQL       │
                │   (Port 5432)      │
                └────────────────────┘
```

### Planned Microservices

1. **Auth Service** (✅ Complete) - Port 8001
   - User registration & authentication
   - MFA, KYC, SSO
   - Profile management

2. **Program Service** (⏳ Planned) - Port 8002
   - Bug bounty program management
   - Scope definition
   - Reward tiers

3. **Submission Service** (⏳ Planned) - Port 8003
   - Bug report submissions
   - Triage workflow
   - Severity assessment

4. **Payment Service** (⏳ Planned) - Port 8004
   - Chapa/Telebirr integration
   - Payout processing
   - Transaction history

5. **Notification Service** (⏳ Planned) - Port 8005
   - Email notifications
   - In-app notifications
   - Webhook delivery

6. **Simulation Service** (⏳ Planned) - Port 8006
   - Challenge management
   - Container orchestration
   - Scoring engine

---

## Git Branch Strategy

```
main                    # Production-ready code
├── auth-service        # Authentication microservice (✅ Current)
├── program-service     # Program management microservice
├── submission-service  # Submission microservice
├── payment-service     # Payment microservice
├── frontend            # Frontend application
└── simulation          # Simulation engine
```

Each microservice has its own branch for independent development and deployment.

---

## Database Schema

**Users Table** (Authentication):
- Core: id, email, password_hash, role
- Security: mfa_enabled, mfa_secret, is_locked, failed_login_attempts
- Tokens: refresh_token, password_reset_token, email_verification_token
- Timestamps: created_at, updated_at, last_login_at

**Researchers Table** (Profile):
- Identity: first_name, last_name, username, ninja_email
- Professional: skills (JSON), reputation_score, rank, total_earnings
- Verification: kyc_status, kyc_document_url
- Social: bio, website, github, twitter, linkedin

**Organizations Table** (Profile):
- Company: company_name, industry, website
- Verification: domain_verified, verified_domains, verification_status
- Business: tax_id, business_license_url
- SSO: sso_enabled, sso_provider, sso_metadata_url
- Subscription: subscription_type, subscription_expires_at

---

## Environment Configuration

### Development
- Backend: http://127.0.0.1:8001
- Frontend: http://localhost:3000
- Database: localhost:5432
- Redis: localhost:6379

### Production
- Backend: https://api.findbug.com
- Frontend: https://findbug.com
- Database: RDS PostgreSQL
- Redis: ElastiCache

---

## Key Design Decisions

1. **Microservices**: Independent services for scalability
2. **Dual-Portal**: Separate registration/auth for researchers vs organizations
3. **Ninja Email**: Researchers get `@findbugninja.com` aliases for testing
4. **Business Email Validation**: Organizations must use corporate emails
5. **Mandatory MFA**: Researchers must enable MFA after email verification
6. **Persona KYC**: Biometric verification for researcher payouts
7. **Domain Verification**: Organizations prove domain ownership
8. **Enterprise SSO**: SAML 2.0 for organization team members
9. **JWT Tokens**: Stateless authentication with refresh token rotation
10. **Rate Limiting**: Prevent brute force and abuse

---

**Last Updated**: March 17, 2026
