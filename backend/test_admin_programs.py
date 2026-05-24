import asyncio
from src.core.database import SessionLocal
from src.services.admin_service import AdminService
from src.domain.models.program import BountyProgram

def test():
    db = SessionLocal()
    
    # Check what statuses actually exist in the DB
    programs = db.query(BountyProgram).all()
    print("Statuses in DB:")
    for p in programs:
        print(f" - {p.name}: {p.status}")
        
    service = AdminService(db)
    filtered = service.get_all_programs(status="active")
    print(f"\nService returned {len(filtered)} programs for status='active'")

test()
