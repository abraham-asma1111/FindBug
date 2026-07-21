"""Test payout approval workflow."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from uuid import UUID

load_dotenv()

# Setup database
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    from src.services.payment_service import PaymentService
    from src.domain.models.user import User
    
    # Get finance officer user
    finance_user = db.query(User).filter(User.email == "finance@findbug.com").first()
    if not finance_user:
        print("❌ Finance officer not found")
        exit(1)
    
    print(f"✅ Finance Officer: {finance_user.email} (ID: {finance_user.id})")
    
    # Get first pending payout
    from src.domain.models.payment_extended import PayoutRequest
    pending_payout = db.query(PayoutRequest).filter(
        PayoutRequest.status == "pending"
    ).first()
    
    if not pending_payout:
        print("❌ No pending payouts found")
        exit(1)
    
    print(f"\n📋 Pending Payout:")
    print(f"   ID: {pending_payout.id}")
    print(f"   Amount: {pending_payout.amount} ETB")
    print(f"   Status: {pending_payout.status}")
    
    # Check researcher wallet balance before
    from src.domain.models.bounty_payment import Wallet
    from src.domain.models.researcher import Researcher
    
    researcher = db.query(Researcher).filter(
        Researcher.id == pending_payout.researcher_id
    ).first()
    
    wallet = db.query(Wallet).filter(
        Wallet.owner_id == researcher.user_id,
        Wallet.owner_type == "researcher"
    ).first()
    
    print(f"\n💰 Wallet Before:")
    print(f"   Balance: {wallet.balance} ETB")
    print(f"   Reserved: {wallet.reserved_balance} ETB")
    print(f"   Available: {wallet.balance - wallet.reserved_balance} ETB")
    
    # Approve payout
    payment_service = PaymentService(db)
    
    print(f"\n🔄 Approving payout...")
    approved_payout = payment_service.approve_payout_request(
        payout_id=pending_payout.id,
        approved_by=finance_user.id
    )
    
    print(f"\n✅ Payout Approved!")
    print(f"   Status: {approved_payout.status}")
    print(f"   Processed At: {approved_payout.processed_at}")
    
    # Refresh wallet
    db.refresh(wallet)
    
    print(f"\n💰 Wallet After:")
    print(f"   Balance: {wallet.balance} ETB")
    print(f"   Reserved: {wallet.reserved_balance} ETB")
    print(f"   Available: {wallet.balance - wallet.reserved_balance} ETB")
    
    print(f"\n✅ Test completed successfully!")
    print(f"   Payout should now appear in the 'Completed' tab")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
