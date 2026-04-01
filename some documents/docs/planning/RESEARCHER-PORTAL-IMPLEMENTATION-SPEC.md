# Researcher Portal Implementation Specification
## Final Sidebar, Dashboard Architecture, and Workflow Model

Date: 2026-03-31

## 1. Purpose

This document converts the agreed researcher portal direction into an implementation-ready frontend specification.

It merges:
- the platform RAD and FREQ scope
- the researcher use cases and dashboard diagrams
- the agreed portal navigation model
- the pasted researcher dashboard image
- the previously reviewed workflow patterns from major bug bounty platforms

This document is the source of truth for the researcher portal UI architecture.

## 2. Source Basis

Primary internal sources:
- `some documents/docs/planning/FRONTEND-PORTAL-NAVIGATION-AGREEMENT.md`
- `some documents/docs/design/dashboard-layouts.puml`
- `some documents/docs/design/use-case-diagrams/01-researcher-use-cases.puml`
- `some documents/docs/design/sequence-diagrams/01-bug-report-submission.puml`
- `some documents/docs/design/sequence-diagrams/03-payment-processing.puml`
- `some documents/docs/design/sequence-diagrams/04-simulation-practice.puml`
- `some documents/docs/design/design-class-models/design-model/14-domain-researcher-matching.puml`
- `some documents/docs/design/design-class-models/design-model/12-domain-analytics.puml`
- `some documents/researcher one.png`

External benchmark influence already reviewed earlier:
- HackerOne researcher dashboard, reputation, leaderboard, report states, and payments
- Intigriti submission handling, payouts, and retests
- YesWeHack public program discovery and light-theme visual language

## 3. Design Conclusion From The Researcher Image

The image provides a good dashboard skeleton, but not a complete researcher portal.

Keep from the image:
- left sidebar
- KPI summary row
- central workbench card
- right-side insight card
- strong quick actions
- dense operator-style dashboard layout

Do not keep from the image as-is:
- incomplete sidebar
- mixed content in the right rail
- weak analytics coverage
- program-only mental model
- dark visual style as the default

Final styling direction:
- use the image for layout density and block proportions
- use the YesWeHack-inspired warm light theme for the default appearance
- support dark mode through theme tokens only

## 4. Final Researcher Sidebar

The researcher sidebar is fixed as:

- `Dashboard`
- `Engagements`
- `Reports`
- `Earnings`
- `Reputation`
- `Analytics`
- `Messages`
- `Settings`
- `Simulation`

Notes:
- `Simulation` is a researcher-only subplatform under the same account
- `Leaderboard` does not need to be a top-level sidebar item; it belongs inside `Reputation` and selected dashboard widgets
- `Programs` is absorbed into `Engagements`

## 5. Global Researcher Layout

All researcher pages should use one shared shell:

- left sidebar for main modules
- top header for page title, search, notifications, and profile menu
- optional top horizontal navigation inside the active module
- content area with KPI cards first, then the main workspace
- right rail only where it adds value, not on every page

### 5.1 Header

Header elements:
- page title and contextual subtitle
- search or quick-find field
- notifications
- message shortcut
- profile/avatar menu

Optional header actions by page:
- `Submit Report`
- `Browse Opportunities`
- `Open Simulation`
- `Request Withdrawal`

### 5.2 Shared Dashboard Components

Reusable blocks:
- `MetricCard`
- `TrendMetricCard`
- `SectionCard`
- `OpportunityCard`
- `StatusBadge`
- `SeverityBadge`
- `QueueTable`
- `LeaderboardCard`
- `ChartCard`
- `QuickActionGroup`
- `FilterTabs`
- `TypeSwitch`

## 6. Dashboard Specification

Route:
- `/researcher/dashboard`

Purpose:
- show current standing, active work, earnings, and recommended next actions

### 6.1 Dashboard Block Order

1. Page header
2. KPI row
3. Main engagement workbench
4. Right-side insight rail
5. Analytics row
6. Quick actions row

### 6.2 KPI Row

The top KPI row should contain exactly four primary cards:

- `Total Earnings`
- `Reports Submitted`
- `Pending Bounty`
- `Reputation & Rank`

Optional micro-trend inside each card:
- 7-day delta
- 30-day delta
- small sparkline

### 6.3 Main Workbench

Primary block:
- `My Engagements`

Top controls:
- type switch: `Bug Bounty | PTaaS | AI Red Teaming | Code Review | Live Events`
- status tabs: `Eligible | Recommended | Invited | Active | Completed`
- filter bar: severity focus, private/public, payout range, skill tag

Main content:
- table or card list depending on viewport size

