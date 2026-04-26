"""Count all reports in database."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.report import VulnerabilityReport

def count_all_reports():
    """Count all reports."""
    db: Session = SessionLocal()
    
    try:
        print("\n" + "=" * 80)
        print("ALL REPORTS IN DATABASE")
        print("=" * 80)
        
        # Get ALL reports
        all_reports = db.query(VulnerabilityReport).all()
        
        print(f"\n📊 TOTAL REPORTS IN DATABASE: {len(all_reports)}")
        
        # Count by status
        status_counts = {}
        for report in all_reports:
            status = report.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("\n📋 BY STATUS:")
        for status, count in sorted(status_counts.items()):
            print(f"   • {status}: {count}")
        
        # Count reports WITH triaged_at set
        triaged_count = sum(1 for r in all_reports if r.triaged_at is not None)
        print(f"\n✅ Reports with triaged_at set: {triaged_count}")
        print(f"❌ Reports without triaged_at: {len(all_reports) - triaged_count}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    count_all_reports()
