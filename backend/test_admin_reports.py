import requests
import json

response = requests.post("http://localhost:8002/api/v1/auth/login", json={
    "email": "admin@findbug.com",
    "password": "Password123!"
})
token = response.json().get("access_token")

res = requests.get("http://localhost:8002/api/v1/admin/reports?limit=1000", headers={"Authorization": f"Bearer {token}"})
reports = res.json().get("reports", [])
print(f"Got {len(reports)} reports from API")
breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0, 'none': 0}
for r in reports:
    sev = r.get("assigned_severity") or r.get("suggested_severity")
    if sev:
        sev = sev.lower()
        if sev in breakdown:
            breakdown[sev] += 1
    else:
        breakdown['none'] += 1
print("API Severity Breakdown:")
for k, v in breakdown.items():
    if v > 0:
        print(f"  {k}: {v}")
