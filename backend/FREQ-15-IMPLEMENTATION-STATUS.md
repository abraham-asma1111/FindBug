# FREQ-15 Implementation Status: Analytics Reports

## Requirement
**FREQ-15**: The system shall view analytics reports for vulnerability trends, program effectiveness, and researcher performance.

**Priority**: High

## Implementation Details

### 1. Analytics Models (`backend/src/domain/models/analytics.py`)
Based on Extended ERD, created 4 analytics models:

#### ResearcherMetrics
- Tracks researcher performance metrics
- Fields: total_reports, validated_reports, success_rate, reputation_score, total_earnings, rank
- Severity breakdown (critical, high, medium, low)
- Time metrics (avg_time_to_triage, avg_time_to_resolve)

#### OrganizationMetrics
- Tracks organization analytics
- Fields: total_programs, active_programs, total_reports_received, validated_reports
- Time metrics (mttr_hours, avg_triage_time_hours)
- Financial metrics (total_bounties_paid, platform_commission_paid, roi)
- Severity breakdown

#### PlatformMetrics
- Tracks platform-wide daily statistics
- Fields: total_users, total_researchers, total_organizations, active_users
- Program metrics (total_programs, active_programs)
- Report metrics (total_reports, validated_reports, resolved_reports)
- Financial metrics (total_bounties_paid, platform_revenue)
- Performance metrics (avg_triage_time, avg_resolution_time)

#### AnalyticsReport
- Stores generated custom analytics reports
- Fields: report_type, report_name, description, filters, time_period
- Report data stored as JSON
- Metadata (generated_by, generated_for, generated_at, expires_at)

### 2. Analytics Service (`backend/src/services/analytics_service.py`)
Comprehensive analytics service with 3 main report types:

#### Vulnerability Trends Analytics
**Method**: `get_vulnerability_trends(program_id, organization_id, time_period)`

**Provides**:
- Total vulnerabilities in period
- Severity distribution (critical, high, medium, low, unassigned)
- Status distribution (new, triaged, valid, invalid, duplicate, resolved)
- Top 10 vulnerability types
- Time-series data (submissions over time by week)
- Average time to triage (hours)
- Average time to resolve (days)
- Duplicate rate percentage

**Time Periods**: 7days, 30days, 3months, 6months, 1year

#### Program Effectiveness Analytics
**Method**: `get_program_effectiveness(program_id, organization_id, time_period)`

**Provides**:
- Total programs analyzed
- Report volume (total, valid, resolved)
- Quality rate (valid/total percentage)
- Resolution rate (resolved/valid percentage)
- Unique researchers engaged
- Total bounties paid
- Average response time (hours)
- Average resolution time (days)
- Program-by-program breakdown with quality rates

#### Researcher Performance Analytics
**Method**: `get_researcher_performance(researcher_id, time_period)`

**Single Researcher Analysis**:
- Total reports, valid reports, invalid reports
- Success rate percentage
- Earnings in period
- Current reputation score and rank
- Severity distribution
- Top 5 vulnerability types (specialization)
- Monthly trend (reports, valid reports, earnings)

**Top Researchers Comparison** (when no researcher_id):
- Top 10 researchers by reputation
- Comparison metrics: rank, reputation, reports, success rate, earnings

### 3. API Endpoints (`backend/src/api/v1/endpoints/analytics.py`)
RESTful analytics endpoints with role-based access control:

| Endpoint | Method | Access | Description |
|----------|--------|--------|-------------|
| `/api/v1/analytics/vulnerability-trends` | GET | Org/Staff/Admin | Vulnerability trends analytics |
| `/api/v1/analytics/program-effectiveness` | GET | Org/Staff/Admin | Program effectiveness analytics |
| `/api/v1/analytics/researcher-performance` | GET | Researcher/Staff/Admin | Researcher performance analytics |
| `/api/v1/analytics/my-performance` | GET | Researcher | Current researcher's performance |

### 4. Access Control

#### Vulnerability Trends
- **Organizations**: Can view their own programs only
- **Staff/Admin**: Can view all programs
- **Researchers**: No access

#### Program Effectiveness
- **Organizations**: Can view their own programs only
- **Staff/Admin**: Can view all programs
- **Researchers**: No access

#### Researcher Performance
- **Researchers**: Can view their own performance only
- **Organizations**: Can view top researchers comparison (no specific researcher)
- **Staff/Admin**: Can view any researcher or top researchers

## Analytics Features

### Vulnerability Trends
✅ Submission volume over time
✅ Severity distribution analysis
✅ Status progression tracking
✅ Top vulnerability types identification
✅ Time-to-triage metrics
✅ Time-to-resolve metrics
✅ Duplicate rate calculation
✅ Weekly time-series data

### Program Effectiveness
✅ Report volume and quality metrics
✅ Response time analysis
✅ Resolution rate tracking
✅ ROI indicators
✅ Researcher engagement metrics
✅ Program-by-program comparison
✅ Quality rate per program
✅ Financial performance tracking

### Researcher Performance
✅ Submission trends over time
✅ Success rate calculation
✅ Earnings trend analysis
✅ Specialization identification
✅ Severity distribution
✅ Monthly performance trends
✅ Peer comparison (top 10)
✅ Reputation and rank tracking

## Query Parameters

### Time Periods
- `7days` - Last 7 days
- `30days` - Last 30 days
- `3months` - Last 3 months
- `6months` - Last 6 months (default)
- `1year` - Last 12 months

### Filters
- `program_id` - Filter by specific program
- `organization_id` - Filter by organization
- `researcher_id` - Filter by specific researcher

## API Response Examples

