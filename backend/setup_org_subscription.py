#!/usr/bin/env python3
"""
Setup test subscription data for organization
"""
import asyncio
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = "postgresql+asyncpg://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"

async def setup_subscription():
    """Create test subscription for org@test.com"""
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Get organization ID for org@test.com
            result = await session.execute(
                text("""
                    SELECT o.id, o.name 
                    FROM organizations o
                    JOIN users u ON u.id = o.id
                    WHERE u.email = 'org@test.com'
                """)
            )
            org = result.fetchone()
            
            if not org:
                print("❌ Organization not found for org@test.com")
                return
            
            org_id = org[0]
            org_name = org[1]
            print(f"✅ Found organization: {org_name} ({org_id})")
            
            # Check if subscription already exists
            result = await session.execute(
                text("""
                    SELECT subscription_id, tier, status 
                    FROM organization_subscriptions 
                    WHERE organization_id = :org_id
                """),
                {"org_id": org_id}
            )
            existing = result.fetchone()
            
            if existing:
                print(f"⚠️  Subscription already exists: {existing[1]} ({existing[2]})")
                print(f"   Subscription ID: {existing[0]}")
                
                # Update to active if not already
                if existing[2] != 'active':
                    await session.execute(
                        text("""
                            UPDATE organization_subscriptions 
                            SET status = 'active', updated_at = NOW()
                            WHERE subscription_id = :sub_id
                        """),
                        {"sub_id": existing[0]}
                    )
                    await session.commit()
                    print(f"✅ Updated subscription status to 'active'")
                return
            
            # Create new subscription
            subscription_id = uuid4()
            start_date = datetime.now()
            current_period_start = start_date
            current_period_end = start_date + timedelta(days=120)  # 4 months
            next_billing_date = current_period_end
            
            await session.execute(
                text("""
                    INSERT INTO organization_subscriptions (
                        subscription_id, organization_id, tier, status,
                        subscription_fee, currency, billing_cycle_months, payments_per_year,
                        start_date, current_period_start, current_period_end, next_billing_date,
                        is_trial, created_at, updated_at
                    ) VALUES (
                        :subscription_id, :organization_id, :tier, :status,
                        :subscription_fee, :currency, :billing_cycle_months, :payments_per_year,
                        :start_date, :current_period_start, :current_period_end, :next_billing_date,
                        :is_trial, NOW(), NOW()
                    )
                """),
                {
                    "subscription_id": subscription_id,
                    "organization_id": org_id,
                    "tier": "professional",
                    "status": "active",
                    "subscription_fee": Decimal("25000.00"),
                    "currency": "ETB",
                    "billing_cycle_months": 4,
                    "payments_per_year": 3,
                    "start_date": start_date,
                    "current_period_start": current_period_start,
                    "current_period_end": current_period_end,
                    "next_billing_date": next_billing_date,
                    "is_trial": False
                }
            )
            
            # Create a payment record
            payment_id = uuid4()
            await session.execute(
                text("""
                    INSERT INTO subscription_payments (
                        payment_id, subscription_id, organization_id,
                        amount, currency, period_start, period_end,
                        status, payment_method, due_date, paid_at,
                        invoice_number, created_at, updated_at
                    ) VALUES (
                        :payment_id, :subscription_id, :organization_id,
                        :amount, :currency, :period_start, :period_end,
                        :status, :payment_method, :due_date, :paid_at,
                        :invoice_number, NOW(), NOW()
                    )
                """),
                {
                    "payment_id": payment_id,
                    "subscription_id": subscription_id,
                    "organization_id": org_id,
                    "amount": Decimal("25000.00"),
                    "currency": "ETB",
                    "period_start": current_period_start,
                    "period_end": current_period_end,
                    "status": "paid",
                    "payment_method": "bank_transfer",
                    "due_date": start_date,
                    "paid_at": start_date,
                    "invoice_number": f"INV-{datetime.now().strftime('%Y%m%d')}-001"
                }
            )
            
            await session.commit()
            
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
            await session.rollback()
            raise
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(setup_subscription())
