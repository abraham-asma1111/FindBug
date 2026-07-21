"""
Check wallet for current logged-in user.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.bounty_payment import Wallet, WalletTransaction

def check_wallet():
    """Check wallet balance for current user."""
    db: Session = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("CURRENT USER WALLET CHECK")
        print("="*80)
        
        # Get user by ID (from screenshot context)
        user_id = "5e6615eb-5d83-4882-a573-a0742c15b869"
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"❌ User {user_id} not found")
            return
        
        print(f"\n✅ User:")
        print(f"   Email: {user.email}")
        print(f"   User ID: {user.id}")
        print(f"   Role: {user.role}")
        
        # Check wallets
        print(f"\n📊 Checking wallets for user_id={user.id}...")
        wallets = db.query(Wallet).filter(Wallet.owner_id == user.id).all()
        
        if not wallets:
            print("   ❌ No wallets found for this user")
        else:
            print(f"   ✅ Found {len(wallets)} wallet(s):")
            for wallet in wallets:
                print(f"\n   Wallet ID: {wallet.wallet_id}")
                print(f"   Owner Type: {wallet.owner_type}")
                print(f"   Balance: {wallet.balance} {wallet.currency}")
                print(f"   Available: {wallet.available_balance} {wallet.currency}")
                print(f"   Reserved: {wallet.reserved_balance} {wallet.currency}")
                print(f"   Created: {wallet.created_at}")
                
                # Get recent transactions
                transactions = db.query(WalletTransaction).filter(
                    WalletTransaction.wallet_id == wallet.wallet_id
                ).order_by(WalletTransaction.created_at.desc()).limit(5).all()
                
                if transactions:
                    print(f"\n   Recent Transactions ({len(transactions)}):")
                    for tx in transactions:
                        print(f"      - {tx.transaction_type}: {tx.amount} {wallet.currency}")
                        print(f"        Balance After: {tx.balance_after}")
                        print(f"        Reference: {tx.reference_type}")
                        print(f"        Created: {tx.created_at}")
                else:
                    print(f"\n   No transactions found")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_wallet()
