# Diagram Reference Guide for Implementation

**Date**: March 13, 2026  
**Purpose**: Map diagrams to implementation phases

---

## 🎯 HOW TO USE DIAGRAMS

### Implementation Order
1. **Database ERD** → Create tables and relationships
2. **Design Class Models** → Implement domain models and services
3. **Sequence Diagrams** → Understand workflow and API calls
4. **Activity Diagrams** → Implement business logic flow
5. **State Diagrams** → Implement entity state transitions

---

## 📊 PHASE 0: PROJECT SETUP (Week 1)

### Architecture Diagrams
- **component-diagram.puml** - Overall system architecture
- **deployment-diagram.puml** - Docker Compose setup
- **deployment-diagram-aws.puml** - Future AWS deployment

### Purpose
- Understand system components
- Setup Docker services correctly
- Plan infrastructure

---

## 📊 PHASE 1: AUTHENTICATION (FREQ 1-2, Weeks 2-5)

### Database Diagrams
**Primary**:
- `database-erd/01-core-tables.puml` - Users, researchers, organizations, staff tables
- `database-erd/database-schema.sql` - SQL schema for core tables

**What to implement**:
```sql
-- From 01-core-tables.puml
CREATE TABLE users (...)
CREATE TABLE researchers (...)
CREATE TABLE organizations (...)
CREATE TABLE staff (...)
CREATE TABLE roles (...)
CREATE TABLE permissions (...)
```

### Design Class Models
**Primary**:
- `design-class-models/design-model/01-domain-user-management.puml`
  - User, Researcher, Organization, Staff classes
  - UserRepository, AuthService
  - Password hashing, JWT generation

**What to implement**:
```python
# From 01-domain-user-management.puml
class User(Base):
    id, email, password_hash, role, is_verified, ...

class Researcher(Base):
    user_id, full_name, country, reputation_score, ...

class AuthService:
    register_researcher()
    register_organization()
    login()
    verify_email()
    reset_password()
```

### Sequence Diagrams
**Primary**:
- `sequence-diagrams/06-staff-provisioning.puml` - Staff creation workflow
- `sequence-diagrams/08-sso-navigation-flow.puml` - Multi-platform navigation

**What to implement**:
- Registration flow (Frontend → API → Service → Database)
- Login flow (Frontend → API → AuthService → JWT)
- Staff provisioning (Admin → API → UserService)

### Architecture Diagrams
**Primary**:
- `authentication-architecture.puml` - JWT, MFA, session management
- `multi-platform-navigation.puml` - Role-based routing

**What to implement**:
- JWT middleware
- Role-based access control (RBAC)
- MFA with TOTP

---

## 📊 PHASE 2: BUG BOUNTY CORE (FREQ 3-11, Weeks 6-13)

### Database Diagrams
**Primary**:
- `database-erd/01-core-tables.puml` - Programs, reports, VRT tables
- `database-erd/database-schema.sql` - Bug bounty tables

**What to implement**:
```sql
-- From 01-core-tables.puml
CREATE TABLE programs (...)
CREATE TABLE reports (...)
CREATE TABLE vrt_categories (...)
CREATE TABLE report_attachments (...)
CREATE TABLE messages (...)
CREATE TABLE bounties (...)
CREATE TABLE reputation_scores (...)
```

### Design Class Models
**Primary**:
- `design-class-models/design-model/02-domain-bug-bounty-core.puml`
  - Program, Report, VRTCategory classes
  - ProgramService, ReportService, VRTService
  
- `design-class-models/design-model/03-domain-triage-validation.puml`
  - TriageService, ValidationService
  - Deduplication logic

**What to implement**:
```python
# From 02-domain-bug-bounty-core.puml
class Program(Base):
    id, organization_id, name, scope, rewards, status, ...

class Report(Base):
    id, program_id, researcher_id, title, severity, status, ...

class ProgramService:
    create_program()
    publish_program()
    archive_program()

class ReportService:
    submit_report()
    update_status()
    assign_severity()

class VRTService:
    calculate_severity()
    map_to_priority()
    suggest_reward()
```

