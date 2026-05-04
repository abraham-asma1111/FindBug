#!/usr/bin/env python3
"""Check platform wallet data in database."""

import psycopg2
from uuid import UUID

# Database connection
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="bug_bounty_production",
    user="bugbounty_user",
    password="changeme123"
)

cursor = conn.cursor()

# Platform wallet owner ID
platform_owner_id = '00000000-0000-0000-0000-000000000000'

print("=" * 80)
print("PLATFORM WALLET DATA")
print("=" * 80)

# Check wallet record
cursor.execute("""
    SELECT 
        wallet_id,
        owner_id,
        owner_type,
        balance,
        reserved_balance,
        available_balance,
        currency,
        created_at
    FROM wallets
    WHERE owner_id = %s
""", (platform_owner_id,))

wallet = cursor.fetchone()
if wallet:
    print("\n✓ Platform Wallet Found:")
    print(f"  Wallet ID: {wallet[0]}")
    print(f"  Owner ID: {wallet[1]}")
    print(f"  Owner Type: {wallet[2]}")
    print(f"  Balance: {wallet[3]} {wallet[6]}")
    print(f"  Reserved Balance: {wallet[4]} {wallet[6]}")
    print(f"  Available Balance: {wallet[5]} {wallet[6]}")
    print(f"  Created: {wallet[7]}")
    
    wallet_id = wallet[0]
    
    # Check transactions
    print("\n" + "=" * 80)
    print("PLATFORM WALLET TRANSACTIONS")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            transaction_id,
            transaction_type,
            amount,
            balance_before,
            balance_after,
            description,
            created_at
        FROM wallet_transactions
        WHERE wallet_id = %s
        ORDER BY created_at DESC
    """, (wallet_id,))
    
    transactions = cursor.fetchall()
    print(f"\nTotal Transactions: {len(transactions)}")
    
    for i, tx in enumerate(transactions, 1):
        print(f"\n{i}. Transaction {tx[0]}")
        print(f"   Type: {tx[1]}")
        print(f"   Amount: {tx[2]} ETB")
        print(f"   Balance Before: {tx[3]} ETB")
        print(f"   Balance After: {tx[4]} ETB")
        print(f"   Description: {tx[5]}")
        print(f"   Created: {tx[6]}")
    
    # Calculate expected balance
    print("\n" + "=" * 80)
    print("BALANCE VERIFICATION")
    print("=" * 80)
    
    cursor.execute("""
        SELECT SUM(amount) 
        FROM wallet_transactions
        WHERE wallet_id = %s AND transaction_type = 'credit'
    """, (wallet_id,))
    
    total_credits = cursor.fetchone()[0] or 0
    
    cursor.execute("""
        SELECT SUM(amount) 
        FROM wallet_transactions
        WHERE wallet_id = %s AND transaction_type = 'debit'
    """, (wallet_id,))
    
    total_debits = cursor.fetchone()[0] or 0
    
    expected_balance = total_credits - total_debits
    
    print(f"\nTotal Credits: {total_credits} ETB")
    print(f"Total Debits: {total_debits} ETB")
    print(f"Expected Balance: {expected_balance} ETB")
    print(f"Actual Balance: {wallet[3]} ETB")
    print(f"Actual Available Balance: {wallet[5]} ETB")
    
    if expected_balance == wallet[3]:
        print("\n✓ Balance is CORRECT")
    else:
        print(f"\n✗ Balance MISMATCH! Difference: {expected_balance - wallet[3]} ETB")
    
    if wallet[3] == wallet[5]:
        print("✓ Available Balance matches Balance (no reserved funds)")
    else:
        print(f"✗ Available Balance MISMATCH! Should be {wallet[3]} but is {wallet[5]}")
        print(f"  Reserved Balance: {wallet[4]} ETB")
        print(f"  Expected Available: {wallet[3] - wallet[4]} ETB")

else:
    print("\n✗ Platform wallet not found!")

cursor.close()
conn.close()

print("\n" + "=" * 80)
