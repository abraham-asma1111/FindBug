#!/usr/bin/env python3
"""
Test wallet endpoint directly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.user import User
from src.services.wallet_service import WalletService

def test_wallet_service():
    """Test WalletService directly."""
    db: Session = SessionLocal()
    
    try:
        # Get researcher user
        user = db.query(User).filter(User.email == "foyihob867@justnapa.com").first()
        
        if not user:
            print("❌ User not found")
            return
        
        print(f"✅ Found user: {user.email}")
        print(f"   User ID: {user.id}")
        print(f"   Role: {user.role}")
        
        # Test WalletService
        print(f"\n🔧 Testing WalletService...")
        service = WalletService(db)
        
        # Test get_balance
        print(f"\n📊 Getting balance...")
        try:
            balance = service.get_balance(user.id, "researcher")
            print(f"✅ Balance retrieved successfully:")
            print(f"   Balance: {balance['balance']} ETB")
            print(f"   Available: {balance['available_balance']} ETB")
            print(f"   Reserved: {balance['reserved_balance']} ETB")
        except Exception as e:
            print(f"❌ Error getting balance: {e}")
            import traceback
            traceback.print_exc()
        
        # Test get_transaction_history
        print(f"\n📜 Getting transaction history...")
        try:
            transactions = service.get_transaction_history(user.id, "researcher", limit=10, offset=0)
            print(f"✅ Transactions retrieved: {len(transactions)} transactions")
        except Exception as e:
            print(f"❌ Error getting transactions: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_wallet_service()
