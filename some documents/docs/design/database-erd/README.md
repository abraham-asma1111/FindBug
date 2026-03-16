# Database ERD Diagrams

**Project**: Bug Bounty and Its Simulation Platform  
**Database**: PostgreSQL  

## Overview

The database schema is split into multiple ERD diagrams to prevent rendering issues and ensure all content is visible.

## ERD Files

### 1. Core Tables (`01-core-tables.puml`)
**Tables**: 8 tables
- User Management: users, researchers, organizations
- Bug Bounty: bounty_programs, vulnerability_reports
- Payments: bounty_payments, researcher_balances

**Purpose**: Shows the core platform entities and their relationships

---

### 2. Engagement Tables (`02-engagement-tables.puml`)
**Tables**: 8 tables
- PTaaS: ptaas_engagements, retest_requests
- Code Review: code_review_engagements, code_review_findings
- AI Red Teaming: ai_red_teaming_engagements, ai_vulnerability_reports
- Live Events: live_hacking_events, event_participations

**Purpose**: Shows all engagement types (PTaaS, Code Review, AI, Events)

---

### 3. Communication & Analytics (`03-communication-analytics.puml`)
**Tables**: 7 tables
- Communication: notifications, messages, comments, webhook_endpoints
- Analytics: researcher_metrics, organization_metrics, platform_metrics

**Purpose**: Shows notification system and metrics tracking

---

### 4. Main ERD (`../database-schema-erd.puml`)
**Tables**: Core tables with full details
- All user management tables
- All bug bounty core tables
- All triage and payment tables
- Complete relationships

**Purpose**: Comprehensive view of core database schema

---

## Complete Table List (50+ tables)

### User Management (6)
- users
- researchers
- organizations
- triage_specialists
- administrators
- kyc_verifications

### Bug Bounty Core (7)
- bounty_programs
- program_scopes
- reward_tiers
- vulnerability_reports
- attachments
- comments
- program_invitations

### Triage & Validation (2)
- triage_queue
- validation_results

### Payment System (4)
- bounty_payments
- researcher_balances
- payout_requests
- transactions

### PTaaS (2)
- ptaas_engagements
- retest_requests

### Simulation (2)
- simulated_environments
- simulation_sessions

### Code Review (2)
- code_review_engagements
- code_review_findings

### Live Events (2)
- live_hacking_events
- event_participations

### AI Red Teaming (2)
- ai_red_teaming_engagements
- ai_vulnerability_reports

### Communication (4)
- notifications
- notification_preferences
- messages
- webhook_endpoints

### Analytics (4)
- researcher_metrics
- organization_metrics
- platform_metrics
- analytics_reports

### Audit & Logging (3)
- audit_logs
- security_events
- login_history

### Researcher Matching (5)
- matching_requests
- match_results
- researcher_profiles
- skill_tags
- researcher_skills

### SSDLC Integration (2)
- external_integrations
- sync_logs

---

## Viewing the Diagrams

### Online
1. Visit: https://www.plantuml.com/plantuml/uml/
2. Copy content from any .puml file
3. Paste and render

### VS Code
1. Install "PlantUML" extension
2. Open any .puml file
3. Press Alt+D to preview

### Command Line
```bash
cd database-erd
plantuml *.puml
# Generates PNG images
```

---

## Why Multiple Files?

Large ERD diagrams with 50+ tables can have rendering issues:
- Content hidden on sides
- Difficult to read
- Slow to render

By splitting into logical groups:
- ✅ All content visible
- ✅ Easier to understand
- ✅ Faster rendering
- ✅ Better for documentation

---

## Full Schema Documentation

See `../database-schema-README.md` for:
- Complete table descriptions
- Index strategy
- Constraints and triggers
- Sample queries
- Migration strategy
- Performance tuning

---

**Created**: March 12, 2026  
**Status**: Complete - 50+ tables across 4 ERD diagrams

