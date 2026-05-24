#!/usr/bin/env python3
"""Debug script to check user lookup for enrichment."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.audit_log import AuditLog

def debug_user_lookup():
    """Check user lookup."""
    db: Session = SessionLocal()
    
    try:
        # Get program_published event
        program_event = db.query(AuditLog).filter(
            AuditLog.action_type == "program_published"
        ).first()
        
        if program_event:
            print("=" * 80)
            print("PROGRAM EVENT")
            print("=" * 80)
            print(f"Actor ID: {program_event.actor_id}")
            print(f"Actor Role: {program_event.actor_role}")
            print(f"Actor Email: {program_event.actor_email}")
            
            if program_event.actor_id:
                user = db.query(User).filter(User.id == program_event.actor_id).first()
                if user:
                    print(f"\n✓ Found user:")
                    print(f"  User ID: {user.id}")
                    print(f"  Email: {user.email}")
                    print(f"  Role: {user.role}")
                    print(f"  Has organization: {user.organization is not None}")
                    
                    if user.organization:
                        print(f"\n✓ Organization:")
                        print(f"  Company Name: {user.organization.company_name}")
                    else:
                        print(f"\n✗ No organization relationship")
                else:
                    print(f"\n✗ User not found for ID: {program_event.actor_id}")
        
        # Get kyc_submitted event
        kyc_event = db.query(AuditLog).filter(
            AuditLog.action_type == "kyc_submitted"
        ).first()
        
        if kyc_event:
            print("\n" + "=" * 80)
            print("KYC EVENT")
            print("=" * 80)
            print(f"Actor ID: {kyc_event.actor_id}")
            print(f"Actor Role: {kyc_event.actor_role}")
            print(f"Actor Email: {kyc_event.actor_email}")
            
            if kyc_event.actor_id:
                user = db.query(User).filter(User.id == kyc_event.actor_id).first()
                if user:
                    print(f"\n✓ Found user:")
                    print(f"  User ID: {user.id}")
                    print(f"  Email: {user.email}")
                    print(f"  Role: {user.role}")
                    print(f"  Has researcher: {user.researcher is not None}")
                    
                    if user.researcher:
                        print(f"\n✓ Researcher:")
                        print(f"  Username: {user.researcher.username}")
                        print(f"  First Name: {user.researcher.first_name}")
                        print(f"  Last Name: {user.researcher.last_name}")
                    else:
                        print(f"\n✗ No researcher relationship")
                else:
                    print(f"\n✗ User not found for ID: {kyc_event.actor_id}")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_user_lookup()
