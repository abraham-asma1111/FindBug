"""Fix subscription status for org@test.com"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import uuid

DATABASE_URL = "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Get organization ID for org@test.com
    result = db.execute(text("""
        SELECT o.id, u.id as user_id
        FROM organizations o
        JOIN users u ON o.user_id = u.id
        WHERE u.email = 'org@test.com'
    """))
    org_data = result.fetchone()
    
    if not org_data:
        print("❌ Organization not found for org@test.com")
        exit(1)
    
    org_id = org_data[0]
    user_id = org_data[1]
    print(f"✅ Found organization: {org_id}")
    
    # Delete existing subscription
    db.execute(text("""
        DELETE FROM organization_subscriptions 
        WHERE organization_id = :org_id
    """), {"org_id": org_id})
    db.commit()
    print("✅ Deleted old subscription")
    
    # Create new subscription with ACTIVE status
    subscription_id = str(uuid.uuid4())
    current_period_start = datetime.utcnow()
    current_period_end = current_period_start + timedelta(days=120)  # 4 months
    next_billing_date = current_period_end
    
    db.execute(text("""
        INSERT INTO organization_subscriptions (
            subscription_id,
            organization_id,
            tier,
            status,
            subscription_fee,
            currency,
            billing_cycle_months,
            payments_per_year,
            start_date,
            current_period_start,
            current_period_end,
            next_billing_date,
            is_trial,
            trial_end_date,
            created_at,
            updated_at
        ) VALUES (
            :subscription_id,
            :organization_id,
            'PROFESSIONAL',
            'ACTIVE',
            25000.00,
            'ETB',
            4,
            3,
            :start_date,
            :current_period_start,
            :current_period_end,
            :next_billing_date,
            false,
            NULL,
            :created_at,
            :updated_at
        )
    """), {
        "subscription_id": subscription_id,
        "organization_id": org_id,
        "start_date": current_period_start,
        "current_period_start": current_period_start,
        "current_period_end": current_period_end,
        "next_billing_date": next_billing_date,
        "created_at": current_period_start,
        "updated_at": current_period_start
    })
    db.commit()
    
    print(f"\n✅ Created new ACTIVE subscription!")
    print(f"   - Subscription ID: {subscription_id}")
    print(f"   - Tier: PROFESSIONAL")
    print(f"   - Status: ACTIVE")
    print(f"   - Fee: 25,000 ETB per 4 months")
    print(f"   - Current Period: {current_period_start.date()} to {current_period_end.date()}")
    
    # Verify
    result = db.execute(text("""
        SELECT subscription_id, tier, status, subscription_fee
        FROM organization_subscriptions
        WHERE organization_id = :org_id
    """), {"org_id": org_id})
    
    sub = result.fetchone()
    if sub:
        print(f"\n✅ Verification successful!")
        print(f"   - ID: {sub[0]}")
        print(f"   - Tier: {sub[1]}")
        print(f"   - Status: {sub[2]}")
        print(f"   - Fee: {sub[3]} ETB")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
