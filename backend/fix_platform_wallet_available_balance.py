#!/usr/bin/env python3
"""Fix platform wallet available_balance in database."""

import psycopg2

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
print("FIXING PLATFORM WALLET AVAILABLE BALANCE")
print("=" * 80)

# Get current wallet data
cursor.execute("""
    SELECT 
        wallet_id,
        balance,
        reserved_balance,
        available_balance
    FROM wallets
    WHERE owner_id = %s
""", (platform_owner_id,))

wallet = cursor.fetchone()

if wallet:
    wallet_id, balance, reserved_balance, available_balance = wallet
    
    print(f"\nCurrent State:")
    print(f"  Balance: {balance} ETB")
    print(f"  Reserved Balance: {reserved_balance} ETB")
    print(f"  Available Balance: {available_balance} ETB (INCORRECT)")
    
    # Calculate correct available balance
    correct_available_balance = balance - reserved_balance
    
    print(f"\nCorrect State:")
    print(f"  Balance: {balance} ETB")
    print(f"  Reserved Balance: {reserved_balance} ETB")
    print(f"  Available Balance: {correct_available_balance} ETB (CORRECT)")
    
    # Update the available_balance
    cursor.execute("""
        UPDATE wallets
        SET available_balance = balance - reserved_balance
        WHERE owner_id = %s
    """, (platform_owner_id,))
    
    conn.commit()
    
    print(f"\n✓ Updated available_balance from {available_balance} to {correct_available_balance} ETB")
    
    # Verify the fix
    cursor.execute("""
        SELECT balance, reserved_balance, available_balance
        FROM wallets
        WHERE owner_id = %s
    """, (platform_owner_id,))
    
    new_data = cursor.fetchone()
    print(f"\nVerification:")
    print(f"  Balance: {new_data[0]} ETB")
    print(f"  Reserved Balance: {new_data[1]} ETB")
    print(f"  Available Balance: {new_data[2]} ETB")
    
    if new_data[2] == correct_available_balance:
        print("\n✓ Fix successful!")
    else:
        print("\n✗ Fix failed!")
else:
    print("\n✗ Platform wallet not found!")

cursor.close()
conn.close()

print("\n" + "=" * 80)
