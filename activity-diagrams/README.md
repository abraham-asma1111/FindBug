# Activity Diagrams

This directory contains activity diagrams for the Bug Bounty and Its Simulation Platform.

**Team:** Niway Tadesse, Abraham Asimamaw, Melkamu Tesfa  
**Advisor:** Yosef Worku

## Overview

Activity diagrams model business processes and workflows, showing the flow of control from activity to activity. They illustrate decision points, parallel processing, and the sequence of actions across different actors/swimlanes.

## Diagrams

### 1. Bug Report Workflow (`01-bug-report-workflow.puml`)
**Purpose:** Shows the complete end-to-end workflow from report submission to payment.

**Key Activities:**
- Researcher submits vulnerability report
- System validates and stores submission
- Triage analyst reviews and scores
- Organization validates and sets reward
- Finance officer processes payment
- Researcher receives funds

**Decision Points:**
- Eligibility check
- Valid vulnerability?
- Accept or dispute?

**Swimlanes:** Researcher, System, Triage Analyst, Organization, Finance Officer

---

### 2. Researcher Onboarding (`02-researcher-onboarding.puml`)
**Purpose:** Demonstrates the registration and KYC verification process.

**Key Activities:**
- User registration with email verification
- KYC document submission
- Admin manual review
- Account approval/rejection
- Profile completion
- Platform access enablement

**Decision Points:**
- Valid registration data?
- Documents valid?
- Resubmit after rejection?

**Swimlanes:** Researcher, System, Admin

---

### 3. Payment and Withdrawal (`03-payment-withdrawal.puml`)
**Purpose:** Shows payment processing and researcher withdrawal workflow.

**Key Activities:**
- Finance officer batch payment approval
- Wallet credit operations
- Researcher withdrawal request
- Payment gateway integration
- Success/failure handling
- Refund on failure

**Decision Points:**
- Reports ready for payment?
- Sufficient balance?
- Meets minimum amount?
- Transfer successful?
- Retry on failure?

**Parallel Processing:**
- Update report status
- Credit wallets
- Create transactions
- Send notifications

**Swimlanes:** Finance Officer, System, Researcher, Celery Worker, Payment Gateway

**Integration:** Telebirr, CBE Birr payment gateways

---

### 4. Simulation Learning Path (`04-simulation-learning.puml`)
**Purpose:** Illustrates the practice mode learning workflow.

**Key Activities:**
- Challenge selection based on skill level
- Vulnerable instance deployment (OWASP Juice Shop)
- Vulnerability exploitation
- Hint system usage
- Solution submission and scoring
- Progress tracking and level unlocking

**Decision Points:**
- Beginner or advanced level?
- Advanced challenges unlocked?
- Need hint?
- Hints available?
- Vulnerability found?
- Score >= 70%?
- Retry or try different challenge?
- Unlock criteria met?

**Loops:**
- Repeat exploit attempts until successful
- Continue with more challenges

**Swimlanes:** Researcher, System

**Note:** Completely isolated from production system

---

### 5. Live Hacking Event (`05-live-hacking-event.puml`)
**Purpose:** Shows the complete live event lifecycle.

**Key Activities:**
- Organization creates and publishes event
- Researchers register for participation
- Event activation at scheduled time
- Real-time vulnerability hunting
- Live leaderboard updates
- Duplicate detection (first submission wins)
- Final review and scoring
- Winner announcement and rewards

**Decision Points:**
- Researcher eligible?
- Event started?
- Duplicate submission?
- Event still active?
- Won prize?

**Parallel Processing:**
- Validate findings
- Calculate scores
- Identify winners

**Swimlanes:** Organization, System, Researcher, Triage Team

**Special Features:**
- Real-time leaderboard
- Countdown timer
- Duplicate detection
- Quick triage during event

---

### 6. Program Creation (`06-program-creation.puml`)
**Purpose:** Shows how organizations create bug bounty programs.

**Key Activities:**
- Program details configuration
- Scope definition (in-scope/out-of-scope)
- Reward tier setup
- Eligibility criteria
- Program rules and policies
- Asset upload
- Publish or save as draft

