"""Create subscription payment records for testing."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine, text
from datetime import datetime
from dateutil.relativedelta import relativedelta
from src.core.config import settings
import uuid

def create_subscription_payments():
    """Create subscription payment records."""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Get the subscription
        result = conn.execute(text('''
            SELECT 
                subscription_id,
                organization_id,
                subscription_fee,
                currency,
                start_date,
                next_billing_date,
                billing_cycle_months
            FROM organization_subscriptions
            LIMIT 1
        '''))
        
        sub = result.fetchone()
        if not sub:
            print("❌ No subscription found!")
            return
        
        sub_id, org_id, fee, currency, start_date, next_billing, cycle_months = sub
        
        print(f"Creating payments for subscription:")
        print(f"  Subscription Fee: {fee} {currency}")
        print(f"  Start Date: {start_date}")
        print(f"  Billing Cycle: {cycle_months} months\n")
        
        # Create 3 payments:
        # 1. First payment (paid) - for the first period
        # 2. Second payment (pending) - for the current period
        # 3. Third payment (pending) - for the next period
        
        payments = []
        
        # Payment 1: First period (PAID)
        period1_start = start_date
        period1_end = start_date + relativedelta(months=int(cycle_months))
        payment1 = {
            'payment_id': str(uuid.uuid4()),
            'subscription_id': str(sub_id),
            'organization_id': str(org_id),
            'amount': float(fee),
            'currency': currency,
            'period_start': period1_start,
            'period_end': period1_end,
            'status': 'paid',
            'payment_method': 'bank_transfer',
            'gateway_transaction_id': f'TXN-{uuid.uuid4().hex[:12].upper()}',
            'due_date': period1_end,
            'paid_at': period1_start + relativedelta(days=5),
            'invoice_number': f'INV-2026-001',
            'created_at': period1_start
        }
        payments.append(payment1)
        print(f"✅ Payment 1 (PAID):")
        print(f"   Period: {period1_start.date()} to {period1_end.date()}")
        print(f"   Due: {period1_end.date()}")
        print(f"   Paid: {payment1['paid_at'].date()}")
        print(f"   Invoice: {payment1['invoice_number']}\n")
        
        # Payment 2: Current period (PENDING)
        period2_start = period1_end
        period2_end = period2_start + relativedelta(months=int(cycle_months))
        payment2 = {
            'payment_id': str(uuid.uuid4()),
            'subscription_id': str(sub_id),
            'organization_id': str(org_id),
            'amount': float(fee),
            'currency': currency,
            'period_start': period2_start,
            'period_end': period2_end,
            'status': 'pending',
            'payment_method': None,
            'gateway_transaction_id': None,
            'due_date': period2_end,
            'paid_at': None,
            'invoice_number': f'INV-2026-002',
            'created_at': period2_start
        }
        payments.append(payment2)
        print(f"✅ Payment 2 (PENDING):")
        print(f"   Period: {period2_start.date()} to {period2_end.date()}")
        print(f"   Due: {period2_end.date()}")
        print(f"   Invoice: {payment2['invoice_number']}\n")
        
        # Payment 3: Next period (PENDING)
        period3_start = period2_end
        period3_end = period3_start + relativedelta(months=int(cycle_months))
        payment3 = {
            'payment_id': str(uuid.uuid4()),
            'subscription_id': str(sub_id),
            'organization_id': str(org_id),
            'amount': float(fee),
            'currency': currency,
            'period_start': period3_start,
            'period_end': period3_end,
            'status': 'pending',
            'payment_method': None,
            'gateway_transaction_id': None,
            'due_date': period3_end,
            'paid_at': None,
            'invoice_number': f'INV-2027-001',
            'created_at': period3_start
        }
        payments.append(payment3)
        print(f"✅ Payment 3 (PENDING):")
        print(f"   Period: {period3_start.date()} to {period3_end.date()}")
        print(f"   Due: {period3_end.date()}")
        print(f"   Invoice: {payment3['invoice_number']}\n")
        
        # Insert payments
        for payment in payments:
            conn.execute(text('''
                INSERT INTO subscription_payments (
                    payment_id, subscription_id, organization_id,
                    amount, currency, period_start, period_end,
                    status, payment_method, gateway_transaction_id,
                    due_date, paid_at, invoice_number, created_at,
                    retry_count
                ) VALUES (
                    :payment_id, :subscription_id, :organization_id,
                    :amount, :currency, :period_start, :period_end,
                    :status, :payment_method, :gateway_transaction_id,
                    :due_date, :paid_at, :invoice_number, :created_at,
                    0
                )
            '''), payment)
        
        conn.commit()
        print(f"\n✅ Created {len(payments)} subscription payments!")
        print(f"   - 1 PAID payment")
        print(f"   - 2 PENDING payments")

if __name__ == "__main__":
    create_subscription_payments()
