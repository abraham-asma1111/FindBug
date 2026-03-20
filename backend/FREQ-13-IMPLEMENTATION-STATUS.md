# FREQ-13 Implementation Status: Role-Specific Dashboards

## Requirement
**FREQ-13**: The system shall provide role-specific dashboards: Researcher (submissions, earnings, rankings), Organization (program performance, reports, trends), Staff (triage queue), and Admin (platform overview).

**Priority**: High

## Implementation Details

### 1. Dashboard Service (`backend/src/services/dashboard_service.py`)
Comprehensive dashboard service with role-specific data aggregation:

#### Researcher Dashboard
**Method**: `get_researcher_dashboard(researcher_id)`

**Data Provided**:
- **Submissions Overview**
  - Total submissions count
  - Submissions by status (new, triaged, valid, invalid, resolved)
  - Active program participation count

- **Earnings Summary**
  - Total earnings (lifetime)
  - Pending earnings (approved but not paid)
  - Paid earnings

- **Reputation & Rankings**
  - Current reputation score
  - Current rank
  - Total researchers count
  - Percentile ranking (top X%)

- **Recent Activity**
  - Last 5 submissions with details

- **Monthly Trend** (6 months)
  - Submissions per month
  - Earnings per month

#### Organization Dashboard
**Method**: `get_organization_dashboard(organization_id)`

**Data Provided**:
- **Program Performance**
  - Total programs count
  - Active programs count
  - Top 5 programs by report count

- **Reports Overview**
  - Total reports across all programs
  - Reports by status (new, triaged, valid, resolved)
  - Reports by severity (critical, high, medium, low)

- **Bounty Spending**
  - Total paid bounties
  - Total pending bounties
  - Platform commission (30%)
  - Total cost (bounties + commission)

- **Recent Activity**
  - Last 10 reports across all programs

- **Monthly Trend** (6 months)
  - Reports received per month
  - Spending per month

#### Staff/Triage Dashboard
**Method**: `get_staff_dashboard()`

**Data Provided**:
- **Triage Queue**
  - New reports count
  - Triaged reports count
  - Total pending (new + triaged)

- **Priority Reports**
  - Critical severity suggestions
  - High severity suggestions
  - Unacknowledged reports (over 24 hours)

- **Status Breakdown**
  - Reports by all statuses

- **Recent Activity**
  - Last 10 triaged reports

- **Oldest Pending**
  - 10 oldest reports needing attention

- **Daily Stats** (7 days)
  - Reports submitted per day
  - Reports triaged per day

#### Admin Dashboard
**Method**: `get_admin_dashboard()`

**Data Provided**:
- **User Statistics**
  - Total users
  - Total researchers
  - Total organizations
  - Active users (last 30 days)
  - New users (last 30 days)

- **Program Statistics**
  - Total programs
  - Active programs
  - New programs (last 30 days)

- **Report Statistics**
  - Total reports
  - Reports by status
  - New reports (last 30 days)

- **Financial Overview**
  - Total bounties paid
  - Total bounties pending
  - Platform revenue (30% commission)
  - Commission rate

- **Top Performers**
  - Top 5 researchers by reputation
  - Top 5 organizations by program count

- **Platform Health**
  - Pending triage count
  - Overdue payouts count (over 30 days)

- **Monthly Growth** (6 months)
  - New users per month
  - New reports per month
  - New programs per month
  - Platform revenue per month

