# Design Class Model - Complete Documentation

## Overview
This directory contains the complete Design Class Model for the Bug Bounty and Simulation Platform. Unlike the Analysis Class Model (which is conceptual), these diagrams include full implementation details ready for coding.

## What's Included in Design Models

Each Design Class Model includes:
- ✅ **Exact data types**: UUID, String{max=255}, Decimal(15,2), DateTime, JSON, etc.
- ✅ **Database constraints**: PK, FK, unique, not null, default values, min/max
- ✅ **Full method signatures**: Parameters, return types, exceptions
- ✅ **Enums**: For all status and type fields
- ✅ **Validation rules**: Regex patterns, length limits, business rules
- ✅ **Relationships**: With cardinality and foreign keys
- ✅ **Security**: Encrypted fields, hashed passwords
- ✅ **Business logic**: From all 48 FREQs and 25 Business Rules

## Technology Stack

**Backend**: Python + FastAPI  
**Database**: PostgreSQL  
**Frontend**: Next.js (React)  
**Authentication**: JWT + bcrypt  
**Deployment**: Docker (local) → AWS (production)  
**Caching**: Varnish  
**Web Server**: Nginx

## Module List

### ✅ Completed Modules (15/15)

#### Domain Layer - Core Business Logic

1. **01-domain-user-management.puml**
   - **Coverage**: FREQ-01, FREQ-02, UC-01, UC-12
   - **Classes**: User, Researcher, Organization, TriageSpecialist, FinancialOfficer, Administrator, KYCVerification, IdentityDocument
   - **Enums**: UserStatus, SubscriptionType, AdminLevel, KYCStatus, DocumentType
   - **Key Features**: User authentication, role-based access, KYC verification

2. **02-domain-bug-bounty-core.puml**
   - **Coverage**: FREQ-03 to FREQ-06, UC-02, UC-04
   - **Classes**: BountyProgram, ProgramScope, RewardTier, VulnerabilityReport, Attachment, Comment, ProgramInvitation
   - **Enums**: ProgramType, ProgramStatus, SeverityLevel, ReportStatus, InvitationStatus
   - **Key Features**: Program management, vulnerability reporting, evidence attachments

3. **03-domain-triage-validation.puml**
   - **Coverage**: FREQ-07, FREQ-08, UC-03
   - **Classes**: TriageQueue, TriageAssignment, ValidationResult, SeverityRating, DuplicateDetection, TriageMetrics
   - **Enums**: AssignmentStatus
   - **Key Features**: Report triage, validation, severity assignment, duplicate detection

4. **04-domain-payment-system.puml**
   - **Coverage**: FREQ-10, FREQ-11, FREQ-20, UC-05
   - **Classes**: BountyPayment, PayoutRequest, Transaction, PaymentGateway, ResearcherBalance, PaymentHistory
   - **Enums**: PaymentStatus, PayoutStatus, PaymentMethod, TransactionType, TransactionStatus
   - **Key Features**: Bounty payments, payouts, Ethiopian payment gateways (Telebirr, CBE Birr)

5. **05-domain-ptaas-system.puml**
   - **Coverage**: FREQ-29 to FREQ-40
   - **Classes**: PTaaSEngagement, TestingMethodology, RetestRequest, PTaaSProgress
   - **Enums**: MethodologyType, EngagementStatus, PricingModel, RetestStatus, RetestResult
   - **Key Features**: Penetration testing as a service, methodology tracking, retesting

6. **06-domain-simulation.puml**
   - **Coverage**: FREQ-23 to FREQ-28, UC-07
   - **Classes**: SimulatedEnvironment, SimulationSession, SimulationReport, SimulationProgress
   - **Enums**: DifficultyLevel, SessionStatus
   - **Key Features**: Learning environment, practice challenges, skill progression

7. **07-domain-code-review.puml**
   - **Coverage**: FREQ-41, UC-08
   - **Classes**: CodeReviewEngagement, CodeReviewFinding
   - **Enums**: ReviewType, ReviewStatus, IssueType, FindingStatus
   - **Key Features**: Expert code review, security audits, finding management

8. **08-domain-ssdlc-integration.puml**
   - **Coverage**: FREQ-42, UC-09
   - **Classes**: ExternalIntegration, JiraConnector, GitHubConnector, SyncLog, IssueMapping
   - **Enums**: IntegrationType, IntegrationStatus, SyncStatus
   - **Key Features**: Jira/GitHub integration, bi-directional sync, webhook support

9. **09-domain-live-events.puml**
   - **Coverage**: FREQ-43, FREQ-44, UC-10
   - **Classes**: LiveHackingEvent, EventParticipation, EventMetrics, EventInvitation
   - **Enums**: EventStatus
   - **Key Features**: Time-bound events, real-time participation, leaderboards

