#!/usr/bin/env python3
"""
Test Password Reset Flow
Tests the complete password reset functionality
"""
import requests
import time

BASE_URL = "http://localhost:8002/api/v1"

def test_password_reset_flow():
    """Test complete password reset flow"""
    
    print("\n" + "="*60)
    print("PASSWORD RESET FLOW TEST")
    print("="*60)
    
    # Use an existing test email
    test_email = "abrahamasmamaw4@gmail.com"
    
    print(f"\n1️⃣  Requesting password reset for: {test_email}")
    print("-" * 60)
    
    # Step 1: Request password reset
    response = requests.post(
        f"{BASE_URL}/auth/forgot-password",
        json={"email": test_email}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("\n✅ Password reset email sent successfully!")
        print("\n📧 Check your email for the reset link")
        print("   The link will look like:")
        print("   http://localhost:3000/auth/reset-password?token=...")
        print("\n⏰ Token expires in 15 minutes")
        print("\n2️⃣  Next steps:")
        print("   1. Check email inbox")
        print("   2. Click the reset link")
        print("   3. Enter new password on the page")
        print("   4. Submit to reset password")
        print("\n✨ The page should now display correctly (no blank page)")
    else:
        print(f"\n❌ Failed to send password reset email")
        print(f"   Status: {response.status_code}")
        print(f"   Error: {response.text}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_password_reset_flow()
