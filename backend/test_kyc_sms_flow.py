"""
Test script for KYC + SMS verification flow
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8002/api/v1"

# Test user credentials (create a test user first)
TEST_EMAIL = "researcher@test.com"
TEST_PASSWORD = "Test123!@#"


async def test_kyc_sms_flow():
    """Test the complete KYC + SMS verification flow"""
    
    print("=" * 60)
    print("KYC + SMS VERIFICATION FLOW TEST")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # Step 1: Login
        print("\n[1] Logging in...")
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
        # Step 2: Start Persona KYC
        print("\n[2] Starting Persona KYC verification...")
        persona_start_response = await client.post(
            f"{BASE_URL}/kyc/persona/start",
            headers=headers
        )
        
        if persona_start_response.status_code != 200:
            print(f"❌ Persona start failed: {persona_start_response.text}")
            return
        
        persona_data = persona_start_response.json()
        print(f"✅ Persona inquiry created: {persona_data['inquiry_id']}")
        print(f"   Template: {persona_data['template_id']}")
        
        # Step 3: Check Persona status
        print("\n[3] Checking Persona status...")
        persona_status_response = await client.get(
            f"{BASE_URL}/kyc/persona/status",
            headers=headers
        )
        
        if persona_status_response.status_code != 200:
            print(f"❌ Persona status check failed: {persona_status_response.text}")
            return
        
        persona_status = persona_status_response.json()
        print(f"✅ Persona status: {persona_status['persona_status']}")
        print(f"   Can verify phone: {persona_status['can_verify_phone']}")
        
        # Step 4: Send SMS verification code
        print("\n[4] Sending SMS verification code...")
        phone_number = "+251912345678"  # Test Ethiopian number
        
        sms_send_response = await client.post(
            f"{BASE_URL}/kyc/phone/send",
            headers=headers,
            params={"phone_number": phone_number}
        )
        
        if sms_send_response.status_code != 200:
            print(f"❌ SMS send failed: {sms_send_response.text}")
            # This might fail if Persona KYC is not approved yet
            print("   Note: Persona KYC must be approved first")
            return
        
        sms_data = sms_send_response.json()
        print(f"✅ SMS sent to: {sms_data['phone_number']}")
        
        # In mock mode, the code is returned in the response
        if "mock_code" in sms_data:
            verification_code = sms_data["mock_code"]
            print(f"   Mock code: {verification_code}")
            
            # Step 5: Verify the code
            print("\n[5] Verifying SMS code...")
            verify_response = await client.post(
                f"{BASE_URL}/kyc/phone/verify",
                headers=headers,
                params={"code": verification_code}
            )
            
            if verify_response.status_code != 200:
                print(f"❌ Code verification failed: {verify_response.text}")
                return
            
            verify_data = verify_response.json()
            print(f"✅ Phone verified: {verify_data['phone_number']}")
            print(f"   Verified at: {verify_data['verified_at']}")
        else:
            print("   Check your phone for the verification code")
            print("   Then call: POST /api/v1/kyc/phone/verify with the code")
        
        # Step 6: Check final status
        print("\n[6] Checking final verification status...")
        phone_status_response = await client.get(
            f"{BASE_URL}/kyc/phone/status",
            headers=headers
        )
        
        if phone_status_response.status_code != 200:
            print(f"❌ Phone status check failed: {phone_status_response.text}")
            return
        
        phone_status = phone_status_response.json()
        print(f"✅ Phone verified: {phone_status['phone_verified']}")
        print(f"   Persona approved: {phone_status['persona_approved']}")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
        
        # Summary
        print("\n📊 VERIFICATION STATUS:")
        print(f"   ✅ Email: Verified (logged in)")
        print(f"   {'✅' if persona_status.get('persona_status') == 'completed' else '⏳'} Persona KYC: {persona_status.get('persona_status', 'not started')}")
        print(f"   {'✅' if phone_status.get('phone_verified') else '⏳'} Phone: {'Verified' if phone_status.get('phone_verified') else 'Not verified'}")


if __name__ == "__main__":
    print("\n🔧 Configuration:")
    print(f"   Persona Template: {os.getenv('PERSONA_TEMPLATE_RESEARCHER')}")
    print(f"   SMS Mode: {'Mock' if os.getenv('SMS_MOCK_MODE', 'true').lower() == 'true' else 'Production'}")
    print(f"   SMS Provider: {os.getenv('SMS_PROVIDER', 'mock')}")
    
    asyncio.run(test_kyc_sms_flow())