### Sequence Diagrams
**Primary**:
- `sequence-diagrams/01-bug-report-submission.puml` - Report submission flow
- `sequence-diagrams/02-triage-validation.puml` - Triage workflow

**What to implement**:
- Report submission (Researcher → API → ReportService → VRTService)
- Triage workflow (Staff → API → TriageService → Validation)
- File upload (Frontend → API → MinIO/S3)

### Activity Diagrams
**Primary**:
- `activity-diagrams/01-bug-report-workflow.puml` - Complete bug bounty flow
- `activity-diagrams/06-program-creation.puml` - Program creation steps

**What to implement**:
- Report lifecycle (New → Triaged → Valid → Resolved)
- Program lifecycle (Draft → Published → Archived)
- Bounty approval workflow

---

## 📊 PHASE 3: PLATFORM OPERATIONS (FREQ 12-22, Weeks 14-17)

### Database Diagrams
**Primary**:
- `database-erd/03-communication-analytics.puml` - Notifications, analytics tables

**What to implement**:
```sql
-- From 03-communication-analytics.puml
CREATE TABLE notifications (...)
CREATE TABLE audit_logs (...)
CREATE TABLE analytics_metrics (...)
CREATE TABLE payment_transactions (...)
```

### Design Class Models
**Primary**:
- `design-class-models/design-model/11-domain-communication.puml`
  - NotificationService, MessageService
  
- `design-class-models/design-model/12-domain-analytics.puml`
  - AnalyticsService, MetricsCalculator
  
- `design-class-models/design-model/13-domain-audit-logging.puml`
  - AuditService, ActivityLogger

- `design-class-models/design-model/04-domain-payment-system.puml`
  - PaymentService, CommissionCalculator

**What to implement**:
```python
# From design class models
class NotificationService:
    send_notification()
    send_email()
    mark_as_read()

class AnalyticsService:
    calculate_metrics()
    generate_report()
    get_trends()

class PaymentService:
    process_payout()
    calculate_commission()  # 30%
    integrate_chapa()
    integrate_telebirr()
```

### Sequence Diagrams
**Primary**:
- `sequence-diagrams/03-payment-processing.puml` - Payment workflow

**What to implement**:
- Payment processing (Staff → API → PaymentService → Gateway)
- Commission calculation (30% platform fee)
- Payout tracking

### Activity Diagrams
**Primary**:
- `activity-diagrams/03-payment-withdrawal.puml` - Payment flow
- `activity-diagrams/12-analytics-reporting.puml` - Analytics generation
- `activity-diagrams/13-staff-management.puml` - Staff operations

**What to implement**:
- Payment approval workflow
- Analytics calculation
- Dashboard data aggregation

### Architecture Diagrams
**Primary**:
- `dashboard-layouts.puml` - Dashboard designs for all roles

**What to implement**:
- Researcher dashboard (submissions, earnings, rank)
- Organization dashboard (programs, reports, trends)
- Staff dashboard (triage queue)
- Admin dashboard (platform overview)

---

## 📊 PHASE 4: LEARNING PLATFORM (FREQ 23-28, Weeks 18-19)

### Database Diagrams
**Primary**:
- `database-erd/02-engagement-tables.puml` - Simulation tables

**What to implement**:
```sql
-- Simulation tables
CREATE TABLE challenges (...)
CREATE TABLE challenge_submissions (...)
CREATE TABLE learning_progress (...)
CREATE TABLE badges (...)
```

### Design Class Models
**Primary**:
- `design-class-models/design-model/06-domain-simulation.puml`
  - Challenge, Submission, ScoringEngine classes
  - SimulationService, FeedbackEngine

- `design-class-models/design-model/16-simulation-platform-expanded.puml`
  - Detailed simulation architecture

**What to implement**:
```python
# From 06-domain-simulation.puml
class Challenge(Base):
    id, title, difficulty, flag, hints, ...

class SimulationService:
    get_challenges()
    submit_flag()
    calculate_score()
    provide_feedback()
    sync_to_main_profile()
```

