"""
Cleanup duplicate wallets for organization users.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.bounty_payment import Wallet, WalletTransaction
from decimal import Decimal

def cleanup_duplicates():
    """Cleanup duplicate wallets."""
    db: Session = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("CLEANUP DUPLICATE WALLETS")
        print("="*80)
        
        # Find user with duplicate wallets
        user_id = "5e6615eb-5d83-4882-a573-a0742c15b869"
        
        print(f"\n[1] Finding duplicate wallets for user {user_id}...")
        wallets = db.query(Wallet).filter(
            Wallet.owner_id == user_id,
            Wallet.owner_type == "organization"
        ).all()
        
        print(f"   Found {len(wallets)} wallets:")
        for w in wallets:
            print(f"   - Wallet {w.wallet_id}: Balance={w.balance}, Created={w.created_at}")
        
        if len(wallets) <= 1:
            print("\n✅ No duplicates found!")
            return
        
        # Calculate total balance
        total_balance = sum(w.balance for w in wallets)
        print(f"\n[2] Total balance across all wallets: {total_balance} ETB")
        
        # Keep the wallet with the highest balance (or oldest if tied)
        wallets_sorted = sorted(wallets, key=lambda w: (w.balance, w.created_at), reverse=True)
        wallet_to_keep = wallets_sorted[0]
        wallets_to_delete = wallets_sorted[1:]
        
        print(f"\n[3] Keeping wallet: {wallet_to_keep.wallet_id}")
        print(f"    Current balance: {wallet_to_keep.balance} ETB")
        print(f"    Will update to: {total_balance} ETB")
        
        # Move all transactions to the kept wallet
        print(f"\n[4] Moving transactions from duplicate wallets...")
        for wallet in wallets_to_delete:
            transactions = db.query(WalletTransaction).filter(
                WalletTransaction.wallet_id == wallet.wallet_id
            ).all()
            
            print(f"    Moving {len(transactions)} transactions from wallet {wallet.wallet_id}")
            for tx in transactions:
                tx.wallet_id = wallet_to_keep.wallet_id
        
        # Update the kept wallet balance
        wallet_to_keep.balance = total_balance
        wallet_to_keep.available_balance = total_balance - wallet_to_keep.reserved_balance
        
        # Delete duplicate wallets
        print(f"\n[5] Deleting {len(wallets_to_delete)} duplicate wallet(s)...")
        for wallet in wallets_to_delete:
            print(f"    Deleting wallet {wallet.wallet_id} (balance was {wallet.balance})")
            db.delete(wallet)
        
        # Commit changes
        db.commit()
        
        print(f"\n✅ Cleanup complete!")
        print(f"   Final wallet: {wallet_to_keep.wallet_id}")
        print(f"   Final balance: {wallet_to_keep.balance} ETB")
        
        # Verify
        print(f"\n[6] Verification...")
        remaining_wallets = db.query(Wallet).filter(
            Wallet.owner_id == user_id,
            Wallet.owner_type == "organization"
        ).all()
        print(f"   Remaining wallets: {len(remaining_wallets)}")
        for w in remaining_wallets:
            print(f"   - {w.wallet_id}: {w.balance} ETB")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_duplicates()
