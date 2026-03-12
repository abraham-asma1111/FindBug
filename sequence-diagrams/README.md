# Sequence Diagrams

This directory contains sequence diagrams for the Bug Bounty and Its Simulation Platform.

**Team:** Niway Tadesse, Abraham Asimamaw, Melkamu Tesfa  
**Advisor:** Yosef Worku

## Overview

Sequence diagrams show the interaction between different components and actors over time for specific use cases. They illustrate the flow of messages and operations in chronological order.

## Diagrams

### 1. Bug Report Submission (`01-bug-report-submission.puml`)
**Purpose:** Shows the complete flow of a researcher submitting a vulnerability report.

**Key Flows:**
- Researcher authentication
- Browsing available bug bounty programs
- Submitting vulnerability report with evidence
- File upload to MinIO storage
- Database transactions
- Notification to organization
- Report status tracking

**Components Involved:**
- Researcher Portal (Next.js)
- Bug Bounty Engine (FastAPI)
- Redis Cache
- MinIO Storage
- PostgreSQL Database
- Notification Service

---

### 2. Triage and Validation (`02-triage-validation.puml`)
**Purpose:** Demonstrates the triage process by analysts and validation by organizations.

**Key Flows:**
- Triage analyst reviews pending reports
- Severity scoring using CVSS and VRT
- Report acceptance or rejection
- Organization validation
- Reward amount assignment
- Dispute handling

**Components Involved:**
- Admin Portal (Next.js)
- Bug Bounty Engine (FastAPI)
- Severity Engine
- PostgreSQL Database
- Notification Service

---

### 3. Payment Processing (`03-payment-processing.puml`)
**Purpose:** Shows the payment workflow from report validation to researcher withdrawal.

**Key Flows:**
- Finance officer batch payment processing
- Wallet credit operations
- Researcher withdrawal requests
- Integration with Ethiopian payment gateways (Telebirr, CBE Birr)
- Transaction history tracking
- Async payment processing with Celery

**Components Involved:**
- Finance Portal (Next.js)
- Reward Service (FastAPI)
- Wallet Service
- Celery Workers
- Payment Gateway (Telebirr/CBE)
- PostgreSQL Database
- Notification Service

---

### 4. Simulation Practice Mode (`04-simulation-practice.puml`)
**Purpose:** Illustrates the isolated simulation environment for researcher training.

**Key Flows:**
- Accessing practice challenges
- Starting vulnerable application instances (OWASP Juice Shop)
- Exploiting vulnerabilities in safe environment
- Hint system usage
- Submission and scoring
- Progress tracking and leaderboard
- Challenge unlocking system

**Components Involved:**
- Simulation Interface (Next.js)
- Simulation Engine (FastAPI)
- Vulnerable Applications (OWASP Juice Shop)
- Feedback Engine
- Simulation Database (Isolated)
- Notification Service

**Note:** This system is completely isolated from production data and payments.

---

### 5. PTaaS Engagement (`05-ptaas-engagement.puml`)
**Purpose:** Shows the Penetration Testing as a Service workflow.

**Key Flows:**
- Organization creates PTaaS engagement
- Researcher matching based on skills
- Engagement acceptance
- Penetration testing execution
- Finding submission during testing
- Final report generation
- Organization review and payment

**Components Involved:**
- Organization Portal (Next.js)
- PTaaS Engine (FastAPI)
- BountyMatch Engine
- PostgreSQL Database
- MinIO Storage
- Notification Service

---

## Common Patterns

### Authentication Flow
All user interactions start with JWT-based authentication:
1. User provides credentials
2. System verifies against database
3. JWT token stored in Redis
4. Token used for subsequent requests

### Caching Strategy
Redis caching is used throughout:
- Cache frequently accessed data (programs, reports)
- Cache invalidation on updates
- Session management
- Rate limiting

### Async Processing
Celery workers handle background tasks:
- Email/SMS notifications
- Payment processing
- Report generation
- External API integrations

### Transaction Management
Database operations use transactions:
- BEGIN TRANSACTION
- Multiple related operations
- COMMIT or ROLLBACK
- Ensures data consistency

### File Storage
MinIO (local) / S3 (production):
- Evidence files (screenshots, videos)
- Generated reports (PDF)
- S3-compatible API
- Secure file access

### Notification System
Multi-channel notifications:
- Email (SMTP)
- SMS (Twilio)
- In-app notifications
- Real-time updates via WebSocket

## Technology Stack

- **Frontend:** Next.js (React)
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL with JSONB
- **Cache:** Redis
- **Queue:** Celery with Redis broker
- **Storage:** MinIO (local) / AWS S3 (production)
- **Payments:** Telebirr, CBE Birr (Ethiopian gateways)

## Viewing the Diagrams

To render these PlantUML diagrams:

1. **Online:** Use [PlantUML Online Server](http://www.plantuml.com/plantuml/uml/)
2. **VS Code:** Install PlantUML extension
3. **Command Line:** Use PlantUML JAR with Java
4. **Docker:** Use official PlantUML Docker image

```bash
# Example: Generate PNG from PlantUML
java -jar plantuml.jar sequence-diagrams/*.puml
```

## Notes

- All diagrams follow UML 2.0 sequence diagram notation
- Error handling and alternative flows are shown using `alt/else` blocks
- Loops are shown using `loop` blocks
- Database transactions are explicitly marked
- Async operations are clearly indicated
- Ethiopian payment integration is highlighted
- Simulation isolation is emphasized
