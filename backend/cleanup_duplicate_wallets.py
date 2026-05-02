"""Clean up duplicate wallets - keep the one with the highest balance."""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/bugbounty')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

print("=" * 60)
print("CLEANING UP DUPLICATE WALLETS")
print("=" * 60)

# Find duplicate wallets (same owner_id and owner_type)
print("\n1. Finding duplicate wallets...")
result = session.execute(text("""
    SELECT owner_id, owner_type, COUNT(*) as count
    FROM wallets
    GROUP BY owner_id, owner_type
    HAVING COUNT(*) > 1
"""))
duplicates = result.fetchall()

print(f"Found {len(duplicates)} owners with duplicate wallets")

for owner_id, owner_type, count in duplicates:
    print(f"\n  Owner: {owner_id}, Type: {owner_type}, Duplicates: {count}")
    
    # Get all wallets for this owner
    result = session.execute(text(f"""
        SELECT wallet_id, balance, available_balance, reserved_balance, created_at
        FROM wallets
        WHERE owner_id = '{owner_id}' AND owner_type = '{owner_type}'
        ORDER BY balance DESC, created_at DESC
    """))
    wallets = result.fetchall()
    
    # Keep the wallet with the highest balance (or most recent if all have same balance)
    keep_wallet = wallets[0]
    delete_wallets = wallets[1:]
    
    print(f"  Keeping wallet: {keep_wallet[0]} (Balance: {keep_wallet[1]})")
    
    for wallet in delete_wallets:
        wallet_id = wallet[0]
        balance = wallet[1]
        
        # Check if this wallet has any transactions
        tx_result = session.execute(text(f"""
            SELECT COUNT(*) FROM wallet_transactions WHERE wallet_id = '{wallet_id}'
        """))
        tx_count = tx_result.fetchone()[0]
        
        if tx_count > 0:
            print(f"  ⚠️  Wallet {wallet_id} has {tx_count} transactions - moving to kept wallet")
            
            # Move transactions to the kept wallet
            session.execute(text(f"""
                UPDATE wallet_transactions
                SET wallet_id = '{keep_wallet[0]}'
                WHERE wallet_id = '{wallet_id}'
            """))
        
        # Delete the duplicate wallet
        print(f"  Deleting wallet: {wallet_id} (Balance: {balance})")
        session.execute(text(f"""
            DELETE FROM wallets WHERE wallet_id = '{wallet_id}'
        """))

session.commit()

print("\n2. Verifying cleanup...")
result = session.execute(text("""
    SELECT owner_id, owner_type, COUNT(*) as count
    FROM wallets
    GROUP BY owner_id, owner_type
    HAVING COUNT(*) > 1
"""))
remaining_duplicates = result.fetchall()

if remaining_duplicates:
    print(f"❌ Still have {len(remaining_duplicates)} owners with duplicates")
else:
    print("✅ All duplicate wallets cleaned up!")

print("\n3. Final wallet count...")
result = session.execute(text("SELECT COUNT(*) FROM wallets"))
total_wallets = result.fetchone()[0]
print(f"Total wallets: {total_wallets}")

session.close()

print("\n" + "=" * 60)
print("CLEANUP COMPLETE")
print("=" * 60)
