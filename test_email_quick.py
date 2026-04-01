#!/usr/bin/env python3
"""
Quick Email Test - Run after setting Gmail credentials
"""
import os
import sys
import requests

# Test email configuration
def test_email_setup():
    print("🧪 Testing Email Service")
    print("=" * 40)
    
    # Check if credentials are set
    smtp_user = os.getenv('SMTP_USER', 'YOUR_EMAIL@gmail.com')
    smtp_password = os.getenv('SMTP_PASSWORD', 'YOUR_16_CHAR_APP_PASSWORD')
    
    if smtp_user == 'YOUR_EMAIL@gmail.com' or smtp_password == 'YOUR_16_CHAR_APP_PASSWORD':
        print("❌ Please update Gmail credentials in backend/.env")
        print("   SMTP_USER=your-email@gmail.com")
        print("   SMTP_PASSWORD=your-app-password")
        return False
    
    print(f"✅ Email configured: {smtp_user}")
    return True

def test_registration_flow():
    """Test OTP registration with real email"""
    print("\n🚀 Testing Registration Flow")
    print("=" * 40)
    
    # Test data
    test_email = input("Enter your email to test: ").strip()
    if not test_email:
        print("❌ No email provided")
        return
    
    # Register
    register_data = {
        "email": test_email,
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post("http://localhost:8002/api/v1/registration/researcher/initiate", 
                               json=register_data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Registration initiated successfully!")
            print("📧 Check your email for OTP code")
            
            # Get OTP from user
            otp = input("Enter the 6-digit OTP from your email: ").strip()
            if len(otp) == 6 and otp.isdigit():
                # Verify OTP
                verify_data = {"email": test_email, "otp": otp}
                verify_response = requests.post("http://localhost:8002/api/v1/registration/verify-otp", 
                                              json=verify_data, timeout=10)
                
                if verify_response.status_code == 201:
                    print("🎉 Registration completed successfully!")
                    result = verify_response.json()
                    print(f"   User ID: {result.get('user_id')}")
                    print(f"   Email: {result.get('email')}")
                else:
                    print(f"❌ OTP verification failed: {verify_response.text}")
            else:
                print("❌ Invalid OTP format")
        else:
            print(f"❌ Registration failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running on port 8002?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if test_email_setup():
        test_registration_flow()