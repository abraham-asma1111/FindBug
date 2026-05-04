"""Delete subscription for org@test.com to test subscription selection flow"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Get organization ID for org@test.com
    result = db.execute(text("""
        SELECT o.id, u.email
        FROM organizations o
        JOIN users u ON o.user_id = u.id
        WHERE u.email = 'org@test.com'
    """))
    org_data = result.fetchone()
    
    if not org_data:
        print("❌ Organization not found for org@test.com")
        exit(1)
    
    org_id = org_data[0]
    email = org_data[1]
    print(f"✅ Found organization: {org_id} ({email})")
    
    # Check existing subscription
    result = db.execute(text("""
        SELECT subscription_id, tier, status, subscription_fee
        FROM organization_subscriptions
        WHERE organization_id = :org_id
    """), {"org_id": org_id})
    
    existing = result.fetchone()
    if existing:
        print(f"\n📋 Current subscription:")
        print(f"   - ID: {existing[0]}")
        print(f"   - Tier: {existing[1]}")
        print(f"   - Status: {existing[2]}")
        print(f"   - Fee: {existing[3]} ETB")
    else:
        print("\n📋 No subscription found")
        exit(0)
    
    # Delete subscription
    db.execute(text("""
        DELETE FROM organization_subscriptions 
        WHERE organization_id = :org_id
    """), {"org_id": org_id})
    db.commit()
    
    print(f"\n✅ Subscription deleted successfully!")
    print(f"\nNow you can:")
    print(f"1. Go to /organization/billing/manage-plan")
    print(f"2. Choose any plan you want (Basic, Professional, or Enterprise)")
    print(f"3. Click 'Subscribe Now' to create your subscription")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
