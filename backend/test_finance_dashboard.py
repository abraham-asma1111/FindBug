#!/usr/bin/env python3
"""Test Finance Dashboard Analytics Endpoint"""
import requests
import json

BASE_URL = "http://localhost:8002/api/v1"

# Login as finance officer
print("🔐 Logging in as finance officer...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "finance@findbug.com",
        "password": "Finance123!"
    }
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
print(f"✅ Login successful! Token: {token[:20]}...")

# Test analytics endpoint
print("\n📊 Fetching payment analytics...")
headers = {"Authorization": f"Bearer {token}"}
analytics_response = requests.get(
    f"{BASE_URL}/payments/analytics?range=30d",
    headers=headers
)

if analytics_response.status_code != 200:
    print(f"❌ Analytics request failed: {analytics_response.status_code}")
    print(analytics_response.text)
    exit(1)

analytics_data = analytics_response.json()
print("✅ Analytics data retrieved successfully!")
print(f"\n📈 Stats:")
print(f"  - Total Payments: {analytics_data.get('stats', {}).get('total_payments', 0)}")
print(f"  - Total Amount: ${analytics_data.get('stats', {}).get('total_amount', 0):,.2f}")
print(f"  - Avg Payment: ${analytics_data.get('stats', {}).get('avg_payment', 0):,.2f}")
print(f"  - Total Commission: ${analytics_data.get('stats', {}).get('total_commission', 0):,.2f}")

print(f"\n📊 Payment Trends: {len(analytics_data.get('payment_trends', []))} data points")
print(f"📊 Severity Distribution: {len(analytics_data.get('severity_distribution', []))} categories")
print(f"👥 Top Researchers: {len(analytics_data.get('top_researchers', []))} researchers")
print(f"📅 Monthly Comparison: {len(analytics_data.get('monthly_comparison', []))} months")

print("\n✅ Finance Dashboard is ready to use!")
print("🌐 Open: http://localhost:3000/finance/dashboard")
