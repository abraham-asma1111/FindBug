import asyncio
from src.core.database import SessionLocal
from src.services.admin_service import AdminService

def test():
    db = SessionLocal()
    service = AdminService(db)
    reports = service.get_all_reports(limit=1000, offset=0)
    print(f"Service returned {len(reports)} reports")
    breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0, 'none': 0}
    for r in reports:
        sev = r.assigned_severity or r.suggested_severity
        if sev:
            sev = sev.lower()
            if sev in breakdown:
                breakdown[sev] += 1
            else:
                print(f"Unknown: {sev}")
        else:
            breakdown['none'] += 1
    
    print("Breakdown in service output:")
    for k, v in breakdown.items():
        if v > 0:
            print(f"  {k}: {v}")

test()
