#!/usr/bin/env python3
"""
Create Test Bounty Payments for Finance Portal
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.bounty_payment import BountyPayment
from src.domain.models.report import VulnerabilityReport
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization
from uuid import uuid4
from datetime import datetime, timedelta
from decimal import Decimal

def create_bounty_payments():
    """Create test bounty payments"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("CREATING TEST BOUNTY PAYMENTS FOR FINANCE PORTAL")
        print("=" * 80)
        
        # Get researchers
        researchers = db.query(Researcher).limit(5).all()
        if not researchers:
            print("❌ No researchers found. Run setup_finance_complete_data.py first")
            return
        
        # Get organizations
        organizations = db.query(Organization).limit(3).all()
        if not organizations:
            print("❌ No organizations found. Run setup_finance_complete_data.py first")
            return
        
        # Get valid reports
        reports = db.query(VulnerabilityReport).filter(
            VulnerabilityReport.status == 'valid'
        ).limit(10).all()
        
        if not reports:
            print("❌ No valid reports found. Creating some...")
            # Create some valid reports
            from src.domain.models.program import BugBountyProgram
            programs = db.query(BugBountyProgram).limit(3).all()
            
            if not programs:
                print("❌ No programs found. Cannot create reports.")
                return
            
            for i in range(10):
                report = VulnerabilityReport(
                    id=uuid4(),
                    program_id=programs[i % len(programs)].id,
                    researcher_id=researchers[i % len(researchers)].id,
                    title=f"Test Vulnerability Report #{i+1}",
                    description=f"This is a test vulnerability report for payment testing",
                    severity=["critical", "high", "medium", "low"][i % 4],
                    status="valid",
                    submitted_at=datetime.utcnow() - timedelta(days=30-i)
                )
                db.add(report)
            
            db.commit()
            reports = db.query(VulnerabilityReport).filter(
                VulnerabilityReport.status == 'valid'
            ).all()
            print(f"✅ Created {len(reports)} valid reports")
        
        # Create bounty payments with different statuses
        payment_configs = [
            # Pending payments (5)
            {"status": "pending", "amount": 5000, "count": 5},
            # Approved payments (3)
            {"status": "approved", "amount": 3000, "count": 3},
            # Completed payments (2)
            {"status": "completed", "amount": 2000, "count": 2},
        ]
        
        total_created = 0
        
        for config in payment_configs:
            for i in range(config["count"]):
                if total_created >= len(reports):
                    break
                
                report = reports[total_created]
                researcher_amount = Decimal(str(config["amount"] + (i * 500)))
                commission_amount = researcher_amount * Decimal("0.30")
                total_amount = researcher_amount + commission_amount
                
                payment = BountyPayment(
                    payment_id=uuid4(),
                    transaction_id=f"TXN-{uuid4().hex[:12].upper()}",
                    report_id=report.id,
                    researcher_id=report.researcher_id,
                    organization_id=report.program.organization_id if report.program else organizations[0].id,
                    researcher_amount=researcher_amount,
                    commission_amount=commission_amount,
                    total_amount=total_amount,
                    status=config["status"],
                    payment_method="telebirr" if i % 2 == 0 else "bank_transfer",
                    kyc_verified=True,
                    created_at=datetime.utcnow() - timedelta(days=20-i),
                    approved_at=datetime.utcnow() - timedelta(days=15-i) if config["status"] in ["approved", "completed"] else None,
                    payout_deadline=datetime.utcnow() + timedelta(days=30) if config["status"] == "pending" else None,
                    completed_at=datetime.utcnow() - timedelta(days=5-i) if config["status"] == "completed" else None
                )
                
                db.add(payment)
                total_created += 1
                
                print(f"✅ Created {config['status']} payment: {researcher_amount} ETB (+ {commission_amount} commission)")
        
        db.commit()
        
        # Verify
        pending_count = db.query(BountyPayment).filter(BountyPayment.status == 'pending').count()
        approved_count = db.query(BountyPayment).filter(BountyPayment.status == 'approved').count()
        completed_count = db.query(BountyPayment).filter(BountyPayment.status == 'completed').count()
        
        print("\n" + "=" * 80)
        print("✅ BOUNTY PAYMENTS CREATED SUCCESSFULLY!")
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"   • Pending Payments: {pending_count}")
        print(f"   • Approved Payments: {approved_count}")
        print(f"   • Completed Payments: {completed_count}")
        print(f"   • Total Payments: {total_created}")
        
        print(f"\n🎯 Test the Finance Portal:")
        print(f"   1. Login as finance officer (finance@findbug.com / Finance123!)")
        print(f"   2. Navigate to /finance/payments")
        print(f"   3. You should see {pending_count} pending payments")
        print(f"   4. Test approve/reject functionality")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_bounty_payments()
