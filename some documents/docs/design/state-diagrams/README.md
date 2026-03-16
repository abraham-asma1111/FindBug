# State Diagrams

This directory contains state diagrams for the Bug Bounty and Its Simulation Platform.

**Team:** Niway Tadesse, Abraham Asimamaw, Melkamu Tesfa  
**Advisor:** Yosef Worku

## Overview

State diagrams model the lifecycle and state transitions of key entities in the system. They show all possible states an entity can be in and the events that cause transitions between states.

## Diagrams

### 1. Vulnerability Report States (`01-vulnerability-report-states.puml`)
**Purpose:** Shows the complete lifecycle of a vulnerability report from submission to closure.

**States:**
- Draft → Submitted → Pending_Triage → In_Review → Triaged → Pending_Validation → Validated → Pending_Payment → Paid → Closed
- Alternative paths: Rejected, Duplicate, Disputed, Mediation

**Key Transitions:**
- Automatic duplicate detection
- Triage analyst review
- Organization validation
- Dispute resolution
- Payment processing

---

### 2. Payment States (`02-payment-states.puml`)
**Purpose:** Models payment processing from approval to completion.

**States:**
- Pending → Approved → Processing → Completed → Wallet_Credited
- Alternative paths: On_Hold, Failed, Retry_Pending, Cancelled

**Key Transitions:**
- Finance approval
- Gateway processing (Telebirr, CBE Birr)
- Retry mechanism for failures
- Transaction logging

---

### 3. Program States (`03-program-states.puml`)
**Purpose:** Bug bounty program lifecycle management.

**States:**
- Draft → Review → Active → Paused/Closed → Archived

**Key Transitions:**
- Admin approval
- Temporary suspension
- Program closure
- Archival after 90 days

---

### 4. User Account States (`04-user-account-states.puml`)
**Purpose:** User account lifecycle from registration to various end states.

**States:**
- Unverified → Email_Verified → Pending_KYC → KYC_Review → Active
- Alternative paths: Limited_Access, Suspended, Locked, Inactive, Banned, Archived

**Key Transitions:**
- Email verification
- KYC approval/rejection
- Policy violations
- Security issues
- Inactivity timeouts

---

### 5. PTaaS Engagement States (`05-ptaas-engagement-states.puml`)
**Purpose:** Penetration testing engagement workflow.

**States:**
- Draft → Published → Inviting → Assigned → In_Progress → Testing → Reporting → Review → Completed → Payment_Pending → Paid → Closed
- Alternative paths: Cancelled, Retest_Required

**Key Transitions:**
- Researcher invitation and acceptance
- Testing phases
- Report submission and review
- Retest cycles
- Payment processing

---

### 6. Withdrawal States (`06-withdrawal-states.puml`)
**Purpose:** Researcher fund withdrawal process.

**States:**
- Initiated → Validating → Approved → Processing → Gateway_Pending → Completed
- Alternative paths: Rejected, Failed, Retry_Scheduled, Refunded

**Key Transitions:**
- Balance and limit validation
- Payment gateway integration
- Retry mechanism
- Refund on failure

---

### 7. Simulation Challenge States (`07-simulation-challenge-states.puml`)
**Purpose:** Practice challenge lifecycle in simulation environment.

**States:**
- Available → Started → In_Progress → Submitted → Evaluating → Passed/Failed → Completed
- Alternative paths: Paused, Retry_Available, Abandoned

**Key Transitions:**
- Challenge start and instance deployment
- Pause/resume functionality
- Auto-grading (70% pass threshold)
- Retry mechanism
- Points and badge rewards

---

### 8. Live Event States (`08-live-event-states.puml`)
**Purpose:** Live hacking event management.

**States:**
- Draft → Published → Registration_Open → Registration_Closed → Active → In_Progress → Ending_Soon → Ended → Under_Review → Results_Published → Payment_Processing → Completed → Archived

**Key Transitions:**
- Registration management
- Event timing
- Real-time hacking phase
- Results and winner announcement
- Reward distribution

---

### 9. Code Review States (`09-code-review-states.puml`)
**Purpose:** Code review engagement workflow.

**States:**
- Draft → Published → Inviting → Assigned → In_Progress → Reviewing → Findings_Submitted → Report_Draft → Report_Submitted → Under_Review → Approved → Payment_Pending → Paid → Closed
- Alternative paths: Clarification_Needed, Cancelled

**Key Transitions:**
- Expert invitation and acceptance
- Code analysis phases
- Finding documentation
- Report review and clarification
- Payment processing

