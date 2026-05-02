"""
Check approved bounty payments for Finance Officer.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.bounty_payment import BountyPayment, Wallet
from src.domain.models.report import VulnerabilityReport
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization

def check_approved_bounties():
    """Check approved bounty payments."""
    db: Session = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("APPROVED BOUNTY PAYMENTS FOR FINANCE OFFICER")
        print("="*80)
        
        # Get all approved bounty payments
        print("\n[1] Finding approved bounty payments...")
        approved_bounties = db.query(BountyPayment).filter(
            BountyPayment.status == "approved"
        ).all()
        
        print(f"   Found {len(approved_bounties)} approved bounty payment(s)")
        
        if not approved_bounties:
            print("\n   No approved bounties found.")
            print("   Finance Officer has nothing to process yet.")
            return
        
        # Display each approved bounty
        for i, bounty in enumerate(approved_bounties, 1):
            print(f"\n[{i}] Bounty Payment Details:")
            print(f"   Payment ID: {bounty.payment_id}")
            print(f"   Transaction ID: {bounty.transaction_id}")
            print(f"   Status: {bounty.status}")
            
            # Get report details
            report = db.query(VulnerabilityReport).filter(
                VulnerabilityReport.id == bounty.report_id
            ).first()
            
            if report:
                print(f"\n   Report:")
                print(f"   - Report Number: {report.report_number}")
                print(f"   - Title: {report.title}")
                print(f"   - Severity: {report.assigned_severity}")
            
            # Get researcher details
            researcher = db.query(Researcher).filter(
                Researcher.id == bounty.researcher_id
            ).first()
            
            if researcher:
                print(f"\n   Researcher:")
                print(f"   - Username: {researcher.username}")
                print(f"   - ID: {researcher.id}")
            
            # Get organization details
            organization = db.query(Organization).filter(
                Organization.id == bounty.organization_id
            ).first()
            
            if organization:
                print(f"\n   Organization:")
                print(f"   - Name: {organization.company_name}")
                print(f"   - ID: {organization.id}")
            
            # Payment amounts
            print(f"\n   Payment Breakdown:")
            print(f"   - Researcher Amount: {bounty.researcher_amount} ETB")
            print(f"   - Commission (30%): {bounty.commission_amount} ETB")
            print(f"   - Total Paid by Org: {bounty.total_amount} ETB")
            
            # Dates
            print(f"\n   Timeline:")
            print(f"   - Approved At: {bounty.approved_at}")
            print(f"   - Created At: {bounty.created_at}")
        
        # Check platform wallet balance
        print(f"\n[2] Platform Wallet Status:")
        platform_wallet = db.query(Wallet).filter(
            Wallet.owner_type == "platform"
        ).first()
        
        if platform_wallet:
            print(f"   Balance: {platform_wallet.balance} ETB")
            print(f"   Available: {platform_wallet.available_balance} ETB")
            print(f"   Reserved: {platform_wallet.reserved_balance} ETB")
        else:
            print("   ❌ Platform wallet not found")
        
        print("\n" + "="*80)
        print("✅ Finance Officer can now process these approved bounties")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_approved_bounties()
