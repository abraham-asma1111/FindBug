#!/usr/bin/env python3
"""
Complete Payment Workflow Setup
Sets up payment methods, creates test bounty payments, and verifies the entire workflow.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.services.payment_service import PaymentService
from src.services.kyc_service import KYCService
from src.domain.models.user import User
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization
from src.domain.models.report import VulnerabilityReport
from src.domain.models.bounty_payment import BountyPayment, Wallet
from src.domain.models.payment_extended import PaymentMethod
from decimal import Decimal
from datetime import datetime

def setup_complete_workflow():
    """Setup complete payment workflow with test data."""
    db: Session = SessionLocal()
    
    try:
        print("=" * 80)
        print("COMPLETE PAYMENT WORKFLOW SETUP")
        print("=" * 80)
        
        # 1. Get researcher user
        researcher_user = db.query(User).filter(User.email == "foyihob867@justnapa.com").first()
        if not researcher_user:
            print("❌ Researcher user not found")
            return
        
        print(f"\n✅ Found researcher: {researcher_user.email} (ID: {researcher_user.id})")
        
        # 2. Check KYC status
        kyc_service = KYCService(db)
        kyc_status = kyc_service.get_kyc_status(str(researcher_user.id))
        print(f"\n📋 KYC Status: {kyc_status['status']}")
        
        if kyc_status["status"] != "approved":
            print(f"⚠️  KYC not approved. Please complete KYC first.")
            return
        
        # 3. Setup payment methods
        payment_service = PaymentService(db)
        
        # Check existing payment methods
        existing_methods = payment_service.get_user_payment_methods(str(researcher_user.id))
        print(f"\n💳 Existing Payment Methods: {len(existing_methods)}")
        
        if len(existing_methods) == 0:
            print("\n➕ Adding payment methods...")
            
            # Add Ethiopian bank account
            bank_method = payment_service.add_payment_method(str(researcher_user.id), {
                "method_type": "bank_account",
                "account_name": "Test Researcher",
                "account_number": "1000123456789",
                "bank_name": "Commercial Bank of Ethiopia",
                "is_default": True
            })
            print(f"   ✅ Bank Account: {bank_method.bank_name} - ****{bank_method.account_number[-4:]}")
            
            # Add Telebirr
            telebirr_method = payment_service.add_payment_method(str(researcher_user.id), {
                "method_type": "mobile_money",
                "account_name": "Test Researcher",
                "phone_number": "+251912345678",
                "account_number": "0912345678",
                "is_default": False
            })
            print(f"   ✅ Telebirr: {telebirr_method.phone_number}")
            
            existing_methods = payment_service.get_user_payment_methods(str(researcher_user.id))
        
        # Display all payment methods
        print(f"\n💳 Total Payment Methods: {len(existing_methods)}")
        for method in existing_methods:
            default_badge = " [DEFAULT]" if method.is_default else ""
            verified_badge = " [VERIFIED]" if method.is_verified else " [PENDING]"
            print(f"   - {method.method_type}: {method.account_name}{default_badge}{verified_badge}")
        
        # 4. Check researcher wallet
        researcher = db.query(Researcher).filter(Researcher.user_id == researcher_user.id).first()
        if not researcher:
            print("\n❌ Researcher profile not found")
            return
        
        wallet = db.query(Wallet).filter(
            Wallet.owner_id == researcher_user.id,
            Wallet.owner_type == "researcher"
        ).first()
        
        if wallet:
            print(f"\n💰 Wallet Balance: {wallet.balance} ETB")
            print(f"   Available: {wallet.available_balance} ETB")
            print(f"   Reserved: {wallet.reserved_balance} ETB")
        else:
            print("\n⚠️  No wallet found for researcher")
        
        # 5. Check for pending bounty payments
        pending_payments = db.query(BountyPayment).filter(
            BountyPayment.researcher_id == researcher.id,
            BountyPayment.status.in_(["pending", "approved"])
        ).all()
        
        print(f"\n💵 Pending Bounty Payments: {len(pending_payments)}")
        for payment in pending_payments:
            print(f"   - Payment ID: {payment.payment_id}")
            print(f"     Amount: {payment.researcher_amount} ETB")
            print(f"     Status: {payment.status}")
            print(f"     Report ID: {payment.report_id}")
        
        # 6. Get a valid report for testing (if needed)
        valid_report = db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher.id,
            VulnerabilityReport.status == "valid"
        ).first()
        
        if valid_report:
            print(f"\n📝 Found valid report for testing: {valid_report.id}")
            print(f"   Title: {valid_report.title}")
            print(f"   Severity: {valid_report.severity}")
            
            # Check if payment already exists for this report
            existing_payment = db.query(BountyPayment).filter(
                BountyPayment.report_id == valid_report.id
            ).first()
            
            if not existing_payment:
                print("\n   Creating test bounty payment...")
                # Get organization for the report
                org = db.query(Organization).filter(
                    Organization.id == valid_report.program.organization_id
                ).first()
                
                if org:
                    # Create bounty payment
                    test_payment = payment_service.create_bounty_payment(
                        report_id=valid_report.id,
                        bounty_amount=Decimal("5000.00"),  # 5000 ETB bounty
                        approved_by=researcher_user.id  # Using researcher as approver for testing
                    )
                    print(f"   ✅ Created bounty payment: {test_payment.payment_id}")
                    print(f"      Researcher Amount: {test_payment.researcher_amount} ETB")
                    print(f"      Commission: {test_payment.commission_amount} ETB")
                    print(f"      Total (Org Pays): {test_payment.total_amount} ETB")
                    print(f"      Status: {test_payment.status}")
        
        print("\n" + "=" * 80)
        print("SETUP COMPLETE!")
        print("=" * 80)
        print("\n📌 Next Steps:")
        print("   1. Login as Finance Officer")
        print("   2. Navigate to Finance Portal → Payments")
        print("   3. Approve pending bounty payments")
        print("   4. Process payouts to researcher")
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    setup_complete_workflow()