---

### 10. AI Red Teaming States (`10-ai-red-teaming-states.puml`)
**Purpose:** AI security testing engagement lifecycle.

**States:**
- Draft → Published → Inviting → Assigned → In_Progress → Testing → Vulnerability_Found/No_Issues → Documenting → Report_Draft → Report_Submitted → Under_Review → Validated → Fixing → Retest_Requested → Retesting → Retest_Passed/Retest_Failed → Approved → Payment_Pending → Paid → Closed
- Alternative paths: Clarification_Needed, Cancelled

**Key Transitions:**
- AI security expert matching
- Attack execution (prompt injection, jailbreaking, etc.)
- Vulnerability documentation
- Retest cycles (max 3 rounds)
- Payment processing

**Attack Types:**
- Prompt injection
- Jailbreaking
- Data poisoning
- Model inversion
- Adversarial examples
- Bias exploitation

---

### 11. Dispute Resolution States (`11-dispute-resolution-states.puml`)
**Purpose:** Handling disputes between organizations and researchers.

**States:**
- Initiated → Evidence_Collection → Researcher_Response → Organization_Counter → Under_Mediation → Triage_Review → Decision_Made → Resolved_Favor_Researcher/Resolved_Favor_Organization → Closed
- Escalation path: Escalated → Admin_Review → Expert_Consultation → Final_Decision → Closed
- Appeal path: Researcher_Appeal → Escalated

**Key Transitions:**
- Evidence collection (3 days per party)
- Triage analyst mediation
- Admin escalation for complex cases
- Final binding decision

**Escalation Criteria:**
- High-value disputes (>$5000)
- Complex technical issues
- Conflicting evidence
- Policy interpretation needed

---

### 12. KYC Verification States (`12-kyc-verification-states.puml`)
**Purpose:** Know Your Customer verification lifecycle.

**States:**
- Not_Started → Documents_Pending → Documents_Submitted → Under_Review → Approved → Active
- Alternative paths: Additional_Info_Required, Rejected, Permanently_Rejected, Expired, Under_Reverification, Suspended

**Key Transitions:**
- Document submission (ID, proof of address, selfie)
- Manual admin review (24-48 hours)
- Approval/rejection with retry (max 3 attempts)
- Annual renewal (365 days validity)
- Reverification on suspicious activity

**Benefits of Approved KYC:**
- Full platform access
- Withdrawal enabled
- Higher withdrawal limits
- Private program participation

---

## State Diagram Notation

### States
- **Rounded rectangles** - Regular states
- **[*]** - Initial/final pseudo-states
- **State names** - Use underscore for multi-word states

### Transitions
- **Arrows** - State transitions
- **Labels** - Events/conditions causing transition
- **Notes** - Additional context and business rules

### Common Patterns

#### Happy Path
The main flow through the system:
```
[*] → State1 → State2 → State3 → [*]
```

#### Alternative Paths
Error handling and edge cases:
```
State1 → Error_State → [*]
State1 → Retry_State → State1
```

#### Loops
Repeatable transitions:
```
State1 → State2 → State1 (retry)
```

## Business Rules Illustrated

### Timeouts
- Unverified accounts expire after 7 days
- Inactive accounts after 180 days
- Archived accounts after 365 days
- Programs archived after 90 days of closure

### Validation
- KYC required for full access
- Balance checks before withdrawal
- Minimum withdrawal amounts
- Daily/monthly limits

### Retry Mechanisms
- Payment failures: auto-retry with max attempts
- Withdrawal failures: refund to wallet
- Challenge failures: retry allowed

### Approval Workflows
- Program creation requires admin approval
- Payments require finance officer approval
- KYC requires manual review

## Integration Points

### Payment Gateways
- Telebirr (Ethiopian mobile money)
- CBE Birr (Ethiopian digital wallet)
- Bank transfers

### External Systems
- Email verification
- SMS notifications
- Webhook callbacks

## Viewing the Diagrams

To render these PlantUML diagrams:

1. **Online:** [PlantUML Online Server](http://www.plantuml.com/plantuml/uml/)
2. **VS Code:** Install PlantUML extension
3. **Command Line:**
```bash
java -jar plantuml.jar state-diagrams/*.puml
```

## Notes

- State diagrams complement activity diagrams
- Focus on entity lifecycle, not process flow
- Show all possible states and transitions
- Include error states and recovery paths
- Document business rules in notes

---

**Created**: 2026-03-12  
**Version**: 1.0  
**Format**: PlantUML State Diagram (UML 2.0)
