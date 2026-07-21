"""Count reports triaged in April 2026."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime
from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.report import VulnerabilityReport

def count_april_triaged():
    """Count reports triaged in April 2026."""
    db: Session = SessionLocal()
    
    try:
        print("\n" + "=" * 80)
        print("APRIL 2026 TRIAGED REPORTS COUNT")
        print("=" * 80)
        
        # Define April 2026 date range
        april_start = datetime(2026, 4, 1)
        april_end = datetime(2026, 5, 1)
        
        # Get all reports triaged in April 2026
        april_reports = db.query(VulnerabilityReport).filter(
            VulnerabilityReport.triaged_at >= april_start,
            VulnerabilityReport.triaged_at < april_end
        ).all()
        
        print(f"\n📊 TOTAL REPORTS TRIAGED IN APRIL 2026: {len(april_reports)}")
        
        if len(april_reports) == 0:
            print("\n❌ No reports were triaged in April 2026")
            print("   The chart will show 0 for April")
        else:
            # Count by status
            status_counts = {}
            for report in april_reports:
                status = report.status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print("\n📋 BREAKDOWN BY STATUS:")
            for status, count in sorted(status_counts.items()):
                print(f"   • {status}: {count}")
            
            print("\n📝 DETAILED LIST:")
            for i, report in enumerate(april_reports, 1):
                triaged_date = report.triaged_at.strftime('%Y-%m-%d %H:%M:%S')
                print(f"   {i}. {report.report_number} - Status: {report.status} - Triaged: {triaged_date}")
        
        # Also check total reports with triaged_at set (all time)
        print("\n" + "-" * 80)
        all_triaged = db.query(VulnerabilityReport).filter(
            VulnerabilityReport.triaged_at.isnot(None)
        ).count()
        print(f"📊 TOTAL REPORTS EVER TRIAGED (ALL TIME): {all_triaged}")
        
        # Check reports by month
        print("\n" + "-" * 80)
        print("📅 TRIAGED REPORTS BY MONTH:")
        
        all_triaged_reports = db.query(VulnerabilityReport).filter(
            VulnerabilityReport.triaged_at.isnot(None)
        ).order_by(VulnerabilityReport.triaged_at.desc()).all()
        
        monthly_counts = {}
        for report in all_triaged_reports:
            month_key = report.triaged_at.strftime('%Y-%m')
            month_label = report.triaged_at.strftime('%B %Y')
            if month_key not in monthly_counts:
                monthly_counts[month_key] = {'label': month_label, 'count': 0}
            monthly_counts[month_key]['count'] += 1
        
        for month_key in sorted(monthly_counts.keys(), reverse=True):
            data = monthly_counts[month_key]
            print(f"   • {data['label']}: {data['count']} reports")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    count_april_triaged()
