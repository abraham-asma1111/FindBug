"""
Test Africa's Talking SMS API Integration
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_africastalking_api():
    """Test Africa's Talking SMS API directly"""
    
    # Get credentials from .env
    api_key = os.getenv("SMS_API_KEY")
    username = os.getenv("AFRICASTALKING_USERNAME", "sandbox")
    sender_id = os.getenv("SMS_SENDER_ID", "FindBug")
    
    print("=" * 60)
    print("AFRICA'S TALKING SMS API TEST")
    print("=" * 60)
    print(f"API Key: {api_key[:20]}..." if api_key else "API Key: NOT SET")
    print(f"Username: {username}")
    print(f"Sender ID: {sender_id}")
    print("=" * 60)
    
    if not api_key:
        print("❌ ERROR: SMS_API_KEY not set in .env file")
        return
    
    # Test phone number
    phone = "+251902676824"
    message = "Test SMS from FindBug Platform. Your verification code is: 123456"
    
    print(f"\n📱 Sending SMS to: {phone}")
    print(f"📝 Message: {message}")
    print("\n🔄 Making API request...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.africastalking.com/version1/messaging",
                headers={
                    "apiKey": api_key,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                },
                data={
                    "username": username,
                    "to": phone,
                    "message": message,
                    "from": sender_id
                }
            )
            
            print(f"\n📊 Response Status: {response.status_code}")
            print(f"📄 Response Body:\n{response.text}")
            
            if response.status_code == 201:
                print("\n✅ SUCCESS: SMS sent successfully!")
                data = response.json()
                print(f"Response data: {data}")
            else:
                print(f"\n❌ FAILED: Status {response.status_code}")
                print(f"Error: {response.text}")
                
    except httpx.TimeoutException:
        print("\n❌ ERROR: Request timed out (30 seconds)")
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_africastalking_api())
