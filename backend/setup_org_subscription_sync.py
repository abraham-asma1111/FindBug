#!/usr/bin/env python3
"""
Setup test subscription data for organization (synchronous version)
"""
import psycopg2
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

# Database connection
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "bug_bounty_production",
    "user": "bugbounty_user",
    "password": "changeme123"
}

def setup_subscription():
    """Create test subscription for org@test.com"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # Get organization ID for org@test.com
        cur.execute("""
            SELECT o.id, o.company_name 
            FROM organizations o
            JOIN users u ON u.id = o.user_id
            WHERE u.email = 'org@test.com'
        """)
        org = cur.fetchone()
        
        if not org:
            print("❌ Organization not found for org@test.com")
            return
        
        org_id = org[0]
        org_name = org[1]
        print(f"✅ Found organization: {org_name} ({org_id})")
        
        # Check if subscription already exists
        cur.execute("""
            SELECT subscription_id, tier, status 
            FROM organization_subscriptions 
            WHERE organization_id = %s
        """, (org_id,))
        existing = cur.fetchone()
        
        if existing:
            print(f"⚠️  Subscription already exists: {existing[1]} ({existing[2]})")
            print(f"   Subscription ID: {existing[0]}")
            
            # Update to active if not already
            if existing[2] != 'active':
                cur.execute("""
                    UPDATE organization_subscriptions 
                    SET status = 'active', updated_at = NOW()
                    WHERE subscription_id = %s
                """, (existing[0],))
                conn.commit()
                print(f"✅ Updated subscription status to 'active'")
            return
        
        # Create new subscription
        subscription_id = str(uuid4())
        start_date = datetime.now()
        current_period_start = start_date
        current_period_end = start_date + timedelta(days=120)  # 4 months
        next_billing_date = current_period_end
        
        cur.execute("""
            INSERT INTO organization_subscriptions (
                subscription_id, organization_id, tier, status,
                subscription_fee, currency, billing_cycle_months, payments_per_year,
                start_date, current_period_start, current_period_end, next_billing_date,
                is_trial, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, NOW(), NOW()
            )
        """, (
            subscription_id, str(org_id), "professional", "active",
            Decimal("25000.00"), "ETB", 4, 3,
            start_date, current_period_start, current_period_end, next_billing_date,
            False
        ))
        
        # Create a payment record
        payment_id = str(uuid4())
        cur.execute("""
            INSERT INTO subscription_payments (
                payment_id, subscription_id, organization_id,
                amount, currency, period_start, period_end,
                status, payment_method, due_date, paid_at,
                invoice_number, created_at, updated_at
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, NOW(), NOW()
            )
        """, (
            payment_id, subscription_id, str(org_id),
            Decimal("25000.00"), "ETB", current_period_start, current_period_end,
            "paid", "bank_transfer", start_date, start_date,
            f"INV-{datetime.now().strftime('%Y%m%d')}-001"
        ))
        
        conn.commit()
        
        print(f"\n✅ Subscription created successfully!")
        print(f"   Subscription ID: {subscription_id}")
        print(f"   Tier: Professional")
        print(f"   Status: Active")
        print(f"   Fee: 25,000 ETB per 4 months")
        print(f"   Current Period: {current_period_start.date()} to {current_period_end.date()}")
        print(f"   Next Billing: {next_billing_date.date()}")
        print(f"\n✅ Payment record created:")
        print(f"   Payment ID: {payment_id}")
        print(f"   Invoice: INV-{datetime.now().strftime('%Y%m%d')}-001")
        print(f"   Status: Paid")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    setup_subscription()
