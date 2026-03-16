# Analysis Class Model - Modular Diagrams

## Overview
The complete Analysis Class Model has been split into 15 smaller, focused diagrams to avoid rendering issues. Each diagram represents a specific subsystem or module of the Bug Bounty Platform.

## How to Render

### Option 1: Online PlantUML Editor
1. Visit: https://www.plantuml.com/plantuml/uml/
2. Copy the content of any `.puml` file
3. Paste and click "Submit"

### Option 2: VS Code
1. Install "PlantUML" extension
2. Open any `.puml` file
3. Press `Alt+D` to preview

### Option 3: Command Line
```bash
# Install PlantUML first
plantuml *.puml
# This generates PNG images for all diagrams
```

## Module List

### Core System Modules

#### 1. Core User Management (`01-core-user-management.puml`)
**Coverage**: FREQ-01, FREQ-02, UC-01, UC-12
- User (base class)
- Researcher, Organization, TriageSpecialist, FinancialOfficer, Administrator
- KYCVerification, IdentityDocument

#### 2. Organization Types (`02-organization-types.puml`)
**Coverage**: FREQ-03, FREQ-04
- Organization specializations
- AcademicProgram, NonProfitOrganization, FundingAgency, ConsultingAgent, CodeReview

#### 3. Bug Bounty Core (`03-bug-bounty-core.puml`)
**Coverage**: FREQ-03, FREQ-04, FREQ-05, FREQ-06, UC-02, UC-04
- BountyProgram, ProgramScope, RewardTier
- VulnerabilityReport, Attachment
- Core program-report relationships

#### 4. Triage & Validation (`04-triage-validation.puml`)
**Coverage**: FREQ-07, FREQ-08, UC-03
- TriageQueue, ValidationResult, SeverityRating
- Report validation workflow

#### 5. Payment System (`05-payment-system.puml`)
**Coverage**: FREQ-10, FREQ-11, FREQ-20, UC-05
- BountyPayment, PayoutRequest, Transaction, PaymentGateway
- Reward and payout management

### Advanced Features

#### 6. Simulation Environment (`06-simulation-environment.puml`)
**Coverage**: FREQ-23 to FREQ-28, UC-07
- SimulatedEnvironment, SimulationReport
- Learning and practice system

#### 7. PTaaS System (`07-ptaas-system.puml`)
**Coverage**: FREQ-29 to FREQ-40
- PTaaSEngagement, TestingMethodology, RetestRequest
- Penetration Testing as a Service

#### 8. Code Review (`08-code-review.puml`)
**Coverage**: FREQ-41, UC-08
- CodeReviewEngagement, CodeReviewFinding
- Expert code review services

#### 9. SSDLC Integration (`09-ssdlc-integration.puml`)
**Coverage**: FREQ-42, UC-09
- ExternalIntegration, JiraConnector, GitHubConnector, SyncLog
- Jira and GitHub integration

#### 10. Live Hacking Events (`10-live-hacking-events.puml`)
**Coverage**: FREQ-43, FREQ-44, UC-10
- LiveHackingEvent, EventParticipation, EventMetrics
- Time-bound collaborative events

#### 11. AI Red Teaming (`11-ai-red-teaming.puml`)
**Coverage**: FREQ-45 to FREQ-48, UC-11
- AIRedTeamingEngagement, AIVulnerabilityReport, AITestingEnvironment
- AI security testing

### Supporting Systems

#### 12. Communication System (`12-communication-system.puml`)
**Coverage**: FREQ-09, FREQ-12
- Notification, Message, Comment
- User communication and notifications

#### 13. Analytics & Dashboard (`13-analytics-dashboard.puml`)
**Coverage**: FREQ-13, FREQ-15, UC-06
- Dashboard, AnalyticsReport, Metrics
- Role-based dashboards and analytics

#### 14. Audit & Logging (`14-audit-logging.puml`)
**Coverage**: FREQ-17, BR-19
- AuditLog, ActivityLog
- System audit trail and activity tracking

#### 15. Researcher Matching (`15-researcher-matching.puml`)
**Coverage**: FREQ-16, FREQ-32, FREQ-33, FREQ-39, FREQ-40
- BountyMatch, MatchingCriteria
- Intelligent researcher-program matching

## Coverage Summary

### All 48 FREQs Covered ✅
- FREQ-01 to FREQ-22: Core bug bounty features
- FREQ-23 to FREQ-28: Simulation environment
- FREQ-29 to FREQ-40: PTaaS and BountyMatch
- FREQ-41: Expert code review
- FREQ-42: SSDLC integration
- FREQ-43 to FREQ-44: Live hacking events
- FREQ-45 to FREQ-48: AI Red Teaming

### All 12 Use Cases Covered ✅
- UC-01: Register User
- UC-02: Submit Vulnerability Report
- UC-03: Validate Report
- UC-04: Create Bug Bounty Program
- UC-05: Approve Reward
- UC-06: View Dashboard
- UC-07: Practice Vulnerability in Simulation
- UC-08: Perform Expert Code Review
- UC-09: Integrate with SSDLC Tools
- UC-10: Participate in Live Hacking Event
- UC-11: Conduct AI Red Teaming Engagement
- UC-12: Perform Identity Verification (KYC)

## Total Classes: ~50

### By Module:
1. Core User Management: 8 classes
2. Organization Types: 6 classes
3. Bug Bounty Core: 6 classes
4. Triage & Validation: 5 classes
5. Payment System: 6 classes
6. Simulation: 2 classes
7. PTaaS: 4 classes
8. Code Review: 2 classes
9. SSDLC Integration: 5 classes
10. Live Hacking Events: 3 classes
11. AI Red Teaming: 3 classes
12. Communication: 3 classes
13. Analytics: 3 classes
14. Audit & Logging: 2 classes
15. Researcher Matching: 2 classes

## Integration Points

Key classes that appear in multiple diagrams (integration points):
- **User**: Appears in modules 1, 12, 13, 14
- **Researcher**: Appears in modules 1, 3, 6, 7, 8, 10, 11, 15
- **Organization**: Appears in modules 1, 2, 3, 7, 8, 9, 10, 11
- **VulnerabilityReport**: Appears in modules 3, 4, 5, 7, 9, 10, 12
- **BountyMatch**: Appears in modules 7, 11, 15

## Next Steps

1. **Review Each Module**: Render and review each diagram individually
2. **Validate Relationships**: Ensure all relationships make sense
3. **Create Design Class Model**: Add implementation details (data types, method signatures)
4. **Database Design**: Map classes to database tables
5. **Implementation**: Use as blueprint for code structure

## Notes

- These are **Analysis-level** diagrams (conceptual)
- Attributes show basic types
- Methods show key operations
- For **Design-level**, add detailed types and full method signatures

---

**Project**: Bug Bounty and Simulation Platform  
**Team**: Niway Tadesse, Abraham Asimamaw, Melkamu Tesfa  
**Advisor**: Yosef Worku  
**Date**: March 10, 2026
