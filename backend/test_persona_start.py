#!/usr/bin/env python3
"""
Test script to debug Persona KYC start endpoint
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.services.kyc_service import KYCService
from src.domain.models.user import User
from uuid import UUID


async def test_persona_start():
    """Test starting Persona verification"""
    db = SessionLocal()
    
    try:
        # Get a test user (researcher)
        user = db.query(User).filter(User.role == "researcher").first()
        
        if not user:
            print("❌ No researcher user found in database")
            return
        
        print(f"✓ Found user: {user.email} (ID: {user.id})")
        print(f"✓ User role: {user.role}")
        print(f"✓ Email verified: {user.email_verified_at is not None}")
        
        # Check environment variables
        print("\n📋 Environment Variables:")
        print(f"  PERSONA_API_KEY: {'✓ Set' if os.getenv('PERSONA_API_KEY') else '❌ Missing'}")
        print(f"  PERSONA_ENVIRONMENT: {os.getenv('PERSONA_ENVIRONMENT', 'Not set')}")
        print(f"  PERSONA_TEMPLATE_RESEARCHER: {os.getenv('PERSONA_TEMPLATE_RESEARCHER', 'Not set')}")
        print(f"  PERSONA_TEMPLATE_ORGANIZATION: {os.getenv('PERSONA_TEMPLATE_ORGANIZATION', 'Not set')}")
        
        # Initialize KYC service
        kyc_service = KYCService(db)
        
        print("\n🚀 Starting Persona verification...")
        
        try:
            result = await kyc_service.start_persona_verification(
                user_id=user.id,
                user_role=user.role
            )
            
            print("\n✅ SUCCESS!")
            print(f"  Inquiry ID: {result['inquiry_id']}")
            print(f"  Template ID: {result['template_id']}")
            print(f"  Status: {result['status']}")
            
        except ValueError as e:
            print(f"\n❌ ValueError: {str(e)}")
        except Exception as e:
            print(f"\n❌ Exception: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_persona_start())