### Sequence Diagrams
**Primary**:
- `sequence-diagrams/04-simulation-practice.puml` - Challenge workflow
- `sequence-diagrams/07-simulation-challenge-flow.puml` - Detailed flow
- `sequence-diagrams/08-sso-navigation-flow.puml` - SSO between platforms

**What to implement**:
- Challenge selection (User → API → SimulationService)
- Flag submission (User → API → Validation → Scoring)
- Profile sync (Learning → Main platform)

### Activity Diagrams
**Primary**:
- `activity-diagrams/04-simulation-learning.puml` - Learning flow

**What to implement**:
- Challenge progression (Beginner → Intermediate → Advanced)
- Feedback generation
- Badge awarding

---

## 📊 PHASE 5: ADVANCED SERVICES (FREQ 29-44, Weeks 20-23)

### Database Diagrams
**Primary**:
- `database-erd/02-engagement-tables.puml` - PTaaS, code review, live events tables

**What to implement**:
```sql
-- From 02-engagement-tables.puml
CREATE TABLE ptaas_engagements (...)
CREATE TABLE code_review_engagements (...)
CREATE TABLE live_events (...)
CREATE TABLE ssdlc_integrations (...)
```

### Design Class Models
**Primary**:
- `design-class-models/design-model/05-domain-ptaas-system.puml`
  - PTaaSEngagement, PTaaSService
  
- `design-class-models/design-model/07-domain-code-review.puml`
  - CodeReviewService
  
- `design-class-models/design-model/08-domain-ssdlc-integration.puml`
  - SSDLCIntegrationService (Jira/GitHub)
  
- `design-class-models/design-model/09-domain-live-events.puml`
  - LiveEventService

- `design-class-models/design-model/14-domain-researcher-matching.puml`
  - BountyMatchService

**What to implement**:
```python
# From design class models
class PTaaSService:
    create_engagement()
    assign_researchers()  # BountyMatch
    track_progress()
    generate_report()

class CodeReviewService:
    create_review()
    scan_dependencies()
    detect_dead_code()
    find_logic_flaws()

class SSDLCIntegrationService:
    integrate_jira()
    integrate_github()
    sync_bidirectional()

class LiveEventService:
    create_event()
    manage_invites()
    track_real_time_metrics()
```

### Sequence Diagrams
**Primary**:
- `sequence-diagrams/05-ptaas-engagement.puml` - PTaaS workflow

**What to implement**:
- PTaaS engagement creation
- Researcher assignment via BountyMatch
- Progress tracking

### Activity Diagrams
**Primary**:
- `activity-diagrams/07-code-review-engagement.puml` - Code review flow
- `activity-diagrams/08-ssdlc-integration.puml` - SSDLC integration
- `activity-diagrams/05-live-hacking-event.puml` - Live event flow
- `activity-diagrams/10-researcher-matching.puml` - BountyMatch algorithm

**What to implement**:
- PTaaS workflow
- Code review process
- SSDLC sync logic
- Live event management
- BountyMatch algorithm

---

## 📊 PHASE 6: AI RED TEAMING (FREQ 45-48, Week 24)

### Database Diagrams
**Primary**:
- `database-erd/02-engagement-tables.puml` - AI Red Teaming tables

**What to implement**:
```sql
-- AI Red Teaming tables
CREATE TABLE ai_engagements (...)
CREATE TABLE ai_vulnerabilities (...)
CREATE TABLE ai_test_cases (...)
```

### Design Class Models
**Primary**:
- `design-class-models/design-model/10-domain-ai-red-teaming.puml`
  - AIEngagement, AIVulnerability classes
  - AIRedTeamService

**What to implement**:
```python
# From 10-domain-ai-red-teaming.puml
class AIRedTeamService:
    create_engagement()
    submit_ai_vulnerability()
    validate_ai_report()
    enforce_ethical_guidelines()
```

### Activity Diagrams
**Primary**:
- `activity-diagrams/09-ai-red-teaming.puml` - AI Red Teaming flow

**What to implement**:
- AI engagement creation
- AI vulnerability reporting
- Ethical compliance checks

---

