import os
import sys
from decimal import Decimal
from uuid import UUID

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.database import SessionLocal
from src.domain.models.bounty_payment import BountyPayment, Wallet

def sync_platform_wallet():
    db = SessionLocal()
    try:
        # 1. Calculate actual commission sum from completed bounty payments
        completed_payments = db.query(BountyPayment).filter(
            BountyPayment.status == 'completed'
        ).all()
        
        total_commission = sum(p.commission_amount for p in completed_payments)
        print(f"Total calculated commission from {len(completed_payments)} completed payments: {total_commission} ETB")
        
        # 2. Get all platform wallets
        platform_wallets = db.query(Wallet).filter(
            Wallet.owner_type == 'platform'
        ).all()
        
        print(f"Found {len(platform_wallets)} platform wallets.")
        
        primary_owner_id = UUID('00000000-0000-0000-0000-000000000000')
        primary_wallet = None
        
        for w in platform_wallets:
            if w.owner_id == primary_owner_id:
                primary_wallet = w
                print(f"Primary platform wallet found. Current balance: {w.balance} ETB")
            else:
                print(f"Found secondary platform wallet (owner_id: {w.owner_id}). Current balance: {w.balance} ETB. Zeroing it out...")
                w.balance = Decimal('0.00')
                w.available_balance = Decimal('0.00')
                w.reserved_balance = Decimal('0.00')
        
        if primary_wallet:
            # 3. Update the primary wallet's balance to match the actual calculated commission
            print(f"Updating primary platform wallet balance to {total_commission} ETB...")
            primary_wallet.balance = total_commission
            primary_wallet.available_balance = total_commission
            primary_wallet.reserved_balance = Decimal('0.00')
        else:
            print("Primary platform wallet not found. Creating one...")
            primary_wallet = Wallet(
                owner_id=primary_owner_id,
                owner_type='platform',
                currency='ETB',
                balance=total_commission,
                available_balance=total_commission,
                reserved_balance=Decimal('0.00')
            )
            db.add(primary_wallet)
            
        db.commit()
        print("Successfully synced platform wallet!")
        
    except Exception as e:
        db.rollback()
        print(f"Error syncing platform wallet: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    sync_platform_wallet()
