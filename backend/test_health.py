import asyncio
from src.core.database import SessionLocal
from src.domain.models.user import User
from src.api.v1.endpoints.system_health import get_system_health

async def test():
    db = SessionLocal()
    # Mock an admin user
    user = User(role='admin')
    res = await get_system_health(db, user)
    print(res)

asyncio.run(test())
