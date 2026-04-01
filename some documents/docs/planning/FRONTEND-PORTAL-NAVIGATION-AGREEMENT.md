# Frontend Portal Navigation Agreement
## Final Sidebar, Auth Split, and Portal Boundaries

Date: 2026-03-31

This document captures the agreed frontend information architecture for the platform so implementation can proceed without further drift.

## 1. Auth Boundary

There are two authentication entry points and one researcher-only subplatform:

### Public Auth
- Shared by `researcher` and `organization`
- Public registration allows choosing:
  - `researcher`
  - `organization`
- Shared public login page

### Staff Auth
- Separate frontend access from the public portal
- Separate login page
- No public staff registration
- Staff accounts are provisioned internally by admin
- Staff roles:
  - `admin`
  - `triage_specialist`
  - `finance_officer`

### Simulation / Learning
- Not a separate auth product
- Not a separate registration flow
- Researcher-only subplatform
- Entered from the researcher portal
- Uses the same researcher account/session

## 2. Portal Split

### Public Portal
- Researcher portal
- Organization portal

### Staff Portal
- Admin portal
- Triage portal
- Finance portal

### Researcher Simulation Subplatform
- Separate panel/workspace for learning and practice
- Reached from researcher UI

## 3. High-Level Navigation Rule

Use the following structure consistently:

- `Sidebar`: major modules only
- `Horizontal tabs`: workflow steps, states, or sub-sections inside the active module
- `Cards`: summary metrics
- `Main panel`: queue, workbench, chart area, or management table

Dark and light mode must not change structure. Theme only changes visual tokens.

## 4. Engagement Model

The following are different products, but they belong to a common engagement architecture:

- Regular Bug Bounty Program
- PTaaS Engagement
- AI Red Teaming Engagement
- Code Review Engagement
- Live Hacking Event

`BountyMatch` is the cross-cutting eligibility and assignment layer.

For researchers, engagement views are participation-oriented.
For organizations, engagement views are management-oriented.

## 5. Final Sidebar Agreement

### Researcher Sidebar
- `Dashboard`
- `Engagements`
- `Reports`
- `Earnings`
- `Reputation`
- `Analytics`
- `Messages`
- `Settings`
- `Simulation`

#### Researcher Engagement Tabs
- `Eligible`
- `Recommended`
- `Invited`
- `Active`
- `Completed`

#### Researcher Engagement Type Switch
- `Bug Bounty`
- `PTaaS`
- `AI Red Teaming`
- `Code Review`
- `Live Events`

### Organization Sidebar
- `Dashboard`
- `Engagements`
- `Reports`
- `BountyMatch`
- `Integrations`
- `Team`
- `Billing`
- `Analytics`
- `Messages`
- `Settings`

#### Organization Engagement Tabs
- `Bug Bounty`
- `PTaaS`
- `AI Red Teaming`
- `Code Review`
- `Live Events`

### Admin Sidebar
- `Dashboard`
- `Users`
- `Staff`
- `Engagements`
- `BountyMatch`
- `Integrations`
- `Payments`
- `Analytics`
- `Audit Logs`
- `Settings`

#### Admin Staff Tabs
- `All Staff`
- `Provision Staff`
- `Roles & Permissions`
- `Security`
- `Activity`

#### Admin Engagement Tabs
- `Bug Bounty`
- `PTaaS`
- `AI Red Teaming`
- `Code Review`
- `Live Events`

### Triage Specialist Sidebar
- `Dashboard`
- `Triage Queue`
- `Tools`
- `Analytics`
- `Messages`
- `Settings`

#### Triage Queue Type Tabs
- `Bug Bounty`
- `PTaaS`
- `AI Red Teaming`
- `Live Events`

#### Triage Queue Status Tabs
- `New`
- `In Review`
- `Validated`
- `Rejected`
- `Duplicate`

#### Triage Tools Tabs
- `Duplicate Checker`
- `VRT`
- `Templates`

### Finance Officer Sidebar
- `Dashboard`
- `Payments`
- `Payouts`
- `KYC`
- `Transactions`
- `Invoices`
- `Analytics`
- `Messages`
- `Settings`

#### Finance Payment Tabs
- `Pending Approval`
- `Processing`
- `Completed`
- `Disputes`

## 6. Role Routing

### Public Login Redirects
- `researcher` → `/researcher/dashboard`
- `organization` → `/organization/dashboard`

### Staff Login Redirects
- `admin` → `/admin/dashboard`
- `triage_specialist` → `/triage/dashboard`
- `finance_officer` → `/finance/dashboard`

## 7. Route Structure Direction

### Public Portal
- `/login`
- `/register`
- `/researcher/*`
- `/organization/*`

### Researcher Simulation
- `/researcher/simulation/*`

### Staff Portal
- `/ops/login`
- `/admin/*`
- `/triage/*`
- `/finance/*`

## 8. Analytics Agreement

Every role has analytics.

### Researcher Analytics
- earnings trend
- submissions trend
- severity distribution
- reputation trend

### Organization Analytics
- report volume
- SLA performance
- bounty spend
- vulnerability category trends

### Triage Analytics
- queue inflow vs resolved
- severity mix
- response-time trend
- duplicate rate

### Finance Analytics
- payout throughput
- pending approval value
- commission trend
- payment-method split

### Admin Analytics
- user growth
- program activity
- revenue
- platform health

## 9. Theme Agreement

### Layout Source
- Use the operational density and dashboard layout style from the reviewed dark mockups

### Light Theme Source
- Use the card/button color language from the YesWeHack-style screenshot

### Theme Rule
- Same structure in dark and light mode
- Only tokens/colors change

## 10. Implementation Consequence

The current generic staff portal is temporary and should be replaced by:
- `/triage/*`
- `/finance/*`

The current navigation implementation should be refactored to match this document before deeper workflow pages are added.