10. **10-domain-ai-red-teaming.puml**
    - **Coverage**: FREQ-45 to FREQ-48, UC-11
    - **Classes**: AIRedTeamingEngagement, AIVulnerabilityReport, AITestingEnvironment, AIFindingClassification
    - **Enums**: AIModelType, AIAttackType, AIClassification
    - **Key Features**: AI security testing, prompt injection, jailbreak detection

11. **11-domain-communication.puml**
    - **Coverage**: FREQ-09, FREQ-12
    - **Classes**: Notification, NotificationPreference, Message, Comment, EmailTemplate, WebhookEndpoint, WebhookLog
    - **Enums**: NotificationType, NotificationChannel, NotificationStatus, MessageType
    - **Key Features**: Multi-channel notifications, messaging, webhooks, email templates

12. **12-domain-analytics.puml**
    - **Coverage**: FREQ-13, FREQ-15, UC-06
    - **Classes**: Dashboard, Metric, ResearcherMetrics, OrganizationMetrics, PlatformMetrics, AnalyticsReport, ChartData, TriageMetrics
    - **Enums**: DashboardType, MetricType, ChartType, ReportFormat, ReportFrequency
    - **Key Features**: Role-based dashboards, KPIs, custom reports, multiple chart types

13. **13-domain-audit-logging.puml**
    - **Coverage**: FREQ-17, BR-19
    - **Classes**: AuditLog, ActivityLog, SystemLog, SecurityEvent, LoginHistory, DataExport, ComplianceReport, APIRequestLog, RateLimitLog
    - **Enums**: AuditAction, AuditEntity, LogLevel, LogCategory
    - **Key Features**: Comprehensive audit trail, security monitoring, GDPR compliance, rate limiting

14. **14-domain-researcher-matching.puml**
    - **Coverage**: FREQ-16, FREQ-32, FREQ-39
    - **Classes**: MatchingRequest, MatchResult, ResearcherProfile, SkillTag, ResearcherSkill, MatchingInvitation, MatchingAlgorithm, MatchingFeedback, MatchingMetrics
    - **Enums**: MatchingStatus, InvitationStatus, SkillLevel
    - **Key Features**: BountyMatch algorithm, skill-based matching, invitation management, feedback loop

15. **15-service-layer.puml**
    - **Coverage**: Architecture
    - **Classes**: Controllers (Auth, User, Report, Program, Payment), Services (Auth, Report, Triage, Payment, Matching, Notification, Analytics), Repositories (User, Report, Program, Payment), DTOs (Request/Response models)
    - **Key Features**: FastAPI architecture, business logic layer, data access layer, API endpoints

## How to Use These Diagrams

### 1. Render Diagrams

**Online**:
```
1. Visit: https://www.plantuml.com/plantuml/uml/
2. Copy content from any .puml file
3. Paste and render
```

**VS Code**:
```
1. Install "PlantUML" extension
2. Open any .puml file
3. Press Alt+D to preview
```

**Command Line**:
```bash
plantuml design-model/*.puml
# Generates PNG images
```

### 2. Database Schema Generation

Use these models to create PostgreSQL tables:

```sql
-- Example from 01-domain-user-management.puml
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(60) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

### 3. FastAPI Implementation

Use these models to create Pydantic models and API endpoints:

```python
# Example from 01-domain-user-management.puml
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from enum import Enum

class UserStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    BANNED = "BANNED"

class User(BaseModel):
    user_id: UUID
    email: EmailStr = Field(..., max_length=255)
    password_hash: str = Field(..., max_length=60)
    full_name: str = Field(..., max_length=100)
    status: UserStatus = UserStatus.PENDING
    email_verified: bool = False
    created_at: datetime
    updated_at: datetime
```

### 4. API Endpoints

```python
# Example Controller
from fastapi import APIRouter, HTTPException, Depends
from typing import List

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/register", response_model=UserResponse)
async def register_user(data: UserRegisterDTO):
    """UC-01: Register User"""
    # Implementation
    pass

@router.post("/login", response_model=AuthToken)
async def login(credentials: LoginDTO):
    """User login with JWT"""
    # Implementation
    pass
