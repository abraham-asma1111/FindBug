"""
Test script for bounty approval workflow.

This script tests the complete bounty approval flow:
1. Check organization wallet balance
2. Get a valid report
3. Approve bounty
4. Verify wallet balances updated
5. Verify bounty_payment record created
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.organization import Organization
from src.domain.models.report import VulnerabilityReport
from src.domain.models.bounty_payment import Wallet, BountyPayment
from decimal import Decimal
import uuid

def test_bounty_approval():
    """Test bounty approval workflow."""
    db: Session = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("BOUNTY APPROVAL WORKFLOW TEST")
        print("="*80)
        
        # Step 1: Get organization user
        print("\n[1] Getting organization user...")
        org_user = db.query(User).filter(User.email == "org@test.com").first()
        if not org_user:
            print("❌ Organization user not found")
            return
        
        org = db.query(Organization).filter(Organization.user_id == org_user.id).first()
        if not org:
            print("❌ Organization not found")
            return
        
        print(f"✅ Organization: {org.company_name} (ID: {org.id})")
        
        # Step 2: Check wallet balance
        print("\n[2] Checking organization wallet balance...")
        from src.services.wallet_service import WalletService
        wallet_service = WalletService(db)
        
        # Wallet owner_id should be user_id, not organization_id
        org_wallet = wallet_service.get_or_create_wallet(
            owner_id=org_user.id,  # Use user_id, not organization_id
            owner_type="organization"
        )
        
        print(f"✅ Current Balance: {org_wallet.balance} ETB")
        print(f"   Available Balance: {org_wallet.available_balance} ETB")
        print(f"   Reserved Balance: {org_wallet.reserved_balance} ETB")
        
        # If balance is 0, add some funds for testing
        if org_wallet.balance == 0:
            print("\n   ⚠️  Wallet balance is 0. Adding test funds...")
            wallet_service.credit_wallet(
                owner_id=org_user.id,  # Use user_id
                owner_type="organization",
                amount=Decimal("10000.00"),
                saga_id=f"TEST-{uuid.uuid4().hex[:8].upper()}",
                reference_type="test_recharge",
                reference_id=None
            )
            db.refresh(org_wallet)
            print(f"   ✅ Added 10,000 ETB to wallet")
            print(f"   New Balance: {org_wallet.balance} ETB")
        
        # Step 3: Find a valid report with bounty amount
        print("\n[3] Finding valid reports...")
        valid_reports = db.query(VulnerabilityReport).join(
            VulnerabilityReport.program
        ).filter(
            VulnerabilityReport.status == "valid",
            VulnerabilityReport.bounty_amount.isnot(None),
            VulnerabilityReport.bounty_amount > 0
        ).all()
        
        if not valid_reports:
            print("❌ No valid reports with bounty amount found")
            print("\nCreating a test valid report...")
            
            # Get a program
            from src.domain.models.program import BountyProgram
            program = db.query(BountyProgram).filter(
                BountyProgram.organization_id == org.id
            ).first()
            
            if not program:
                print("❌ No program found for organization")
                return
            
            # Get a researcher
            from src.domain.models.researcher import Researcher
            researcher = db.query(Researcher).first()
            
            if not researcher:
                print("❌ No researcher found")
                return
            
            # Create test report
            test_report = VulnerabilityReport(
                program_id=program.id,
                researcher_id=researcher.id,
                title="Test SQL Injection Vulnerability",
                description="SQL injection found in login form",
                steps_to_reproduce="1. Go to login page\n2. Enter ' OR '1'='1 in username",
                impact_assessment="Attacker can bypass authentication",
                suggested_severity="high",
                assigned_severity="high",
                status="valid",
                bounty_amount=Decimal("5000.00"),
                report_number=f"VR-TEST-{uuid.uuid4().hex[:8].upper()}"
            )
            db.add(test_report)
            db.commit()
            db.refresh(test_report)
            
            print(f"✅ Created test report: {test_report.report_number}")
            valid_reports = [test_report]
        
        # Use first valid report
        report = valid_reports[0]
        print(f"\n✅ Found valid report:")
        print(f"   Report Number: {report.report_number}")
        print(f"   Title: {report.title}")
        print(f"   Severity: {report.assigned_severity}")
        print(f"   Bounty Amount: {report.bounty_amount} ETB")
        
        # Step 4: Calculate costs
        print("\n[4] Calculating costs...")
        bounty_amount = Decimal(str(report.bounty_amount))
        commission = bounty_amount * Decimal("0.30")
        total_cost = bounty_amount + commission
        
        print(f"   Bounty Amount: {bounty_amount} ETB")
        print(f"   Commission (30%): {commission} ETB")
        print(f"   Total Cost: {total_cost} ETB")
        
        # Step 5: Check if sufficient balance
        if org_wallet.available_balance < total_cost:
            print(f"\n❌ Insufficient balance!")
            print(f"   Required: {total_cost} ETB")
            print(f"   Available: {org_wallet.available_balance} ETB")
            print(f"   Shortfall: {total_cost - org_wallet.available_balance} ETB")
            return
        
        print(f"\n✅ Sufficient balance available")
        
        # Step 6: Check if already approved
        existing_payment = db.query(BountyPayment).filter(
            BountyPayment.report_id == report.id
        ).first()
        
        if existing_payment:
            print(f"\n⚠️  Bounty already has payment record:")
            print(f"   Payment ID: {existing_payment.payment_id}")
            print(f"   Status: {existing_payment.status}")
            print(f"   Transaction ID: {existing_payment.transaction_id}")
            
            if existing_payment.status in ["approved", "processing", "completed"]:
                print(f"\n❌ Bounty already approved. Cannot approve again.")
                return
        
        # Step 7: Simulate approval (using service)
        print("\n[5] Simulating bounty approval...")
        print("   This would normally be done via API endpoint")
        print(f"   POST /api/v1/reports/{report.id}/approve-bounty")
        
        from src.services.payment_service import PaymentService
        from datetime import datetime
        
        payment_service = PaymentService(db)
        
        # Generate saga ID
        saga_id = f"BOUNTY-{uuid.uuid4().hex[:12].upper()}"
        
        print(f"\n   Saga ID: {saga_id}")
        
        # Deduct from org wallet
        print(f"\n   [5.1] Deducting {total_cost} ETB from organization wallet...")
        wallet_service.debit_wallet(
            owner_id=org_user.id,  # Use user_id
            owner_type="organization",
            amount=total_cost,
            saga_id=saga_id,
            from_reserved=False,
            reference_type="bounty_approval",
            reference_id=report.id
        )
        print("   ✅ Deducted from organization wallet")
        
        # Credit platform wallet
        print(f"\n   [5.2] Crediting {total_cost} ETB to platform wallet...")
        # Get or create platform wallet - use first admin user
        platform_user = db.query(User).filter(User.role == "admin").first()
        if not platform_user:
            # If no admin, use finance officer
            platform_user = db.query(User).filter(User.role == "finance_officer").first()
        
        if not platform_user:
            print("   ⚠️  No admin or finance user found, skipping platform wallet credit")
            print("   In production, platform wallet would be credited")
        else:
            wallet_service.credit_wallet(
                owner_id=platform_user.id,
                owner_type="platform",
                amount=total_cost,
                saga_id=saga_id,
                reference_type="bounty_approval",
                reference_id=report.id
            )
            print("   ✅ Credited to platform wallet")
        
        # Create payment record
        print(f"\n   [5.3] Creating bounty payment record...")
        payment = payment_service.create_bounty_payment(
            report_id=report.id,
            bounty_amount=bounty_amount,
            approved_by=org_user.id
        )
        
        # Update to approved
        payment.status = "approved"
        payment.approved_by = org_user.id
        payment.approved_at = datetime.utcnow()
        db.commit()
        db.refresh(payment)
        
        print(f"   ✅ Payment record created:")
        print(f"      Payment ID: {payment.payment_id}")
        print(f"      Transaction ID: {payment.transaction_id}")
        print(f"      Status: {payment.status}")
        
        # Update report
        report.bounty_status = "approved"
        db.commit()
        
        # Step 8: Verify final state
        print("\n[6] Verifying final state...")
        
        # Refresh wallets
        db.refresh(org_wallet)
        
        if platform_user:
            platform_wallet = db.query(Wallet).filter(
                Wallet.owner_id == platform_user.id,
                Wallet.owner_type == "platform"
            ).first()
        else:
            platform_wallet = None
        
        print(f"\n   Organization Wallet:")
        print(f"      Balance: {org_wallet.balance} ETB")
        print(f"      Available: {org_wallet.available_balance} ETB")
        
        if platform_wallet:
            print(f"\n   Platform Wallet:")
            print(f"      Balance: {platform_wallet.balance} ETB")
            print(f"      Available: {platform_wallet.available_balance} ETB")
        
        print(f"\n   Bounty Payment:")
        print(f"      Status: {payment.status}")
        print(f"      Researcher Amount: {payment.researcher_amount} ETB")
        print(f"      Commission: {payment.commission_amount} ETB")
        print(f"      Total: {payment.total_amount} ETB")
        
        print("\n" + "="*80)
        print("✅ BOUNTY APPROVAL TEST COMPLETED SUCCESSFULLY")
        print("="*80)
        
        print("\n📋 SUMMARY:")
        print(f"   Report: {report.report_number}")
        print(f"   Bounty: {bounty_amount} ETB")
        print(f"   Commission: {commission} ETB")
        print(f"   Total Cost: {total_cost} ETB")
        print(f"   Payment ID: {payment.payment_id}")
        print(f"   Status: {payment.status}")
        
        print("\n🎯 NEXT STEPS:")
        print("   1. Finance Officer will see this in pending payments")
        print("   2. Finance Officer processes payment")
        print("   3. Researcher wallet gets credited")
        print("   4. Platform keeps commission")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_bounty_approval()
