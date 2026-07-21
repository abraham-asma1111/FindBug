#!/usr/bin/env python3
"""
Test script to verify activity logs display correct names (org names, usernames)
instead of admin email for all events.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.services.admin_service import AdminService
from src.domain.models.user import User
import json

def test_activity_logs():
    """Test activity logs enrichment with organization names and usernames."""
    db: Session = SessionLocal()
    
    try:
        admin_service = AdminService(db)
        
        print("=" * 80)
        print("TESTING ACTIVITY LOGS DISPLAY NAMES")
        print("=" * 80)
        
        # Get all activity logs
        logs = admin_service.get_platform_audit_log(limit=20)
        
        print(f"\n✓ Retrieved {len(logs)} activity log entries\n")
        
        # Check for enrichment fields
        program_events = []
        user_events = []
        
        for log in logs:
            print("-" * 80)
            print(f"Event Type: {log.get('event_type')}")
            print(f"Category: {log.get('category')}")
            print(f"Description: {log.get('description')}")
            print(f"User Email: {log.get('user_email')}")
            print(f"Display Name: {log.get('display_name', 'NOT SET')}")
            print(f"Organization Name: {log.get('organization_name', 'NOT SET')}")
            print(f"Target Username: {log.get('target_username', 'NOT SET')}")
            print(f"Actor Role: {log.get('actor_role', 'NOT SET')}")
            
            if log.get('category') == 'program':
                program_events.append(log)
            elif log.get('category') == 'user':
                user_events.append(log)
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total logs: {len(logs)}")
        print(f"Program events: {len(program_events)}")
        print(f"User events: {len(user_events)}")
        
        # Check if enrichment is working
        print("\n" + "=" * 80)
        print("ENRICHMENT VERIFICATION")
        print("=" * 80)
        
        program_with_org = sum(1 for e in program_events if e.get('organization_name'))
        user_with_username = sum(1 for e in user_events if e.get('target_username'))
        
        print(f"Program events with organization name: {program_with_org}/{len(program_events)}")
        print(f"User events with username: {user_with_username}/{len(user_events)}")
        
        # Display sample enriched events
        if program_events:
            print("\n" + "=" * 80)
            print("SAMPLE PROGRAM EVENT (should show org name)")
            print("=" * 80)
            sample = program_events[0]
            print(f"Event: {sample.get('event_type')}")
            print(f"Description: {sample.get('description')}")
            print(f"Display Name: {sample.get('display_name', 'NOT SET')}")
            print(f"Organization Name: {sample.get('organization_name', 'NOT SET')}")
            print(f"User Email: {sample.get('user_email')}")
        
        if user_events:
            print("\n" + "=" * 80)
            print("SAMPLE USER EVENT (should show username)")
            print("=" * 80)
            sample = user_events[0]
            print(f"Event: {sample.get('event_type')}")
            print(f"Description: {sample.get('description')}")
            print(f"Display Name: {sample.get('display_name', 'NOT SET')}")
            print(f"Target Username: {sample.get('target_username', 'NOT SET')}")
            print(f"User Email: {sample.get('user_email')}")
        
        print("\n" + "=" * 80)
        print("✓ TEST COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    success = test_activity_logs()
    sys.exit(0 if success else 1)
