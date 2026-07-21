#!/usr/bin/env python3
"""
Check subscription payments in the database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import uuid

# Database connection
DATABASE_URL = "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

print("=" * 80)
print("CHECKING SUBSCRIPTION PAYMENTS")
print("=" * 80)

# Get subscription
result = session.execute(text("""
    SELECT 
        s.subscription_id,
        s.organization_id,
        o.company_name,
        s.tier,
        s.status,
        s.subscription_fee,
        s.currency,
        s.start_date,
        s.next_billing_date,
        s.billing_cycle_months
    FROM organization_subscriptions s
    JOIN organizations o ON s.organization_id = o.id
    LIMIT 1
"""))

subscription = result.fetchone()

if subscription:
    print(f"\nSubscription Found:")
    print(f"  ID: {subscription[0]}")
    print(f"  Organization: {subscription[2]}")
    print(f"  Tier: {subscription[3]}")
    print(f"  Status: {subscription[4]}")
    print(f"  Fee: {subscription[5]} {subscription[6]}")
    print(f"  Start Date: {subscription[7]}")
    print(f"  Next Billing: {subscription[8]}")
    print(f"  Billing Cycle: {subscription[9]} months")
    
    # Check existing payments
    result = session.execute(text("""
        SELECT 
            payment_id,
            amount,
            status,
            invoice_number,
            due_date,
            paid_at,
            created_at
        FROM subscription_payments
        WHERE subscription_id = :sub_id
        ORDER BY created_at DESC
    """), {"sub_id": subscription[0]})
    
    payments = result.fetchall()
    
    print(f"\n\nExisting Payments: {len(payments)}")
    if payments:
        for payment in payments:
            print(f"\n  Payment ID: {payment[0]}")
            print(f"  Amount: {payment[1]}")
            print(f"  Status: {payment[2]}")
            print(f"  Invoice: {payment[3]}")
            print(f"  Due Date: {payment[4]}")
            print(f"  Paid At: {payment[5]}")
            print(f"  Created: {payment[6]}")
    else:
        print("  No payments found!")
        
        # Create a payment record
        print("\n\nCreating payment record...")
        
        subscription_id = subscription[0]
        organization_id = subscription[1]
        amount = subscription[5]
        currency = subscription[6]
        start_date = subscription[7]
        billing_cycle_months = int(subscription[9])  # Convert to int
        
        # Calculate period
        period_start = start_date
        period_end = start_date + timedelta(days=billing_cycle_months * 30)
        due_date = period_end
        
        # Generate invoice number
        invoice_number = f"SUB-{str(subscription_id)[:8].upper()}-{start_date.strftime('%Y%m')}"
        
        payment_id = uuid.uuid4()
        
        session.execute(text("""
            INSERT INTO subscription_payments (
                payment_id,
                subscription_id,
                organization_id,
                amount,
                currency,
                status,
                due_date,
                payment_method,
                invoice_number,
                period_start,
                period_end,
                created_at,
                updated_at
            ) VALUES (
                :payment_id,
                :subscription_id,
                :organization_id,
                :amount,
                :currency,
                'paid',
                :due_date,
                'bank_transfer',
                :invoice_number,
                :period_start,
                :period_end,
                :created_at,
                :updated_at
            )
        """), {
            "payment_id": payment_id,
            "subscription_id": subscription_id,
            "organization_id": organization_id,
            "amount": amount,
            "currency": currency,
            "due_date": due_date,
            "invoice_number": invoice_number,
            "period_start": period_start,
            "period_end": period_end,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        
        session.commit()
        
        print(f"✓ Payment created successfully!")
        print(f"  Payment ID: {payment_id}")
        print(f"  Invoice: {invoice_number}")
        print(f"  Amount: {amount} {currency}")
        print(f"  Status: paid")
        print(f"  Period: {period_start} to {period_end}")
        print(f"  Due Date: {due_date}")
else:
    print("No subscription found!")

session.close()
print("\n" + "=" * 80)
