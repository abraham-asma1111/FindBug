import sys
import asyncio
from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.services.admin_service import AdminService

db = SessionLocal()
try:
    service = AdminService(db)
    logs = service.get_platform_audit_log()
    print(f"Got {len(logs)} logs")
    if logs:
        print(logs[0])
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
