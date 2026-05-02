"""Test platform wallet commission accumulation."""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from uuid import UUID
from decimal import Decimal

load_dotenv()

# Setup database
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    from src.services.payment_service import PaymentService
    from src.domain.models.user import User
    from src.domain.models.bounty_payment import BountyPayment, Wallet
    
    # Platform wallet ID
    platform_owner_id = UUID('00000000-0000-0000-0000-000000000000')
    
    print("=" * 70)
    print("PLATFORM WALLET COMMISSION TEST")
    print("=" * 70)
    
    # Check if platform wallet exists
    platform_wallet = db.query(Wallet).filter(
        Wallet.owner_id == platform_owner_id,
        Wallet.owner_type == "platform"
    ).first()
    
    if platform_wallet:
        print(f"\n✅ Platform Wallet Found:")
        print(f"   Wallet ID: {platform_wallet.wallet_id}")
        print(f"   Balance: {platform_wallet.balance} ETB")
        print(f"   Currency: {platform_wallet.currency}")
    else:
        print(f"\n⚠️  Platform wallet doesn't exist yet (will be created on first commission)")
    
    # Get a pending bounty payment to approve
    pending_payment = db.query(BountyPayment).filter(
        BountyPayment.status == "pending"
    ).first()
    
    if not pending_payment:
        print("\n❌ No pending bounty payments found")
        print("   Create a bounty payment first to test commission accumulation")
        exit(0)
    
    print(f"\n📋 Pending Bounty Payment:")
    print(f"   Payment ID: {pending_payment.payment_id}")
    print(f"   Researcher Amount: {pending_payment.researcher_amount} ETB")
    print(f"   Commission Amount: {pending_payment.commission_amount} ETB")
    print(f"   Total Amount: {pending_payment.total_amount} ETB")
    print(f"   Status: {pending_payment.status}")
    
    # Get finance officer
    finance_user = db.query(User).filter(User.email == "finance@findbug.com").first()
    if not finance_user:
        print("\n❌ Finance officer not found")
        exit(1)
    
    print(f"\n👤 Finance Officer: {finance_user.email}")
    
    # Record platform wallet balance before
    balance_before = platform_wallet.balance if platform_wallet else Decimal("0.00")
    
    print(f"\n💰 Platform Wallet Before Approval:")
    print(f"   Balance: {balance_before} ETB")
    
    # Approve the payment
    payment_service = PaymentService(db)
    
    print(f"\n🔄 Approving bounty payment...")
    
    try:
        approved_payment = payment_service.approve_bounty_payment(
            payment_id=pending_payment.payment_id,
            approved_by=finance_user.id
        )
        
        print(f"\n✅ Bounty Payment Approved!")
        print(f"   Status: {approved_payment.status}")
        
        # Check platform wallet after
        db.refresh(platform_wallet) if platform_wallet else None
        platform_wallet = db.query(Wallet).filter(
            Wallet.owner_id == platform_owner_id,
            Wallet.owner_type == "platform"
        ).first()
        
        if platform_wallet:
            balance_after = platform_wallet.balance
            commission_received = balance_after - balance_before
            
            print(f"\n💰 Platform Wallet After Approval:")
            print(f"   Balance: {balance_after} ETB")
            print(f"   Commission Received: +{commission_received} ETB")
            
            if commission_received == pending_payment.commission_amount:
                print(f"\n✅ SUCCESS! Commission correctly credited to platform wallet")
            else:
                print(f"\n⚠️  WARNING: Commission mismatch!")
                print(f"   Expected: {pending_payment.commission_amount} ETB")
                print(f"   Received: {commission_received} ETB")
        else:
            print(f"\n❌ Platform wallet not found after approval")
        
        # Show platform wallet transactions
        result = db.execute(text("""
            SELECT transaction_id, transaction_type, amount, balance_after, description, created_at
            FROM wallet_transactions
            WHERE wallet_id = (
                SELECT wallet_id FROM wallets 
                WHERE owner_id = '00000000-0000-0000-0000-000000000000' 
                AND owner_type = 'platform'
            )
            ORDER BY created_at DESC
            LIMIT 5
        """))
        
        print(f"\n📊 Recent Platform Wallet Transactions:")
        for row in result:
            print(f"   {row[1].upper()}: {row[2]} ETB → Balance: {row[3]} ETB")
            print(f"   Description: {row[4]}")
            print(f"   Time: {row[5]}")
            print()
        
    except Exception as e:
        print(f"\n❌ Error approving payment: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
