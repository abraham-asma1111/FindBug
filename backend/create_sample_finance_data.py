"""Create Sample Finance Data for Testing"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from src.core.database import get_db
from src.domain.models.bounty_payment import BountyPayment, Wallet, WalletTransaction
from src.domain.models.report import VulnerabilityReport
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization
from src.domain.models.user import User

def create_sample_data():
    """Create sample finance data"""
    db = next(get_db())
    
    try:
        # Get existing researcher and organization
        researcher = db.query(Researcher).first()
        organization = db.query(Organization).first()
        
        if not researcher or not organization:
            print("❌ Need at least one researcher and organization")
            return
        
        # Get a report
        report = db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher.id
        ).first()
        
        if not report:
            print("❌ No reports found for researcher")
            return
        
        # Create bounty payment
        payment = BountyPayment(
            payment_id=uuid4(),
            transaction_id=f"TXN-{uuid4().hex[:12].upper()}",
            report_id=report.id,
            researcher_id=researcher.id,
            organization_id=organization.id,
            researcher_amount=Decimal("5000.00"),
            commission_amount=Decimal("1500.00"),  # 30%
            total_amount=Decimal("6500.00"),
            status="pending",
            kyc_verified=True,
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        
        db.add(payment)
        
        # Create researcher wallet if doesn't exist
        wallet = db.query(Wallet).filter(
            Wallet.owner_id == researcher.user_id,
            Wallet.owner_type == "researcher"
        ).first()
        
        if not wallet:
            wallet = Wallet(
                wallet_id=uuid4(),
                owner_id=researcher.user_id,
                owner_type="researcher",
                balance=Decimal("15000.00"),
                reserved_balance=Decimal("0.00"),
                available_balance=Decimal("15000.00"),
                currency="ETB"
            )
            db.add(wallet)
        
        # Create wallet transaction
        transaction = WalletTransaction(
            transaction_id=uuid4(),
            wallet_id=wallet.wallet_id,
            transaction_type="credit",
            amount=Decimal("5000.00"),
            balance_before=Decimal("10000.00"),
            balance_after=Decimal("15000.00"),
            reference_type="bounty_payment",
            reference_id=payment.payment_id,
            description="Bounty payment for vulnerability report",
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        
        db.add(transaction)
        
        db.commit()
        
        print("✅ Sample finance data created successfully")
        print(f"   Payment ID: {payment.payment_id}")
        print(f"   Amount: ${payment.researcher_amount}")
        print(f"   Commission: ${payment.commission_amount}")
        print(f"   Total: ${payment.total_amount}")
        print(f"   Status: {payment.status}")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
