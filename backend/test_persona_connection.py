#!/usr/bin/env python3
"""Test Persona API connectivity"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_persona_connection():
    """Test if we can connect to Persona API"""
    api_key = os.getenv("PERSONA_API_KEY")
    
    print("=" * 80)
    print("PERSONA API CONNECTION TEST")
    print("=" * 80)
    print(f"API Key: {api_key[:20]}..." if api_key else "API Key: NOT SET")
    print()
    
    if not api_key:
        print("❌ PERSONA_API_KEY not set in .env file!")
        return
    
    print("Testing connection to Persona API...")
    print("URL: https://withpersona.com/api/v1/inquiries")
    print()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("Attempting connection (30 second timeout)...")
            response = await client.get(
                "https://withpersona.com/api/v1/inquiries",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Persona-Version": "2023-01-05"
                }
            )
            
            print(f"✅ Connection successful!")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except httpx.ConnectTimeout:
        print("❌ CONNECTION TIMEOUT")
        print("   The request timed out while trying to connect to Persona.")
        print("   Possible causes:")
        print("   - Firewall blocking outbound HTTPS connections")
        print("   - Network connectivity issues")
        print("   - Persona API is down (check https://status.withpersona.com)")
        print()
        print("   Try:")
        print("   1. Check your internet connection")
        print("   2. Try: curl https://withpersona.com")
        print("   3. Check firewall settings")
        
    except httpx.ReadTimeout:
        print("❌ READ TIMEOUT")
        print("   Connected but Persona took too long to respond.")
        
    except httpx.NetworkError as e:
        print(f"❌ NETWORK ERROR: {e}")
        print("   Cannot reach Persona API.")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_persona_connection())