**Decision Points:**
- Valid data?
- Publish now or save draft?
- Researcher interested and eligible?

**Swimlanes:** Organization, System, Researcher

---

### 7. Code Review Engagement (`07-code-review-engagement.puml`)
**Purpose:** Expert code review workflow.

**Key Activities:**
- Organization requests code review
- Source code upload
- Expert reviewer matching
- Code analysis and issue identification
- Finding documentation
- Report generation
- Payment processing

**Decision Points:**
- Accept engagement?
- Issue found?
- More code to review?
- Satisfied with review?
- Request clarification?

**Loops:**
- Review code sections iteratively

**Swimlanes:** Organization, System, Expert Reviewer

---

### 8. SSDLC Integration (`08-ssdlc-integration.puml`)
**Purpose:** Integration with Jira and GitHub for DevSecOps.

**Key Activities:**
- Configure integration (Jira/GitHub)
- Test connection
- Auto-sync vulnerability reports
- Create issues automatically
- Webhook-based status updates
- Manual sync option
- Bidirectional synchronization

**Decision Points:**
- Integration type (Jira/GitHub)?
- Connection successful?
- Auto-sync enabled?
- Valid webhook?
- Report found?
- Integration active?

**Swimlanes:** Organization, System, Celery Worker, Jira/GitHub

**Special Features:**
- OAuth authentication
- Webhook validation
- Field mapping
- Evidence attachment

---

### 9. AI Red Teaming (`09-ai-red-teaming.puml`)
**Purpose:** AI security testing engagement workflow.

**Key Activities:**
- AI system assessment request
- Expert matching for AI security
- Attack vector execution (prompt injection, jailbreaking, etc.)
- AI vulnerability documentation
- Retest after fixes
- Payment processing

**Decision Points:**
- Accept engagement?
- Vulnerability found?
- Testing complete?
- Request retest?

**Attack Types:**
- Prompt injection
- Jailbreaking
- Data poisoning
- Model inversion
- Adversarial examples
- Bias exploitation

**Swimlanes:** Organization, System, AI Security Expert

---

### 10. Researcher Matching (`10-researcher-matching.puml`)
**Purpose:** BountyMatch intelligent matching algorithm.

**Key Activities:**
- Extract matching criteria
- Multi-factor filtering (skills, reputation, availability, performance)
- Score calculation
- Researcher ranking
- Invitation sending
- Acceptance tracking
- Learning and optimization

**Decision Points:**
- Matches found?
- Researcher interested?
- Enough researchers?
- More candidates?
- Retry matching?

**Parallel Processing:**
- Filter by skills
- Filter by reputation
- Filter by availability
- Filter by performance

**Matching Score Formula:**
- Skills (40%)
- Reputation (30%)
- Availability (20%)
- Performance (10%)

**Swimlanes:** Organization, System, Researcher

---

### 11. Dispute Resolution (`11-dispute-resolution.puml`)
**Purpose:** Handling disputes between organizations and researchers.

**Key Activities:**
- Organization disputes report
- Evidence collection from both parties
- Triage analyst mediation
- Admin escalation for complex cases
- Final decision and reasoning
- Status update and notification

**Decision Points:**
- Clear resolution?
- Decision favor?
- Accept decision?
- Need more info?

**Swimlanes:** Organization, Researcher, Triage Analyst, Admin, System

**Escalation Path:**
1. Triage Analyst (first level)
2. Admin (complex cases)
3. External experts (if needed)

---

### 12. Analytics and Reporting (`12-analytics-reporting.puml`)
**Purpose:** Dashboard analytics and custom report generation.

**Key Activities:**
- Role-based dashboard views
- KPI calculation
- Custom report generation
- Export in multiple formats (PDF, Excel, CSV, API)
- Scheduled reports
- Background job processing for large datasets

**Decision Points:**
- User role (Researcher/Organization/Admin)?
- Report type (Standard/Custom)?
- Large dataset?
- Export format?
- Time to generate scheduled report?

