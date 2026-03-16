# Use Case Diagrams
## Bug Bounty and Its Simulation Platform

This directory contains use case diagrams showing all actors and their interactions with the platform.

---

## Diagram Files

### 1. Complete Use Case Diagram
**File**: `../use-case-diagram.puml`

Comprehensive overview showing all actors and their use cases in a single diagram:
- 6 actor types
- 47+ use cases
- External system integrations
- Include/extend relationships

### 2. Researcher Use Cases
**File**: `01-researcher-use-cases.puml`

Detailed use cases for security researchers:
- Account registration and KYC
- Bug hunting activities
- Report submission and tracking
- Rewards and withdrawals
- Live events and PTaaS participation
- Reputation and ranking

**Total Use Cases**: 26

### 3. Organization Use Cases
**File**: `02-organization-use-cases.puml`

Detailed use cases for organizations:
- Program creation and management
- Report review and approval
- Team management
- Advanced services (PTaaS, Code Review, AI Red Teaming)
- Analytics and reporting
- Financial management

**Total Use Cases**: 37

### 4. Staff Use Cases
**File**: `03-staff-use-cases.puml`

Detailed use cases for platform staff:

**Administrator**:
- Staff provisioning
- User management
- System configuration
- Dispute resolution
- Audit logs

**Triage Specialist**:
- Report validation
- Severity assignment
- Duplicate detection
- Triage queue management

**Financial Officer**:
- Payment approval
- Payout processing
- KYC verification
- Financial reporting

**Support Staff**:
- Ticket management
- User assistance
- Documentation
- Issue escalation

**Total Use Cases**: 40

### 5. Learning Platform Use Cases
**File**: `04-learning-platform-use-cases.puml`

Detailed use cases for the learning/simulation platform:

**Learner**:
- SSO authentication
- Learning paths
- Practice challenges
- Achievements and gamification
- Community features

**Instructor** (Admin):
- Content creation
- Challenge management
- Analytics

**Challenge Categories**:
- Web Application Security
- API Security
- Mobile Security
- Network Security
- Cloud Security
- Cryptography

**Total Use Cases**: 39

---

## Actor Summary

### Primary Actors (External Users)

1. **Researcher**
   - Security researchers and ethical hackers
   - Find and report vulnerabilities
   - Earn rewards and reputation
   - Access: Public registration + KYC

2. **Organization**
   - Companies running bug bounty programs
   - Review and reward vulnerability reports
   - Manage security programs
   - Access: Public registration + company verification

3. **Learner**
   - Any user accessing the learning platform
   - Can be researcher, organization member, or staff
   - Practice security skills in safe environment
   - Access: SSO from main platform

### Secondary Actors (Platform Staff)

4. **Administrator**
   - Platform super admin
   - Full system access and control
   - Staff provisioning and management
   - Access: Internal provisioning only

5. **Triage Specialist**
   - Validates vulnerability reports
   - Assigns severity levels
   - Detects duplicates
   - Access: Internal provisioning only

6. **Financial Officer**
   - Manages payments and payouts
   - Verifies KYC documents
   - Handles financial operations
   - Access: Internal provisioning only

7. **Support Staff**
   - Provides user support
   - Assists with onboarding
   - Manages documentation
   - Access: Internal provisioning only

### External Systems

- **Payment Gateway** (Chapa/Telebirr)
- **Email Service** (SendGrid)
- **SMS Service** (Twilio)

---

## Use Case Relationships

### Include Relationship (<<include>>)
Indicates a use case that is always part of another use case.

Examples:
- "Submit Report" includes "Browse Programs"
- "Approve Payment" includes "Review Payment Request"
- "Provision Staff" includes "Manage Users"

### Extend Relationship (<<extend>>)
Indicates optional behavior that extends a base use case.

Examples:
- "Complete KYC" extends "Register Account"
- "Enable MFA" extends "Login"
- "Participate in Live Event" extends "Browse Programs"

---

## Use Case Categories

### Authentication & Authorization
- Registration
- Login/Logout
- KYC verification
- MFA setup
- SSO authentication

### Bug Bounty Core
- Program management
- Report submission
- Triage and validation
- Reward approval
- Payment processing

### Advanced Services
- PTaaS engagements
- Code review
- AI red teaming
- Live hacking events
- SSDLC integration

### Learning Platform
- Simulation challenges
- Learning paths
- Achievements
- Community features
- Content management

### Administration
- User management
- Staff provisioning
- System configuration
- Audit logging
- Dispute resolution

### Financial Operations
- Payment approval
- Payout processing
- KYC verification
- Financial reporting
- Budget management

### Communication
- Messaging
- Notifications
- Announcements
- Support tickets

---

## Coverage Analysis

### Functional Requirements Coverage

These use case diagrams cover all 48 FREQs from the original requirements:

✅ **User Management** (FREQ 1-5): Registration, authentication, profiles, KYC
✅ **Bug Bounty Core** (FREQ 6-15): Programs, reports, triage, rewards
✅ **Payment System** (FREQ 16-20): Payments, withdrawals, Ethiopian gateways
✅ **PTaaS** (FREQ 21-25): Engagements, assessments, reporting
✅ **Simulation** (FREQ 26-30): Challenges, practice, gamification
✅ **Code Review** (FREQ 31-33): Review requests, feedback
✅ **SSDLC** (FREQ 34-36): Tool integration, automation
✅ **Live Events** (FREQ 37-39): Event hosting, participation
✅ **AI Red Teaming** (FREQ 40-42): AI-powered testing
✅ **Communication** (FREQ 43-45): Messaging, notifications
✅ **Analytics** (FREQ 46-47): Dashboards, reports
✅ **Audit Logging** (FREQ 48): Activity tracking

---

## Multi-Platform Architecture

The use case diagrams reflect the multi-platform architecture:

### Main Platform Portals
1. **Researcher Portal** - UC1-UC26 (Researcher use cases)
2. **Organization Portal** - UC1-UC37 (Organization use cases)
3. **Admin Portal** - UC1-UC40 (Staff use cases)

### Learning Platform
4. **Learning Portal** - UC1-UC39 (Learning use cases)
   - Separate full-stack module
   - SSO authentication from main platform
   - Isolated simulation environment

### Single Sign-On (SSO)
- Users authenticate once on main platform
- Can access learning platform without re-login
- Same user account, different dashboards
- Role-based access control maintained

---

## Rendering Instructions

To render these diagrams:

### Online
Visit: http://www.plantuml.com/plantuml/uml/

### Local (Recommended)
```bash
# Install PlantUML
java -jar plantuml.jar use-case-diagram.puml

# Or render all
java -jar plantuml.jar use-case-diagrams/*.puml
```

### VS Code
1. Install PlantUML extension
2. Open .puml file
3. Press Alt+D to preview

---

## Notes

- All use cases are derived from the 48 functional requirements (FREQs)
- Staff provisioning follows internal employee provisioning model (Option 3)
- Learning platform is designed as a separate module with SSO
- External system integrations are clearly marked
- Include/extend relationships show dependencies between use cases

---

**Last Updated**: March 13, 2026
**Team**: Niway Tadesse, Abraham Asimamaw, Melkamu Tesfa
**Advisor**: Yosef Worku