Required columns for desktop:
- engagement name
- organization
- engagement type
- invitation or eligibility state
- joined or assigned date
- status
- reward or payout range
- deadline or next milestone
- action

Primary row actions:
- `View Details`
- `Accept Invite`
- `Decline`
- `Open Workspace`
- `Submit Report`

### 6.4 Right Insight Rail

This area should be modular. The image mixed `Recent Submissions` and `Leaderboard`, which should be separated.

Default dashboard right rail:
- `Leaderboard Snapshot`
- `Recent Activity`
- `Recommended Opportunities`

Alternative mobile behavior:
- these cards collapse below the main workbench

### 6.5 Analytics Row

Dashboard analytics widgets:
- `Earnings Trend` using line or area chart
- `Submission Trend` using line chart
- `Severity Distribution` using stacked bar or donut
- `Response / Resolution Snapshot` using grouped bar chart

This is required. The researcher dashboard cannot be only cards plus tables.

### 6.6 Quick Actions Row

Required actions:
- `Submit New Report`
- `Browse Opportunities`
- `Open Simulation`
- `View Invitations`

## 7. Engagements Module

Route family:
- `/researcher/engagements`

Purpose:
- unify all researcher-facing opportunity discovery and assigned work

### 7.1 Engagement Model

The researcher sees engagements through one shared module, but the underlying logic differs by type:

- `Bug Bounty`
- `PTaaS`
- `AI Red Teaming`
- `Code Review`
- `Live Events`

`BountyMatch` drives eligibility, recommendation, invitation, and assignment visibility.

### 7.2 Top-Level Engagement Tabs

Status tabs:
- `Eligible`
- `Recommended`
- `Invited`
- `Active`
- `Completed`

Type switch:
- `Bug Bounty`
- `PTaaS`
- `AI Red Teaming`
- `Code Review`
- `Live Events`

### 7.3 Engagement List Behavior

#### Eligible
- open to the researcher based on role, skills, and policy
- can include public bug bounty programs and system-qualified service opportunities

#### Recommended
- highest-fit opportunities ranked by BountyMatch
- show match score and explanation preview

#### Invited
- private invitations and assigned opportunities
- clear accept or decline flow
- expiration state visible

#### Active
- currently joined programs or accepted engagements
- direct shortcut to the active workspace

#### Completed
- closed engagements with final outcome, rewards, and feedback history

### 7.4 Engagement Detail Page

Route pattern:
- `/researcher/engagements/[engagementId]`

Shared tabs:
- `Overview`
- `Scope`
- `Requirements`
- `Activity`
- `Deliverables`
- `Messages`

Conditional tabs by type:

Bug Bounty:
- `Rules`
- `Rewards`
- `Leaderboard`

PTaaS:
- `Workspace`
- `Findings`
- `Report`

AI Red Teaming:
- `Environment`
- `Findings`
- `Classification`

Code Review:
- `Repository`
- `Findings`
- `Clarifications`

Live Events:
- `Schedule`
- `Leaderboard`
- `Announcements`

### 7.5 BountyMatch UI Inside Researcher Views

The researcher should not manage the algorithm, but should see matching transparency.

Visible elements:
- match score
- skill fit summary
- reputation fit summary
- availability fit summary
- invitation reason or recommendation reason

Do not expose admin algorithm controls in the researcher portal.

## 8. Reports Module

Route family:
- `/researcher/reports`

Purpose:
- manage vulnerability submissions and researcher-side report communication

### 8.1 Report Tabs

- `Drafts`
- `Submitted`
- `Need Response`
- `Validated`
- `Rejected`
- `Closed`

### 8.2 Main Report List Fields

- report title
- engagement or program
- severity
- current status
- last organization or triage update
- bounty status
- created date
- last action

### 8.3 Report Detail Structure

Route pattern:
- `/researcher/reports/[reportId]`

Tabs:
- `Summary`
- `Timeline`
- `Evidence`
- `Conversation`
- `Bounty`
- `Audit`

Primary researcher actions:
- `Reply to Question`
- `Upload Evidence`
- `Clarify Reproduction`
- `Request Update`

Important rule:
- report status must reflect the true workflow from submission through triage, validation, payout, and closure

## 9. Earnings Module

Route family:
- `/researcher/earnings`

Purpose:
- make payouts and balances operational, not hidden

### 9.1 Earnings Tabs

- `Overview`
- `Balance`
- `Withdrawals`
- `Transactions`
- `Payment Methods`

### 9.2 Earnings Dashboard Blocks

- current available balance
- pending rewards
- lifetime earnings
- withdrawal success rate
- monthly earnings trend chart
- payout method breakdown
- recent transactions

