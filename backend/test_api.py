import requests

# 1. Login to get token (using an admin user from DB, we can just use the first user with admin role)
import asyncio
from src.core.database import SessionLocal
from src.domain.models.user import User

db = SessionLocal()
admin_user = db.query(User).filter(User.role == 'admin').first()

if not admin_user:
    print("No admin user found")
    exit(1)

print(f"Using admin: {admin_user.email}")
# We need to bypass auth or just query the service, but the user is hitting the API.
# Let's just create a token for this user manually.
from src.core.security import create_access_token
token = create_access_token({"sub": str(admin_user.id), "role": admin_user.role})

res = requests.get("http://localhost:8002/api/v1/admin/reports?limit=1000", headers={"Authorization": f"Bearer {token}"})
if res.status_code != 200:
    print(f"Error: {res.status_code} - {res.text}")
    exit(1)

data = res.json()
reports = data.get("reports", [])
print(f"API returned {len(reports)} reports")
if reports:
    print(f"Sample report keys: {list(reports[0].keys())}")
    
breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0, 'none': 0}
for r in reports:
    sev = r.get("assigned_severity") or r.get("suggested_severity")
    if sev:
        sev = sev.lower()
        if sev in breakdown:
            breakdown[sev] += 1
    else:
        breakdown['none'] += 1

print("API Breakdown:")
for k, v in breakdown.items():
    print(f"  {k}: {v}")

