#!/usr/bin/env python3
"""
Fix researcher wallet - Create wallet if it doesn't exist
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.user import User
from src.domain.models.bounty_payment import Wallet
from decimal import Decimal

def fix_researcher_wallet():
    """Create wallet for researcher if it doesn't exist."""
    db: Session = SessionLocal()
    
    try:
        # Get researcher user
        user = db.query(User).filter(User.email == "foyihob867@justnapa.com").first()
        
        if not user:
            print("❌ User not found")
            return
        
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        print(f"   Role: {user.role}")
        
        # Check if wallet exists
        wallet = db.query(Wallet).filter(
            Wallet.owner_id == user.id,
            Wallet.owner_type == "researcher"
        ).first()
        
        if wallet:
            print(f"\n✅ Wallet already exists:")
            print(f"   Wallet ID: {wallet.wallet_id}")
            print(f"   Balance: {wallet.balance} ETB")
            print(f"   Available: {wallet.available_balance} ETB")
            print(f"   Reserved: {wallet.reserved_balance} ETB")
        else:
            print(f"\n⚠️  No wallet found. Creating wallet...")
            
            # Create wallet
            wallet = Wallet(
                owner_id=user.id,
                owner_type="researcher",
                balance=Decimal("0.00"),
                reserved_balance=Decimal("0.00"),
                available_balance=Decimal("0.00"),
                currency="ETB"
            )
            
            db.add(wallet)
            db.commit()
            db.refresh(wallet)
            
            print(f"✅ Wallet created successfully!")
            print(f"   Wallet ID: {wallet.wallet_id}")
            print(f"   Balance: {wallet.balance} ETB")
        
        print("\n" + "=" * 60)
        print("WALLET SETUP COMPLETE!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_researcher_wallet()
