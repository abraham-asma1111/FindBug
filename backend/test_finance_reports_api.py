#!/usr/bin/env python3
"""
Test the finance reports API to see what data it returns
"""
import requests
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8002/api/v1"

# Calculate date ranges
end = datetime.now()
start_30d = end - timedelta(days=30)
start_90d = end - timedelta(days=90)

print("=" * 80)
print("TESTING FINANCE REPORTS API")
print("=" * 80)

# Test with 30 days
print("\n1. Testing with Last 30 Days:")
print(f"   Start: {start_30d.date()}")
print(f"   End: {end.date()}")

url_30d = f"{BASE_URL}/finance/reports/payments?start_date={start_30d.date()}&end_date={end.date()}&format=json"
print(f"   URL: {url_30d}")

try:
    response = requests.get(url_30d)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success!")
        print(f"   Total Transactions: {data['summary'].get('total_transactions', 'N/A')}")
        print(f"   Total Amount: {data['summary'].get('total_amount', 'N/A')} ETB")
        print(f"   Average Amount: {data['summary'].get('average_amount', 'N/A')} ETB")
        print(f"   Number of records: {len(data.get('data', []))}")
    else:
        print(f"   ✗ Error: {response.status_code}")
        print(f"   {response.text}")
except Exception as e:
    print(f"   ✗ Exception: {e}")

# Test with 90 days
print("\n2. Testing with Last 90 Days:")
print(f"   Start: {start_90d.date()}")
print(f"   End: {end.date()}")

url_90d = f"{BASE_URL}/finance/reports/payments?start_date={start_90d.date()}&end_date={end.date()}&format=json"
print(f"   URL: {url_90d}")

try:
    response = requests.get(url_90d)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success!")
        print(f"   Total Transactions: {data['summary'].get('total_transactions', 'N/A')}")
        print(f"   Total Amount: {data['summary'].get('total_amount', 'N/A')} ETB")
        print(f"   Average Amount: {data['summary'].get('average_amount', 'N/A')} ETB")
        print(f"   Number of records: {len(data.get('data', []))}")
    else:
        print(f"   ✗ Error: {response.status_code}")
        print(f"   {response.text}")
except Exception as e:
    print(f"   ✗ Exception: {e}")

print("\n" + "=" * 80)
