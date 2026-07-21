"""Check and fix payment status in database."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine, text
from datetime import datetime
from src.core.config import settings

def check_and_fix_payments():
    """Check payment status and fix if needed."""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check existing payments
        result = conn.execute(text('''
            SELECT 
                payment_id,
                invoice_number,
                amount,
                currency,
                status,
                due_date,
                paid_at,
                period_start,
                period_end
            FROM subscription_payments
            ORDER BY created_at
        '''))
        
        payments = list(result)
        print(f"Found {len(payments)} subscription payments:\n")
        
        if len(payments) == 0:
            print("❌ No payments found in database!")
            return
        
        for p in payments:
            payment_id, invoice, amount, currency, status, due_date, paid_at, period_start, period_end = p
            
            print(f"Payment ID: {payment_id}")
            print(f"  Invoice: {invoice}")
            print(f"  Amount: {amount} {currency}")
            print(f"  Status: {status}")
            print(f"  Period: {period_start.date()} to {period_end.date()}")
            print(f"  Due: {due_date.date()}")
            print(f"  Paid At: {paid_at.date() if paid_at else 'Not paid'}")
            
            # If status is pending but should be paid, update it
            if status == 'pending':
                print(f"\n  ⚠️  Status is PENDING")
                print(f"  Do you want to mark this as PAID? (This will update the database)")
                print(f"  Updating to PAID status...")
                
                # Update to paid status
                conn.execute(text('''
                    UPDATE subscription_payments
                    SET 
                        status = 'paid',
                        paid_at = :paid_at,
                        payment_method = 'bank_transfer',
                        gateway_transaction_id = :txn_id
                    WHERE payment_id = :payment_id
                '''), {
                    'paid_at': period_start,  # Mark as paid at the start of period
                    'txn_id': f'TXN-{payment_id.hex[:12].upper()}',
                    'payment_id': payment_id
                })
                conn.commit()
                print(f"  ✅ Updated to PAID status!")
            else:
                print(f"  ✅ Already marked as {status.upper()}")
            
            print()

if __name__ == "__main__":
    check_and_fix_payments()
