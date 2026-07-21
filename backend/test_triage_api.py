"""Test triage API endpoints directly."""
import requests
import json

BASE_URL = "http://localhost:8002/api/v1"

def test_triage_endpoints():
    """Test triage endpoints."""
    print("=" * 60)
    print("TESTING TRIAGE API ENDPOINTS")
    print("=" * 60)
    
    # Step 1: Login as triage specialist
    print("\n1. Login as triage specialist...")
    login_data = {
        "email": "triage@example.com",
        "password": "Password123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"   ✓ Login successful")
            print(f"   Token: {token[:50]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Step 2: Test queue endpoint
            print("\n2. Testing /triage/queue endpoint...")
            response = requests.get(f"{BASE_URL}/triage/queue", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Queue endpoint works")
                print(f"   Total reports: {data.get('total', 0)}")
                print(f"   Reports returned: {len(data.get('reports', []))}")
                
                if data.get('reports'):
                    print(f"\n   Sample report:")
                    report = data['reports'][0]
                    print(f"     - ID: {report.get('id')}")
                    print(f"     - Title: {report.get('title')}")
                    print(f"     - Status: {report.get('status')}")
                    print(f"     - Severity: {report.get('suggested_severity')}")
            else:
                print(f"   ❌ Error: {response.text}")
            
            # Step 3: Test statistics endpoint
            print("\n3. Testing /triage/statistics endpoint...")
            response = requests.get(f"{BASE_URL}/triage/statistics", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Statistics endpoint works")
                print(f"   Total reports: {data.get('total_reports', 0)}")
                print(f"   Pending triage: {data.get('pending_triage', 0)}")
                print(f"   Status breakdown: {data.get('status_breakdown', {})}")
            else:
                print(f"   ❌ Error: {response.text}")
            
            # Step 4: Test researchers endpoint
            print("\n4. Testing /triage/researchers endpoint...")
            response = requests.get(f"{BASE_URL}/triage/researchers", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Researchers endpoint works")
                print(f"   Total researchers: {data.get('total', 0)}")
            else:
                print(f"   ❌ Error: {response.text}")
            
            # Step 5: Test programs endpoint
            print("\n5. Testing /triage/programs endpoint...")
            response = requests.get(f"{BASE_URL}/triage/programs", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Programs endpoint works")
                print(f"   Total programs: {data.get('total', 0)}")
            else:
                print(f"   ❌ Error: {response.text}")
                
        else:
            print(f"   ❌ Login failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to backend server")
        print("   Make sure backend is running on http://localhost:8002")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_triage_endpoints()
