#!/usr/bin/env python3
"""
Test the verification redirect
"""
import requests

def test_verification_redirect():
    """Test that verification redirects to login page"""
    print("🧪 Testing verification redirect...")
    
    # Get a token from the database
    import os
    from dotenv import load_dotenv
    load_dotenv('backend/.env')
    
    import sys
    sys.path.append('backend/src')
    
    from sqlalchemy import create_engine, text
    
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/bugbounty')
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT verification_token FROM pending_registrations LIMIT 1"))
            row = result.fetchone()
            
            if not row:
                print("❌ No pending registrations found. Register first.")
                return False
            
            token = row[0]
            print(f"Found token: {token}")
            
            # Test the verification endpoint
            verification_url = f"http://localhost:8002/api/v1/registration/verify-email?token={token}"
            
            print(f"\n🔗 Testing verification URL: {verification_url}")
            
            # Use allow_redirects=False to see the redirect response
            response = requests.get(verification_url, allow_redirects=False)
            
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 302:
                redirect_url = response.headers.get('Location')
                print(f"✅ Redirects to: {redirect_url}")
                
                if 'login?verified=true' in redirect_url:
                    print("✅ Correct redirect to login page with verified=true")
                    return True
                else:
                    print("❌ Incorrect redirect URL")
                    return False
            else:
                print(f"❌ Expected 302 redirect, got {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_verification_redirect()