### 2. API Endpoints (`backend/src/api/v1/endpoints/dashboard.py`)
Role-specific dashboard endpoints with proper authorization:

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/api/v1/dashboard/researcher` | GET | Researcher | Researcher dashboard |
| `/api/v1/dashboard/organization` | GET | Organization | Organization dashboard |
| `/api/v1/dashboard/staff` | GET | Staff/Admin | Staff triage dashboard |
| `/api/v1/dashboard/admin` | GET | Admin | Platform overview dashboard |

### 3. Authorization
Each dashboard endpoint enforces role-based access:
- Researcher dashboard: Only researchers
- Organization dashboard: Only organizations
- Staff dashboard: Only staff and admins
- Admin dashboard: Only admins

## Dashboard Features

### Researcher Dashboard Features
✅ Submission tracking (total, by status)
✅ Earnings overview (total, pending, paid)
✅ Reputation score and rank
✅ Percentile ranking
✅ Recent submissions list
✅ Active program participation
✅ 6-month submission trend
✅ 6-month earnings trend

### Organization Dashboard Features
✅ Program performance metrics
✅ Report statistics (total, by status, by severity)
✅ Bounty spending analysis
✅ Platform commission tracking
✅ Top programs by report count
✅ Recent reports across all programs
✅ 6-month report trend
✅ 6-month spending trend

### Staff Dashboard Features
✅ Triage queue overview
✅ Priority report identification
✅ Unacknowledged report alerts
✅ Status breakdown
✅ Recent triage activity
✅ Oldest pending reports
✅ 7-day daily statistics
✅ Workload visualization

### Admin Dashboard Features
✅ Platform-wide user statistics
✅ Program activity metrics
✅ Report statistics
✅ Financial overview
✅ Platform revenue tracking
✅ Top performers (researchers & organizations)
✅ Platform health indicators
✅ 6-month growth trends
✅ User growth tracking
✅ Revenue growth tracking

## Data Aggregation

### Performance Optimizations
- Efficient SQL queries with proper indexing
- Aggregation at database level using SQLAlchemy functions
- Minimal data transfer
- Cached calculations where appropriate

### Time-Based Trends
- Monthly trends: 6-month rolling window
- Daily stats: 7-day rolling window
- Configurable time periods
- Consistent date formatting

### Statistical Calculations
- Percentile rankings
- Growth rates
- Success rates
- Average metrics
- Trend analysis

## Use Cases

### UC-01: Researcher Checks Dashboard
1. Researcher logs in
2. Navigates to dashboard
3. Views submission statistics
4. Checks pending earnings
5. Sees current rank and reputation
6. Reviews recent submissions
7. Analyzes monthly trends

### UC-02: Organization Reviews Performance
1. Organization logs in
2. Opens organization dashboard
3. Reviews program performance
4. Checks report statistics
5. Analyzes bounty spending
6. Identifies top-performing programs
7. Reviews monthly trends

### UC-03: Staff Manages Triage Queue
1. Triage specialist logs in
2. Opens staff dashboard
3. Sees pending report count
4. Identifies priority reports
5. Checks unacknowledged reports
6. Reviews recent activity
7. Prioritizes work based on data

### UC-04: Admin Monitors Platform
1. Admin logs in
2. Opens admin dashboard
3. Reviews platform statistics
4. Checks financial overview
5. Identifies top performers
6. Monitors platform health
7. Analyzes growth trends

## API Response Examples

### Researcher Dashboard Response
```json
{
  "overview": {
    "total_submissions": 25,
    "submissions_by_status": {
      "new": 2,
      "triaged": 3,
      "valid": 15,
      "invalid": 3,
      "resolved": 2
    },
    "active_programs": 5
  },
  "earnings": {
    "total_earnings": 5000.00,
    "pending_earnings": 500.00,
    "paid_earnings": 4500.00
  },
  "reputation": {
    "score": 450.0,
    "rank": 15,
    "total_researchers": 500,
    "percentile": 97.0
  },
  "recent_submissions": [...],
  "monthly_trend": [...]
}
```

### Organization Dashboard Response
```json
{
  "programs": {
    "total": 3,
    "active": 2,
    "top_programs": [...]
  },
  "reports": {
    "total": 150,
    "by_status": {...},
    "by_severity": {...}
  },
  "bounties": {
    "total_paid": 50000.00,
    "total_pending": 5000.00,
    "total_commission": 15000.00,
    "total_cost": 65000.00
  },
  "recent_reports": [...],
  "monthly_trend": [...]
}
```

### Staff Dashboard Response
```json
{
  "queue": {
    "new_reports": 25,
    "triaged_reports": 15,
    "total_pending": 40
  },
  "priority": {
    "critical": 5,
    "high": 10,
    "unacknowledged": 3
  },
  "status_breakdown": {...},
  "recent_activity": [...],
  "oldest_pending": [...],
  "daily_stats": [...]
}
```

### Admin Dashboard Response
```json
{
  "users": {
    "total": 1000,
    "researchers": 800,
    "organizations": 50,
    "active_30d": 600,
    "new_30d": 50
  },
  "programs": {...},
  "reports": {...},
  "financials": {
    "total_paid": 500000.00,
    "total_pending": 50000.00,
    "platform_revenue": 150000.00,
    "commission_rate": 0.30
  },
  "top_performers": {...},
  "health": {...},
  "monthly_growth": [...]
}
```

## Files Created/Modified

### Created
- `backend/src/services/dashboard_service.py` - Dashboard service with all role-specific methods
- `backend/src/api/v1/endpoints/dashboard.py` - Dashboard API endpoints

### Modified
- `backend/src/main.py` - Registered dashboard router
- `backend/src/api/v1/endpoints/__init__.py` - Added dashboard export

## Integration Points

### Existing Services Used
- Report statistics from `ReportRepository`
- Program data from `BountyProgram` model
- Researcher data from `Researcher` model
- Organization data from `Organization` model
- User data from `User` model
- Reputation data from reputation system
- Bounty data from bounty service

### Database Queries
- Efficient aggregation queries
- Proper use of indexes
- Minimal N+1 query issues
- Optimized joins

## Testing Scenarios

### Scenario 1: Researcher Views Dashboard
1. Researcher with 10 submissions logs in
2. Calls GET `/api/v1/dashboard/researcher`
3. Receives complete dashboard data
4. Sees accurate submission counts
5. Sees correct earnings breakdown
6. Sees current rank and reputation

### Scenario 2: Organization Analyzes Performance
1. Organization with 3 programs logs in
2. Calls GET `/api/v1/dashboard/organization`
3. Receives program performance data
4. Sees report statistics across all programs
5. Sees bounty spending breakdown
6. Sees monthly trends

### Scenario 3: Staff Checks Triage Queue
1. Triage specialist logs in
2. Calls GET `/api/v1/dashboard/staff`
3. Sees pending report counts
4. Identifies priority reports
5. Sees unacknowledged reports
6. Reviews daily statistics

### Scenario 4: Admin Monitors Platform
1. Admin logs in
2. Calls GET `/api/v1/dashboard/admin`
3. Sees platform-wide statistics
4. Reviews financial overview
5. Checks platform health
6. Analyzes growth trends

## Status: ✅ COMPLETE

All FREQ-13 requirements implemented:
- ✅ Researcher dashboard (submissions, earnings, rankings)
- ✅ Organization dashboard (program performance, reports, trends)
- ✅ Staff dashboard (triage queue, workload)
- ✅ Admin dashboard (platform overview, analytics)
- ✅ Role-based access control
- ✅ Comprehensive statistics
- ✅ Trend analysis (monthly/daily)
- ✅ Performance metrics
- ✅ Financial tracking

## Next Steps
- Frontend: Build dashboard UI components for each role
- Caching: Implement dashboard data caching for performance
- Real-time: Add WebSocket updates for live dashboard data
- Export: Add dashboard data export functionality (PDF, CSV)
- Customization: Allow users to customize dashboard widgets
- Alerts: Add dashboard alerts for important metrics
