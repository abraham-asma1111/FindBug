"""Check triaged reports by month."""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from src.domain.models.report import VulnerabilityReport
from datetime import datetime, timedelta

# Database connection
DATABASE_URL = "postgresql://bugbounty_user:changeme123@localhost:5432/bugbounty_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("\n" + "="*80)
print("TRIAGED REPORTS BY MONTH")
print("="*80)

# Get all reports with triaged_at set
triaged_reports = db.query(VulnerabilityReport).filter(
    VulnerabilityReport.triaged_at.isnot(None)
).order_by(VulnerabilityReport.triaged_at.desc()).all()

print(f"\nTotal reports with triaged_at set: {len(triaged_reports)}")

# Group by month
monthly_counts = {}
for report in triaged_reports:
    month_key = report.triaged_at.strftime('%Y-%m')
    month_label = report.triaged_at.strftime('%B %Y')
    
    if month_key not in monthly_counts:
        monthly_counts[month_key] = {
            'label': month_label,
            'count': 0,
            'reports': []
        }
    
    monthly_counts[month_key]['count'] += 1
    monthly_counts[month_key]['reports'].append({
        'number': report.report_number,
        'status': report.status,
        'triaged_at': report.triaged_at.strftime('%Y-%m-%d %H:%M:%S')
    })

# Print monthly breakdown
print("\n" + "-"*80)
print("MONTHLY BREAKDOWN:")
print("-"*80)

for month_key in sorted(monthly_counts.keys(), reverse=True):
    data = monthly_counts[month_key]
    print(f"\n{data['label']}: {data['count']} reports")
    for r in data['reports'][:5]:  # Show first 5
        print(f"  - {r['number']} ({r['status']}) - {r['triaged_at']}")
    if len(data['reports']) > 5:
        print(f"  ... and {len(data['reports']) - 5} more")

# Check April 2026 specifically
print("\n" + "="*80)
print("APRIL 2026 DETAILS:")
print("="*80)

april_2026 = db.query(VulnerabilityReport).filter(
    VulnerabilityReport.triaged_at >= datetime(2026, 4, 1),
    VulnerabilityReport.triaged_at < datetime(2026, 5, 1)
).all()

print(f"\nTotal reports triaged in April 2026: {len(april_2026)}")
print("\nAll April 2026 reports:")
for report in april_2026:
    print(f"  - {report.report_number} ({report.status}) - {report.triaged_at.strftime('%Y-%m-%d %H:%M:%S')}")

# Check what the API query returns (last 6 months)
print("\n" + "="*80)
print("API QUERY SIMULATION (last 6 months):")
print("="*80)

six_months_ago = datetime.utcnow() - timedelta(days=180)
api_results = db.query(
    func.date(VulnerabilityReport.triaged_at).label('date'),
    func.count(VulnerabilityReport.id).label('triaged_count')
).filter(
    VulnerabilityReport.triaged_at >= six_months_ago,
    VulnerabilityReport.triaged_at.isnot(None)
).group_by(
    func.date(VulnerabilityReport.triaged_at)
).order_by(
    func.date(VulnerabilityReport.triaged_at).desc()
).all()

print(f"\nAPI would return {len(api_results)} daily records")
print("\nDaily breakdown:")
for result in api_results[:10]:  # Show first 10
    print(f"  {result.date}: {result.triaged_count} reports")
if len(api_results) > 10:
    print(f"  ... and {len(api_results) - 10} more days")

# Calculate monthly totals from API data
api_monthly = {}
for result in api_results:
    month_key = result.date.strftime('%Y-%m')
    if month_key not in api_monthly:
        api_monthly[month_key] = 0
    api_monthly[month_key] += result.triaged_count

print("\nMonthly totals from API data:")
for month_key in sorted(api_monthly.keys(), reverse=True):
    print(f"  {month_key}: {api_monthly[month_key]} reports")

db.close()
print("\n" + "="*80)
