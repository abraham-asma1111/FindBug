#!/usr/bin/env python3
"""
Clean mock/test data from the database.
Removes audit logs and programs that were created for testing.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.audit_log import AuditLog
from src.domain.models.program import BountyProgram
from src.domain.models.security_log import SecurityEvent, LoginHistory

def clean_mock_data():
    """Remove mock/test data from database."""
    db: Session = SessionLocal()
    
    try:
        print("=" * 80)
        print("CLEANING MOCK DATA FROM DATABASE")
        print("=" * 80)
        
        # 1. Delete audit logs with missing target_id (mock data)
        print("\n1. Cleaning Audit Logs...")
        audit_logs = db.query(AuditLog).filter(
            AuditLog.target_id.is_(None)
        ).all()
        print(f"   Found {len(audit_logs)} audit logs with no target_id")
        for log in audit_logs:
            print(f"   - Deleting: {log.action_type} ({log.created_at})")
            db.delete(log)
        
        # 2. Delete mock programs (those with test names)
        print("\n2. Cleaning Mock Programs...")
        mock_program_names = [
            'gdefjkefjejd', 'gaqs', 'melkamu', 'second program',
            'hefdfkedfjj', 'BIT', 'BIT2'
        ]
        for name in mock_program_names:
            programs = db.query(BountyProgram).filter(
                BountyProgram.name == name
            ).all()
            for program in programs:
                print(f"   - Deleting program: {program.name}")
                db.delete(program)
        
        # 3. Delete old security events (keep only recent ones)
        print("\n3. Cleaning Old Security Events...")
        # Keep events from last 7 days, delete older ones
        from datetime import datetime, timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        old_events = db.query(SecurityEvent).filter(
            SecurityEvent.created_at < seven_days_ago
        ).all()
        print(f"   Found {len(old_events)} old security events (>7 days)")
        for event in old_events:
            db.delete(event)
        
        # 4. Delete old login history (keep only recent ones)
        print("\n4. Cleaning Old Login History...")
        old_logins = db.query(LoginHistory).filter(
            LoginHistory.created_at < seven_days_ago
        ).all()
        print(f"   Found {len(old_logins)} old login records (>7 days)")
        for login in old_logins:
            db.delete(login)
        
        # Commit all deletions
        db.commit()
        
        print("\n" + "=" * 80)
        print("✓ MOCK DATA CLEANED SUCCESSFULLY")
        print("=" * 80)
        
        # Show remaining counts
        print("\nRemaining data:")
        print(f"  - Audit Logs: {db.query(AuditLog).count()}")
        print(f"  - Programs: {db.query(BountyProgram).count()}")
        print(f"  - Security Events: {db.query(SecurityEvent).count()}")
        print(f"  - Login History: {db.query(LoginHistory).count()}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = clean_mock_data()
    sys.exit(0 if success else 1)
