"""
Setup organization wallet with initial balance for testing.
"""
import psycopg2
from uuid import uuid4

conn = psycopg2.connect(
    dbname="bug_bounty_production",
    user="bugbounty_user",
    password="changeme123",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

# Organization ID
org_id = '7c3b13e0-afb3-460b-b240-a74eb83e574c'

# Check if wallet exists
cur.execute("""
    SELECT wallet_id, balance FROM wallets 
    WHERE owner_id = %s AND owner_type = 'organization'
""", (org_id,))

wallet = cur.fetchone()

if wallet:
    print(f"✓ Wallet already exists: {wallet[0]}")
    print(f"  Current balance: {wallet[1]} ETB")
else:
    # Create wallet
    wallet_id = str(uuid4())
    initial_balance = 100000.00  # 100,000 ETB
    
    cur.execute("""
        INSERT INTO wallets (
            wallet_id,
            owner_id,
            owner_type,
            balance,
            reserved_balance,
            available_balance,
            currency
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        wallet_id,
        org_id,
        'organization',
        initial_balance,
        0.00,
        initial_balance,
        'ETB'
    ))
    
    # Create initial credit transaction
    tx_id = str(uuid4())
    cur.execute("""
        INSERT INTO wallet_transactions (
            transaction_id,
            wallet_id,
            transaction_type,
            amount,
            balance_before,
            balance_after,
            description,
            reference_type,
            saga_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        tx_id,
        wallet_id,
        'credit',
        initial_balance,
        0.00,
        initial_balance,
        'Initial wallet balance for testing',
        'initial_credit',
        str(uuid4())
    ))
    
    conn.commit()
    
    print(f"✓ Created wallet: {wallet_id}")
    print(f"  Initial balance: {initial_balance} ETB")
    print(f"  Transaction ID: {tx_id}")

cur.close()
conn.close()

print("\n✅ Organization wallet setup complete!")