## 📊 PHASE 7: DEPLOYMENT (Weeks 25-26)

### Architecture Diagrams
**Primary**:
- `deployment-diagram-aws.puml` - AWS infrastructure
- `component-diagram.puml` - Microservices architecture

**What to implement**:
- Terraform modules (VPC, RDS, ElastiCache, ECS, S3)
- Kubernetes manifests
- CI/CD pipeline (GitHub Actions)
- Monitoring (Prometheus, Grafana)

---

## 📋 QUICK REFERENCE BY FREQ

### FREQ-01, FREQ-02 (Authentication)
- Database: `01-core-tables.puml`
- Design: `01-domain-user-management.puml`
- Sequence: `06-staff-provisioning.puml`, `08-sso-navigation-flow.puml`
- Architecture: `authentication-architecture.puml`

### FREQ-03 to FREQ-11 (Bug Bounty)
- Database: `01-core-tables.puml`
- Design: `02-domain-bug-bounty-core.puml`, `03-domain-triage-validation.puml`
- Sequence: `01-bug-report-submission.puml`, `02-triage-validation.puml`
- Activity: `01-bug-report-workflow.puml`, `06-program-creation.puml`

### FREQ-12 to FREQ-22 (Operations)
- Database: `03-communication-analytics.puml`
- Design: `11-domain-communication.puml`, `12-domain-analytics.puml`, `13-domain-audit-logging.puml`, `04-domain-payment-system.puml`
- Sequence: `03-payment-processing.puml`
- Activity: `03-payment-withdrawal.puml`, `12-analytics-reporting.puml`
- Architecture: `dashboard-layouts.puml`

### FREQ-23 to FREQ-28 (Learning)
- Database: `02-engagement-tables.puml`
- Design: `06-domain-simulation.puml`, `16-simulation-platform-expanded.puml`
- Sequence: `04-simulation-practice.puml`, `07-simulation-challenge-flow.puml`
- Activity: `04-simulation-learning.puml`

### FREQ-29 to FREQ-44 (Advanced Services)
- Database: `02-engagement-tables.puml`
- Design: `05-domain-ptaas-system.puml`, `07-domain-code-review.puml`, `08-domain-ssdlc-integration.puml`, `09-domain-live-events.puml`, `14-domain-researcher-matching.puml`
- Sequence: `05-ptaas-engagement.puml`
- Activity: `07-code-review-engagement.puml`, `08-ssdlc-integration.puml`, `05-live-hacking-event.puml`, `10-researcher-matching.puml`

### FREQ-45 to FREQ-48 (AI Red Teaming)
- Database: `02-engagement-tables.puml`
- Design: `10-domain-ai-red-teaming.puml`
- Activity: `09-ai-red-teaming.puml`

---

## 🎯 IMPLEMENTATION WORKFLOW

### For Each FREQ:

1. **Read Database ERD**
   - Understand table structure
   - Identify relationships
   - Note constraints

2. **Read Design Class Model**
   - Understand domain classes
   - Identify services and repositories
   - Note business logic

3. **Read Sequence Diagram**
   - Understand API flow
   - Identify endpoints needed
   - Note request/response

4. **Read Activity Diagram**
   - Understand business process
   - Identify decision points
   - Note state transitions

5. **Implement**
   - Create database tables (from ERD)
   - Create models (from Design Class Model)
   - Create services (from Design Class Model)
   - Create API endpoints (from Sequence Diagram)
   - Implement business logic (from Activity Diagram)

---

## ✅ CHECKLIST

### Before Starting Implementation
- [ ] Read relevant database ERD
- [ ] Read relevant design class model
- [ ] Read relevant sequence diagram
- [ ] Read relevant activity diagram
- [ ] Understand data flow
- [ ] Understand business logic
- [ ] Identify API endpoints needed

### During Implementation
- [ ] Follow database schema from ERD
- [ ] Follow class structure from design model
- [ ] Follow API flow from sequence diagram
- [ ] Follow business logic from activity diagram
- [ ] Test each component

---

**Use this guide to know which diagrams to reference for each implementation phase!**

