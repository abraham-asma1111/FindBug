#!/usr/bin/env python3
"""
Script to get valid reports grouped by severity for Finance Dashboard.
Usage: python3 get_reports_by_severity.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import func
from src.core.database import SessionLocal
from src.domain.models.report import VulnerabilityReport


def get_reports_by_severity():
    """Get valid reports grouped by severity."""
    db: Session = SessionLocal()
    
    try:
        # Query valid reports grouped by severity
        severity_stats = db.query(
            func.coalesce(
                VulnerabilityReport.assigned_severity,
                VulnerabilityReport.suggested_severity
            ).label('severity'),
            func.count(VulnerabilityReport.id).label('count')
        ).filter(
            VulnerabilityReport.status == 'valid'
        ).group_by(
            'severity'
        ).order_by(
            func.count(VulnerabilityReport.id).desc()
        ).all()
        
        print(f"\n{'='*80}")
        print(f"VALID REPORTS BY SEVERITY (Finance Dashboard)")
        print(f"{'='*80}\n")
        
        total = sum(stat.count for stat in severity_stats)
        
        for stat in severity_stats:
            severity = stat.severity or 'Not Assigned'
            count = stat.count
            percentage = (count / total * 100) if total > 0 else 0
            
            # Color coding
            if severity == 'critical':
                icon = '🔴'
            elif severity == 'high':
                icon = '🟠'
            elif severity == 'medium':
                icon = '🟡'
            elif severity == 'low':
                icon = '🟢'
            else:
                icon = '⚪'
            
            print(f"{icon} {severity.upper():15} : {count:3} reports ({percentage:5.1f}%)")
        
        print(f"\n{'='*80}")
        print(f"TOTAL VALID REPORTS: {total}")
        print(f"{'='*80}\n")
        
        # Return data for API
        return {
            'total': total,
            'by_severity': [
                {
                    'severity': stat.severity or 'not_assigned',
                    'count': stat.count,
                    'percentage': round((stat.count / total * 100) if total > 0 else 0, 1)
                }
                for stat in severity_stats
            ]
        }
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {'total': 0, 'by_severity': []}
    finally:
        db.close()


if __name__ == "__main__":
    data = get_reports_by_severity()
    
    print("\nJSON Format for API:")
    import json
    print(json.dumps(data, indent=2))
