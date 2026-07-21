#!/usr/bin/env python3
"""Debug script to check actual audit log data in database."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.audit_log import AuditLog
from src.domain.models.program import BountyProgram
from src.domain.models.organization import Organization

def debug_audit_logs():
    """Check actual audit log data."""
    db: Session = SessionLocal()
    
    try:
        print("=" * 80)
        print("CHECKING AUDIT LOG DATA")
        print("=" * 80)
        
        # Get program_published event
        program_event = db.query(AuditLog).filter(
            AuditLog.action_type == "program_published"
        ).first()
        
        if program_event:
            print("\n✓ Found program_published event:")
            print(f"  ID: {program_event.id}")
            print(f"  Action Type: {program_event.action_type}")
            print(f"  Category: {program_event.action_category}")
            print(f"  Target Type: {program_event.target_type}")
            print(f"  Target ID: {program_event.target_id}")
            print(f"  Actor ID: {program_event.actor_id}")
            print(f"  Actor Email: {program_event.actor_email}")
            print(f"  Metadata: {program_event.audit_metadata}")
            
            # Try to find the program
            if program_event.target_id:
                program = db.query(BountyProgram).filter(
                    BountyProgram.id == program_event.target_id
                ).first()
                
                if program:
                    print(f"\n✓ Found program:")
                    print(f"  Program ID: {program.id}")
                    print(f"  Program Name: {program.name}")
                    print(f"  Organization ID: {program.organization_id}")
                    
                    if program.organization_id:
                        org = db.query(Organization).filter(
                            Organization.id == program.organization_id
                        ).first()
                        
                        if org:
                            print(f"\n✓ Found organization:")
                            print(f"  Org ID: {org.id}")
                            print(f"  Company Name: {org.company_name}")
                        else:
                            print(f"\n✗ Organization not found for ID: {program.organization_id}")
                else:
                    print(f"\n✗ Program not found for ID: {program_event.target_id}")
            else:
                print("\n✗ No target_id in program event")
        else:
            print("\n✗ No program_published event found")
        
        # Get kyc_submitted event
        print("\n" + "=" * 80)
        kyc_event = db.query(AuditLog).filter(
            AuditLog.action_type == "kyc_submitted"
        ).first()
        
        if kyc_event:
            print("\n✓ Found kyc_submitted event:")
            print(f"  ID: {kyc_event.id}")
            print(f"  Action Type: {kyc_event.action_type}")
            print(f"  Category: {kyc_event.action_category}")
            print(f"  Target Type: {kyc_event.target_type}")
            print(f"  Target ID: {kyc_event.target_id}")
            print(f"  Actor ID: {kyc_event.actor_id}")
            print(f"  Actor Email: {kyc_event.actor_email}")
            print(f"  Metadata: {kyc_event.audit_metadata}")
        else:
            print("\n✗ No kyc_submitted event found")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_audit_logs()
