import asyncio
from src.core.database import SessionLocal
from src.domain.models.report import VulnerabilityReport

def count_severities():
    db = SessionLocal()
    reports = db.query(VulnerabilityReport).all()
    
    breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0, 'none': 0}
    for r in reports:
        sev = r.assigned_severity or r.suggested_severity
        if sev:
            sev = sev.lower()
            if sev in breakdown:
                breakdown[sev] += 1
            else:
                print(f"Unknown severity: {sev}")
        else:
            breakdown['none'] += 1
            
    print(f"Total reports: {len(reports)}")
    print("Severity Breakdown:")
    for k, v in breakdown.items():
        if v > 0:
            print(f"  {k}: {v}")

if __name__ == "__main__":
    count_severities()
