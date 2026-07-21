#!/usr/bin/env python3
"""
Complete registration flow test
"""
import requests
import time

BASE_URL = "http://localhost:8002/api/v1"

def test_registration_flow():
    """Test complete registration flow"""
    
    # Step 1: Initiate registration
    print("Step 1: Initiating registration...")
    email = f"testuser{int(time.time())}@example.com"
    
    response = requests.post(
        f"{BASE_URL}/registration/researcher/initiate",
        json={
            "email": email,
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code != 200:
        print("❌ Registration initiation failed!")
        return False
    
    # Step 2: Get OTP from database
    print("\nStep 2: Getting OTP from database...")
    import psycopg2
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="bugbounty_db",
        user="bugbounty_user",
        password="bugbounty_secure_2024"
    )
    cur = conn.cursor()
    cur.execute(
        "SELECT verification_otp FROM pending_registrations WHERE email = %s",
        (email,)
    )
    result = cur.fetchone()
    
    if not result:
        print("❌ No pending registration found!")
        return False
    
    otp = result[0]
    print(f"OTP: {otp}")
    
    # Step 3: Verify OTP
    print("\nStep 3: Verifying OTP...")
    response = requests.post(
        f"{BASE_URL}/registration/verify-otp",
        json={
            "email": email,
            "otp": otp
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        print("\n✅ Registration completed successfully!")
        
        # Verify user was created
        cur.execute("SELECT id, email, role FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        if user:
            print(f"✅ User created: ID={user[0]}, Email={user[1]}, Role={user[2]}")
        
        conn.close()
        return True
    else:
        print("\n❌ OTP verification failed!")
        conn.close()
        return False

if __name__ == "__main__":
    success = test_registration_flow()
    exit(0 if success else 1)
