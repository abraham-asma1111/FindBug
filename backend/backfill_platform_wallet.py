"""
Backfill platform wallet with commissions from completed bounty payments.

This script credits the platform wallet with commissions from bounty payments
that were completed before the platform wallet feature was implemented.
"""
import sys
sys.path.insert(0, '/home/abraham/findbug-backend-frontend/backend')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
from uuid import UUID
import uuid

DATABASE_URL = 'postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Platform wallet owner ID
PLATFORM_OWNER_ID = UUID('00000000-0000-0000-0000-000000000000')

print("=== BACKFILLING PLATFORM WALLET ===\n")

# Get platform wallet
result = session.execute(text("""
    SELECT wallet_id, balance, reserved_balance
    FROM wallets
    WHERE owner_id = :owner_id
"""), {"owner_id": str(PLATFORM_OWNER_ID)})

platform_wallet = result.fetchone()

if not platform_wallet:
    print("ERROR: Platform wallet not found!")
    session.close()
    sys.exit(1)

print(f"Platform Wallet ID: {platform_wallet.wallet_id}")
print(f"Current Balance: {platform_wallet.balance} ETB")
print(f"Reserved Balance: {platform_wallet.reserved_balance} ETB\n")

# Get completed bounty payments that don't have platform wallet transactions
result = session.execute(text("""
    SELECT 
        bp.payment_id,
        bp.transaction_id,
        bp.commission_amount,
        bp.completed_at,
        bp.created_at
    FROM bounty_payments bp
    WHERE bp.status = 'completed'
    AND NOT EXISTS (
        SELECT 1 FROM wallet_transactions wt
        WHERE wt.wallet_id = :wallet_id
        AND wt.reference_type = 'commission'
        AND wt.reference_id = bp.payment_id
    )
    ORDER BY bp.created_at ASC
"""), {"wallet_id": platform_wallet.wallet_id})

payments_to_backfill = result.fetchall()

if not payments_to_backfill:
    print("No payments to backfill. Platform wallet is up to date!")
    session.close()
    sys.exit(0)

print(f"Found {len(payments_to_backfill)} completed payments to backfill:\n")

total_backfill = Decimal('0')
current_balance = Decimal(str(platform_wallet.balance))

for payment in payments_to_backfill:
    print(f"Payment ID: {payment.payment_id}")
    print(f"  Transaction ID: {payment.transaction_id}")
    print(f"  Commission: {payment.commission_amount} ETB")
    print(f"  Completed: {payment.completed_at}")
    total_backfill += Decimal(str(payment.commission_amount))

print(f"\nTotal to backfill: {total_backfill} ETB")
print(f"New balance will be: {current_balance + total_backfill} ETB\n")

# Confirm
response = input("Proceed with backfill? (yes/no): ")
if response.lower() != 'yes':
    print("Backfill cancelled.")
    session.close()
    sys.exit(0)

print("\nBackfilling platform wallet...\n")

# Process each payment
for payment in payments_to_backfill:
    commission = Decimal(str(payment.commission_amount))
    balance_before = current_balance
    current_balance += commission
    
    # Create wallet transaction
    transaction_id = uuid.uuid4()
    
    session.execute(text("""
        INSERT INTO wallet_transactions (
            transaction_id,
            wallet_id,
            transaction_type,
            amount,
            balance_before,
            balance_after,
            reference_type,
            reference_id,
            saga_id,
            compensated,
            description,
            created_at
        ) VALUES (
            :transaction_id,
            :wallet_id,
            'credit',
            :amount,
            :balance_before,
            :balance_after,
            'commission',
            :reference_id,
            :saga_id,
            false,
            :description,
            :created_at
        )
    """), {
        "transaction_id": str(transaction_id),
        "wallet_id": platform_wallet.wallet_id,
        "amount": float(commission),
        "balance_before": float(balance_before),
        "balance_after": float(current_balance),
        "reference_id": str(payment.payment_id),
        "saga_id": payment.transaction_id,
        "description": f"Platform commission from bounty payment (backfilled)",
        "created_at": payment.completed_at or payment.created_at
    })
    
    print(f"✓ Created transaction for payment {str(payment.payment_id)[:8]}... (+{commission} ETB)")

# Update wallet balance
session.execute(text("""
    UPDATE wallets
    SET balance = :new_balance,
        updated_at = NOW()
    WHERE wallet_id = :wallet_id
"""), {
    "new_balance": float(current_balance),
    "wallet_id": platform_wallet.wallet_id
})

session.commit()

print(f"\n✓ Platform wallet updated!")
print(f"  Old Balance: {platform_wallet.balance} ETB")
print(f"  New Balance: {current_balance} ETB")
print(f"  Total Backfilled: {total_backfill} ETB")
print(f"\n=== BACKFILL COMPLETE ===")

session.close()
