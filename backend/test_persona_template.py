"""
Test script to verify Persona template configuration.

This will test if the template ID is valid and can create inquiries.
"""
import httpx
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_persona_template():
    """Test Persona template by creating a test inquiry"""
    
    api_key = os.getenv("PERSONA_API_KEY")
    template_id = os.getenv("PERSONA_TEMPLATE_RESEARCHER")
    environment = os.getenv("PERSONA_ENVIRONMENT", "sandbox")
    
    print("="*60)
    print("PERSONA TEMPLATE TEST")
    print("="*60)
    print(f"API Key: {api_key[:20]}..." if api_key else "API Key: NOT SET")
    print(f"Template ID: {template_id}")
    print(f"Environment: {environment}")
    print()
    
    if not api_key or not template_id:
        print("❌ ERROR: Persona configuration missing in .env file")
        return
    
    # Test creating an inquiry with the template
    print("Testing inquiry creation with template...")
    print()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://withpersona.com/api/v1/inquiries",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "Persona-Version": "2023-01-05"
                },
                json={
                    "data": {
                        "attributes": {
                            "inquiry-template-id": template_id,
                            "reference-id": "test-user-123",
                            "environment": environment
                        }
                    }
                },
                timeout=10.0
            )
            
            print(f"Status Code: {response.status_code}")
            print()
            
            if response.status_code == 201:
                data = response.json()
                inquiry_id = data["data"]["id"]
                print("✅ SUCCESS: Inquiry created successfully!")
                print(f"   Inquiry ID: {inquiry_id}")
                print()
                print("Template is valid and working correctly.")
                print()
                print("Response data:")
                print(f"   ID: {data['data']['id']}")
                print(f"   Type: {data['data']['type']}")
                print(f"   Status: {data['data']['attributes'].get('status')}")
                
            elif response.status_code == 400:
                print("❌ ERROR: Bad Request (400)")
                print()
                print("This usually means:")
                print("  1. Template ID is invalid or doesn't exist")
                print("  2. Template is not properly configured")
                print("  3. Template is not active")
                print()
                print("Response:")
                print(response.text)
                
            elif response.status_code == 401:
                print("❌ ERROR: Unauthorized (401)")
                print("API key is invalid or expired")
                
            elif response.status_code == 404:
                print("❌ ERROR: Not Found (404)")
                print("Template ID does not exist")
                
            else:
                print(f"❌ ERROR: Unexpected status code {response.status_code}")
                print()
                print("Response:")
                print(response.text)
                
        except httpx.TimeoutException:
            print("❌ ERROR: Request timed out")
            print("Check your internet connection")
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print()
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_persona_template())