### Vulnerability Trends Response
```json
{
  "period": "6months",
  "start_date": "2025-09-18T00:00:00",
  "end_date": "2026-03-18T23:59:59",
  "total_vulnerabilities": 150,
  "severity_distribution": {
    "critical": 15,
    "high": 45,
    "medium": 60,
    "low": 25,
    "unassigned": 5
  },
  "status_distribution": {
    "new": 10,
    "triaged": 20,
    "valid": 80,
    "invalid": 15,
    "duplicate": 10,
    "resolved": 15
  },
  "top_vulnerability_types": [
    {"type": "SQL Injection", "count": 25},
    {"type": "XSS", "count": 20}
  ],
  "time_series": [...],
  "metrics": {
    "avg_time_to_triage_hours": 4.5,
    "avg_time_to_resolve_days": 15.2,
    "duplicate_rate": 6.67
  }
}
```

### Program Effectiveness Response
```json
{
  "period": "6months",
  "summary": {
    "total_programs": 3,
    "total_reports": 150,
    "valid_reports": 80,
    "resolved_reports": 15,
    "quality_rate": 53.33,
    "resolution_rate": 18.75,
    "unique_researchers": 45,
    "total_paid": 50000.00,
    "avg_response_time_hours": 12.5,
    "avg_resolution_time_days": 20.3
  },
  "programs": [
    {
      "program_id": "...",
      "program_name": "Web Application Security",
      "total_reports": 80,
      "valid_reports": 50,
      "quality_rate": 62.5
    }
  ]
}
```

### Researcher Performance Response
```json
{
  "researcher_id": "...",
  "period": "6months",
  "metrics": {
    "total_reports": 25,
    "valid_reports": 20,
    "invalid_reports": 3,
    "success_rate": 80.0,
    "earnings": 5000.00,
    "reputation_score": 450.0,
    "rank": 15
  },
  "severity_distribution": {
    "critical": 5,
    "high": 10,
    "medium": 8,
    "low": 2
  },
  "top_vulnerability_types": [
    {"type": "SQL Injection", "count": 8},
    {"type": "XSS", "count": 6}
  ],
  "monthly_trend": [...]
}
```

## Use Cases

### UC-01: Organization Reviews Vulnerability Trends
1. Organization logs in
2. Calls GET `/api/v1/analytics/vulnerability-trends?time_period=6months`
3. Views severity distribution over time
4. Identifies most common vulnerability types
5. Analyzes triage and resolution times
6. Makes informed decisions about security priorities

### UC-02: Organization Evaluates Program Effectiveness
1. Organization logs in
2. Calls GET `/api/v1/analytics/program-effectiveness?program_id=xxx`
3. Reviews report quality rates
4. Checks response and resolution times
5. Analyzes researcher engagement
6. Calculates ROI on bug bounty investment

### UC-03: Researcher Tracks Performance
1. Researcher logs in
2. Calls GET `/api/v1/analytics/my-performance?time_period=3months`
3. Views success rate trends
4. Checks earnings over time
5. Identifies specialization areas
6. Compares to peer performance

### UC-04: Admin Monitors Platform Health
1. Admin logs in
2. Calls GET `/api/v1/analytics/vulnerability-trends` (all programs)
3. Reviews platform-wide trends
4. Identifies systemic issues
5. Monitors quality metrics
6. Makes platform improvements

## Integration with Dashboards (FREQ-13)

The analytics service complements the dashboard service:

**Dashboards (FREQ-13)**:
- Real-time current metrics
- Quick overview cards
- Recent activity lists
- Calculated on-demand

**Analytics (FREQ-15)**:
- Historical trend analysis
- Time-series data
- Comparative analysis
- Detailed breakdowns

Both services can be used together:
- Dashboard shows current state
- Analytics shows trends and history
- Dashboard uses analytics for trend charts

## Files Created/Modified

### Created
- `backend/src/domain/models/analytics.py` - Analytics models (Extended ERD)
- `backend/src/services/analytics_service.py` - Analytics service
- `backend/src/api/v1/endpoints/analytics.py` - Analytics API endpoints

### Modified
- `backend/src/main.py` - Registered analytics router
- `backend/src/api/v1/endpoints/__init__.py` - Added analytics export
- `backend/src/domain/models/__init__.py` - Added analytics models export

## Performance Considerations

### Query Optimization
- Efficient aggregation queries using SQLAlchemy functions
- Proper use of indexes on date fields
- Filtered queries to reduce data volume
- Time-based partitioning for large datasets

### Caching Strategy (Future)
- Cache analytics results for 1 hour
- Invalidate cache on new reports
- Use Redis for distributed caching
- Pre-calculate daily metrics

### Scalability
- Analytics tables for pre-calculated metrics
- Background jobs for metric updates
- Materialized views for complex queries
- Query result pagination

## Future Enhancements

### Advanced Analytics
- Predictive analytics (ML-based)
- Anomaly detection
- Trend forecasting
- Correlation analysis

### Export Capabilities
- PDF report generation
- CSV data export
- Excel spreadsheets
- Scheduled email reports

### Visualization
- Interactive charts
- Customizable dashboards
- Drill-down capabilities
- Real-time updates

### Custom Reports
- User-defined report templates
- Saved report configurations
- Scheduled report generation
- Report sharing

## Status: ✅ COMPLETE

All FREQ-15 requirements implemented:
- ✅ Vulnerability trends analytics
- ✅ Program effectiveness analytics
- ✅ Researcher performance analytics
- ✅ Time-series data analysis
- ✅ Comparative analysis
- ✅ Role-based access control
- ✅ Multiple time period options
- ✅ Detailed breakdowns and metrics

## Next Steps
- Create database migration for analytics tables
- Implement background jobs to populate analytics tables
- Add caching layer for performance
- Build frontend visualization components
- Add export functionality (PDF, CSV)
- Implement scheduled report generation
