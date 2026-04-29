#!/usr/bin/env python3
"""
Add medium severity valid reports to database for testing.
"""
import sys
import os
sys.path.insert(0, '.')

from src.core.database import SessionLocal
from src.domain.models.report import VulnerabilityReport
from sqlalchemy import func

db = SessionLocal()

try:
    # Check current valid reports
    print("\n=== CURRENT VALID REPORTS ===")
    valid_reports = db.query(VulnerabilityReport).filter(
        VulnerabilityReport.status == 'valid'
    ).all()
    
    for report in valid_reports:
        severity = report.assigned_severity or report.suggested_severity
        print(f"Report #{report.report_number}: {severity}")
    
    # Count by severity
    severity_stats = db.query(
        func.coalesce(
            VulnerabilityReport.assigned_severity,
            VulnerabilityReport.suggested_severity
        ).label('severity'),
        func.count(VulnerabilityReport.id).label('count')
    ).filter(
        VulnerabilityReport.status == 'valid'
    ).group_by('severity').all()
    
    print("\n=== SEVERITY BREAKDOWN ===")
    for stat in severity_stats:
        print(f"{stat.severity}: {stat.count}")
    
    # Find reports that can be updated to medium
    # Get some 'low' or 'high' reports and change them to 'medium'
    reports_to_update = db.query(VulnerabilityReport).filter(
        VulnerabilityReport.status == 'valid',
        func.coalesce(
            VulnerabilityReport.assigned_severity,
            VulnerabilityReport.suggested_severity
        ).in_(['low', 'high'])
    ).limit(2).all()
    
    if reports_to_update:
        print(f"\n=== UPDATING {len(reports_to_update)} REPORTS TO MEDIUM ===")
        for report in reports_to_update:
            old_severity = report.assigned_severity or report.suggested_severity
            if report.assigned_severity:
                report.assigned_severity = 'medium'
            else:
                report.suggested_severity = 'medium'
            print(f"Report #{report.report_number}: {old_severity} → medium")
        
        db.commit()
        print("\n✓ Reports updated successfully!")
    else:
        print("\n⚠ No reports found to update")
    
    # Show final breakdown
    severity_stats = db.query(
        func.coalesce(
            VulnerabilityReport.assigned_severity,
            VulnerabilityReport.suggested_severity
        ).label('severity'),
        func.count(VulnerabilityReport.id).label('count')
    ).filter(
        VulnerabilityReport.status == 'valid'
    ).group_by('severity').order_by(
        func.count(VulnerabilityReport.id).desc()
    ).all()
    
    print("\n=== FINAL SEVERITY BREAKDOWN ===")
    total = sum(stat.count for stat in severity_stats)
    for stat in severity_stats:
        severity = stat.severity or 'not_assigned'
        count = stat.count
        percentage = round((count / total * 100) if total > 0 else 0, 1)
        print(f"{severity}: {count} ({percentage}%)")
    
    print(f"\nTotal valid reports: {total}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
