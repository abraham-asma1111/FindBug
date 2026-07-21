import sys
import os
from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.bounty_payment import Wallet
from src.domain.models.user import User

def main():
    db = SessionLocal()
    try:
        print("--- Platform Wallets ---")
        platform_wallets = db.query(Wallet).filter(Wallet.owner_type == 'platform').all()
        for w in platform_wallets:
            print(f"Platform Wallet ID: {w.wallet_id}")
            print(f"Owner ID: {w.owner_id}")
            print(f"Balance: {w.balance} {w.currency}")
            print(f"Available Balance: {w.available_balance} {w.currency}")
            print("---")
            
        print("\n--- Researcher Wallets ---")
        researcher_wallets = db.query(Wallet).filter(Wallet.owner_type == 'researcher').limit(5).all()
        for w in researcher_wallets:
            if w.balance > 0:
                print(f"Researcher Wallet ID: {w.wallet_id}")
                print(f"Owner ID: {w.owner_id}")
                print(f"Balance: {w.balance} {w.currency}")
                print(f"Available Balance: {w.available_balance} {w.currency}")
                print("---")
            
    finally:
        db.close()

if __name__ == "__main__":
    main()