**Parallel Processing:**
- Query multiple data sources
- Calculate various metrics
- Generate visualizations

**Swimlanes:** User, System, Celery Worker, Celery Beat

**Metrics by Role:**
- **Researcher:** Reports, earnings, reputation, skills
- **Organization:** Programs, vulnerabilities, ROI, MTTR
- **Admin:** Platform stats, user growth, revenue, system health

---

## Activity Diagram Elements

### Swimlanes
Represent different actors or systems:
- **Researcher** - Security researchers/ethical hackers
- **Organization** - Companies using the platform
- **System** - Automated platform operations
- **Triage Analyst** - Report reviewers
- **Finance Officer** - Payment approvers
- **Admin** - Platform administrators
- **Celery Worker** - Background task processor
- **Payment Gateway** - External payment services

### Decision Points (Diamond)
- Conditional branching based on criteria
- Yes/No or multiple choice paths
- Examples: "Valid data?", "Eligible?", "Score >= 70?"

### Parallel Processing (Fork/Join)
- Activities that happen simultaneously
- Fork: Split into parallel paths
- Join: Merge parallel paths
- Example: Batch payment processing

### Loops (Repeat)
- Iterative activities
- Continue until condition met
- Example: Retry exploit until successful

### Notes
- Additional context or explanations
- Clarify business rules
- Highlight important constraints

## Common Patterns

### Validation Pattern
```
:Submit Data;
|System|
:Validate Input;
if (Valid?) then (yes)
  :Process;
else (no)
  :Show Error;
  stop
endif
```

### Approval Pattern
```
:Submit Request;
|Approver|
:Review Request;
if (Approve?) then (yes)
  :Process Request;
else (no)
  :Reject with Reason;
endif
```

### Retry Pattern
```
:Attempt Operation;
if (Success?) then (yes)
  :Continue;
else (no)
  if (Retry?) then (yes)
    :Attempt Again;
  else (no)
    :Give Up;
  endif
endif
```

### Notification Pattern
```
fork
  :Main Operation;
fork again
  :Send Notification;
end fork
```

## Business Rules Illustrated

1. **KYC Requirement** - Users must complete KYC before full access
2. **Eligibility Check** - Researchers must meet program criteria
3. **First Submission Wins** - Duplicate detection in live events
4. **Minimum Withdrawal** - Withdrawal amount constraints
5. **Hint Limits** - Maximum 3 hints per simulation challenge
6. **Score Threshold** - 70% minimum to pass simulation
7. **Level Unlocking** - Progressive challenge access
8. **Payment Approval** - Finance officer must approve payments

## Technology Integration

- **MinIO/S3** - File storage for evidence and documents
- **Redis** - Caching and session management
- **Celery** - Async task processing
- **PostgreSQL** - Data persistence
- **Payment Gateways** - Telebirr, CBE Birr integration
- **OWASP Juice Shop** - Vulnerable application for practice

## Viewing the Diagrams

To render these PlantUML diagrams:

1. **Online:** [PlantUML Online Server](http://www.plantuml.com/plantuml/uml/)
2. **VS Code:** Install PlantUML extension
3. **Command Line:** 
```bash
java -jar plantuml.jar activity-diagrams/*.puml
```

## Differences from Sequence Diagrams

| Aspect | Activity Diagram | Sequence Diagram |
|--------|-----------------|------------------|
| Focus | Business process flow | Component interactions |
| Time | Implicit | Explicit timeline |
| Actors | Swimlanes | Lifelines |
| Purpose | Workflow logic | Message exchange |
| Decisions | Prominent | Less common |
| Loops | Explicit | Less common |

## Notes

- Activity diagrams complement sequence diagrams
- Focus on business logic and decision flow
- Show parallel processing capabilities
- Illustrate error handling and retry logic
- Demonstrate Ethiopian payment integration
- Emphasize simulation system isolation
- Highlight real-time features (live events, leaderboards)

---

**Created**: 2026-03-11  
**Version**: 1.0  
**Format**: PlantUML Activity Diagram (UML 2.0)