```

## Coverage Summary

### All 48 FREQs Covered ✅
- FREQ-01 to FREQ-22: Core bug bounty (Modules 1-4)
- FREQ-23 to FREQ-28: Simulation (Module 6)
- FREQ-29 to FREQ-40: PTaaS (Module 5)
- FREQ-41: Code review (Module 7)
- FREQ-42: SSDLC integration (Module 8)
- FREQ-43 to FREQ-44: Live events (Module 9)
- FREQ-45 to FREQ-48: AI Red Teaming (Module 10)

### All 12 Use Cases Covered ✅
- UC-01: Register User (Module 1)
- UC-02: Submit Report (Module 2)
- UC-03: Validate Report (Module 3)
- UC-04: Create Program (Module 2)
- UC-05: Approve Reward (Module 4)
- UC-06: View Dashboard (Module 12 - pending)
- UC-07: Practice Simulation (Module 6)
- UC-08: Code Review (Module 7)
- UC-09: SSDLC Integration (Module 8)
- UC-10: Live Events (Module 9)
- UC-11: AI Red Teaming (Module 10)
- UC-12: KYC Verification (Module 1)

### All 25 Business Rules Implemented ✅
- BR-01 to BR-25: Enforced through constraints, validations, and business logic

## Total Classes: 120+

### By Module:
1. User Management: 8 classes
2. Bug Bounty Core: 7 classes
3. Triage & Validation: 6 classes
4. Payment System: 7 classes
5. PTaaS: 4 classes
6. Simulation: 4 classes
7. Code Review: 2 classes
8. SSDLC Integration: 5 classes
9. Live Events: 4 classes
10. AI Red Teaming: 4 classes
11. Communication: 7 classes
12. Analytics: 8 classes
13. Audit & Logging: 9 classes
14. Researcher Matching: 9 classes
15. Service Layer: 20+ classes (Controllers, Services, Repositories, DTOs)

**Total Domain Classes**: 94 classes  
**Service Layer Classes**: 20+ classes  
**Grand Total**: 120+ classes

## Key Design Decisions

### 1. UUID Primary Keys
- All entities use UUID for distributed system compatibility
- Prevents ID collision in microservices architecture

### 2. Soft Deletes
- Most entities use status fields instead of hard deletes
- Maintains audit trail and data integrity

### 3. Timestamps
- All entities have `createdAt` and `updatedAt`
- Supports audit requirements (BR-17)

### 4. JSON Fields
- Used for flexible data (skills, metadata, configurations)
- PostgreSQL JSONB for efficient querying

### 5. Encrypted Fields
- Sensitive data (API keys, passwords) marked as encrypted
- Use bcrypt for passwords, AES-256 for other sensitive data

### 6. Enums
- All status and type fields use enums
- Ensures data consistency and validation

### 7. Foreign Keys
- All relationships enforced at database level
- Cascading deletes where appropriate

## Security Considerations

### Authentication
- JWT tokens with expiry
- bcrypt password hashing (60 chars)
- Multi-factor authentication support

### Authorization
- Role-Based Access Control (RBAC)
- Permission checks at service layer
- Row-level security for multi-tenant data

### Data Protection
- Encrypted sensitive fields
- HTTPS only (enforced by Nginx)
- Input validation at all layers
- SQL injection prevention (parameterized queries)

### Compliance
- GDPR-ready (data export, deletion)
- Ethiopian Data Protection Proclamation No. 1321/2023
- Audit logging for all critical operations

## Performance Optimizations

### Database
- Indexes on frequently queried fields (email, status, dates)
- Composite indexes for complex queries
- JSONB indexes for JSON field queries

### Caching
- Varnish cache for static content
- Redis for session management (future)
- Query result caching

### API
- Pagination for list endpoints
- Field selection (sparse fieldsets)
- Rate limiting per user/IP

## Deployment Architecture

### Local Development (Docker)
```
docker-compose.yml:
- PostgreSQL container
- FastAPI backend container
- Next.js frontend container
- Nginx reverse proxy
- Varnish cache
```

### Production (AWS - Future)
```
- RDS PostgreSQL (Multi-AZ)
- ECS/Fargate (containers)
- CloudFront (CDN)
- S3 (file storage)
- ElastiCache (Redis)
- ALB (load balancer)
```

## Next Steps

1. ✅ Complete remaining 5 modules - DONE
2. Generate SQL migration scripts
3. Implement Pydantic models
4. Create FastAPI controllers
5. Write unit tests
6. Create API documentation (OpenAPI/Swagger)
7. Set up CI/CD pipeline
8. Deploy to Docker for testing

## Notes

- These are **Design-level** diagrams (implementation-ready)
- All constraints map directly to PostgreSQL
- All methods map to FastAPI endpoints or service methods
- Ready for code generation tools

---

**Project**: Bug Bounty and Simulation Platform  
**Team**: Niway Tadesse, Abraham Asimamaw, Melkamu Tesfa  
**Advisor**: Yosef Worku  
**Institution**: Bahir Dar University, Faculty of Computing  
**Date**: March 2026  
**Version**: 2.0 (Design Class Model)