### 9.3 Primary Actions

- `Request Withdrawal`
- `Add Payment Method`
- `View Payout Status`

## 10. Reputation Module

Route family:
- `/researcher/reputation`

Purpose:
- show researcher standing, trust, and platform recognition

### 10.1 Reputation Tabs

- `Overview`
- `Leaderboard`
- `Badges`
- `Achievements`
- `Feedback`

### 10.2 Reputation Blocks

- reputation score
- global or regional rank
- percentile position
- validated reports count
- severity quality mix
- badges earned
- organization feedback summary

### 10.3 Charting

Recommended charts:
- reputation trend line
- validated severity mix bar chart
- feedback radar or grouped bar chart

## 11. Analytics Module

Route family:
- `/researcher/analytics`

Purpose:
- provide a dedicated performance analysis space beyond the dashboard widgets

### 11.1 Analytics Tabs

- `Overview`
- `Reports`
- `Earnings`
- `Reputation`
- `Engagements`

### 11.2 Analytics Metrics

Required coverage:
- submissions over time
- validation rate
- severity distribution
- response time to triage questions
- earnings over time
- average bounty by severity
- invitation acceptance rate
- active engagement load
- reputation trend

### 11.3 Chart Types

- line or area charts for time trends
- stacked bar charts for status flow
- grouped bar charts for category comparison
- sparklines in KPI cards
- donut only for small composition summaries

## 12. Messages Module

Route family:
- `/researcher/messages`

Purpose:
- support communication with organizations, triage, and system notifications

### 12.1 Message Tabs

- `Inbox`
- `Organizations`
- `Triage`
- `System`
- `Archived`

### 12.2 Required Features

- unread counts
- conversation list
- report-linked conversations
- engagement-linked conversations
- file attachment support

## 13. Settings Module

Route family:
- `/researcher/settings`

Purpose:
- central account, security, profile, and preference management

### 13.1 Settings Tabs

- `Profile`
- `Security`
- `Notifications`
- `Payment Preferences`
- `Visibility`

### 13.2 Settings Capabilities

- update researcher profile
- edit skill tags and specializations
- configure timezone and languages
- enable or manage MFA
- manage notification channels
- manage profile visibility for matching and invitations

## 14. Simulation Module

Route family:
- `/researcher/simulation`

Purpose:
- researcher-only learning and practice subplatform under the same account

This is not a separate login product.

### 14.1 Simulation Sections

- `Dashboard`
- `Challenges`
- `Active Session`
- `Progress`
- `Leaderboard`
- `Resources`

### 14.2 Required Simulation Flow

Based on the simulation sequence:

1. researcher opens simulation
2. challenge list is loaded
3. researcher starts a challenge
4. isolated vulnerable instance is created
5. researcher practices and may request hints
6. researcher submits the exploit and description
7. system evaluates score and feedback
8. progress and leaderboard update

### 14.3 Main Simulation Widgets

- challenges completed
- total points
- current level
- badges
- challenge category grid
- progress tracker
- leaderboard snapshot

## 15. Proposed Route Tree

```text
/researcher
  /dashboard
  /engagements
    /[engagementId]
  /reports
    /new
    /[reportId]
  /earnings
  /reputation
  /analytics
  /messages
  /settings
  /simulation
    /dashboard
    /challenges
    /session/[sessionId]
    /progress
    /leaderboard
```

## 16. Reusable Frontend Component Set

Shared researcher portal components should include:

- `ResearcherShell`
- `ResearcherSidebar`
- `ResearcherHeader`
- `MetricCard`
- `TrendMetricCard`
- `InsightCard`
- `EngagementTable`
- `OpportunityCard`
- `ReportStatusTimeline`
- `BountySummaryCard`
- `LeaderboardCard`
- `ChartCard`
- `QuickActionPanel`
- `SimulationChallengeCard`

## 17. Implementation Order

Recommended build sequence:

1. `Dashboard`
2. `Engagements` list and detail shell
3. `Reports` list, submission, and detail flow
4. `Earnings`
5. `Reputation`
6. `Analytics`
7. `Messages`
8. `Settings`
9. `Simulation`

Reason:
- it preserves the core bug bounty workflow first
- it surfaces BountyMatch-backed opportunity discovery early
- it keeps simulation integrated but not blocking the primary product flow

## 18. Final Decision

The researcher image is accepted as a structural reference only.

The final researcher portal will use:
- the agreed sidebar from the navigation agreement
- the engagement model from the platform business logic
- the workflow realism already benchmarked from major platforms
- the image layout density
- the YesWeHack-inspired light theme

This should be treated as the implementation blueprint for the researcher frontend.
