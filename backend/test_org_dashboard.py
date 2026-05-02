#!/usr/bin/env python3
"""Test organization dashboard endpoint."""
import requests
import json
import sys

# Configuration
API_URL = "http://127.0.0.1:8002/api/v1"

def test_organization_dashboard():
    """Test the organization dashboard endpoint."""
    print("=" * 80)
    print("ORGANIZATION DASHBOARD TEST")
    print("=" * 80)
    
    # Step 1: Login as organization user
    print("\n1. Logging in as organization user...")
    login_data = {
        "email": "org@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   Error: {response.text}")
            print("\n   Trying alternative organization credentials...")
            
            # Try alternative credentials
            alt_credentials = [
                {"email": "organization@example.com", "password": "password123"},
                {"email": "test@org.com", "password": "password123"},
                {"email": "admin@testorg.com", "password": "password123"},
            ]
            
            for cred in alt_credentials:
                print(f"   Trying: {cred['email']}")
                response = requests.post(f"{API_URL}/auth/login", json=cred)
                if response.status_code == 200:
                    print(f"   ✓ Success with {cred['email']}")
                    break
            else:
                print("\n   ✗ Could not login with any credentials")
                print("   Please create an organization user first:")
                print("   cd backend && python create_org_user.py")
                return False
        
        auth_data = response.json()
        access_token = auth_data.get("access_token")
        
        if not access_token:
            print(f"   ✗ No access token in response: {auth_data}")
            return False
        
        print(f"   ✓ Login successful")
        print(f"   User: {auth_data.get('user', {}).get('email')}")
        print(f"   Role: {auth_data.get('user', {}).get('role')}")
        
    except Exception as e:
        print(f"   ✗ Login failed: {e}")
        return False
    
    # Step 2: Fetch organization dashboard
    print("\n2. Fetching organization dashboard...")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{API_URL}/dashboard/organization", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ✗ Error: {response.text}")
            return False
        
        dashboard_data = response.json()
        print(f"   ✓ Dashboard data received")
        
        # Display dashboard summary
        print("\n" + "=" * 80)
        print("DASHBOARD DATA SUMMARY")
        print("=" * 80)
        
        # Programs
        programs = dashboard_data.get("programs", {})
        print(f"\nPrograms:")
        print(f"  Total: {programs.get('total', 0)}")
        print(f"  Active: {programs.get('active', 0)}")
        print(f"  Top Programs: {len(programs.get('top_programs', []))}")
        
        # Reports
        reports = dashboard_data.get("reports", {})
        print(f"\nReports:")
        print(f"  Total: {reports.get('total', 0)}")
        print(f"  By Status: {reports.get('by_status', {})}")
        print(f"  By Severity: {reports.get('by_severity', {})}")
        
        # Bounties
        bounties = dashboard_data.get("bounties", {})
        print(f"\nBounties:")
        print(f"  Total Paid: ETB {bounties.get('total_paid', 0):,.2f}")
        print(f"  Total Pending: ETB {bounties.get('total_pending', 0):,.2f}")
        print(f"  Total Commission: ETB {bounties.get('total_commission', 0):,.2f}")
        print(f"  Total Cost: ETB {bounties.get('total_cost', 0):,.2f}")
        
        # Recent Reports
        recent_reports = dashboard_data.get("recent_reports", [])
        print(f"\nRecent Reports: {len(recent_reports)}")
        for i, report in enumerate(recent_reports[:3], 1):
            print(f"  {i}. {report.get('title', 'N/A')} - {report.get('status', 'N/A')}")
        
        # Monthly Trend
        monthly_trend = dashboard_data.get("monthly_trend", [])
        print(f"\nMonthly Trend: {len(monthly_trend)} months")
        
        # Full JSON output
        print("\n" + "=" * 80)
        print("FULL JSON RESPONSE")
        print("=" * 80)
        print(json.dumps(dashboard_data, indent=2))
        
        return True
        
    except Exception as e:
        print(f"   ✗ Dashboard fetch failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_organization_dashboard()
    sys.exit(0 if success else 1)
