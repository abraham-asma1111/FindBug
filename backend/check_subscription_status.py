"""Check subscription status for org@test.com"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Get organization ID for org@test.com
    result = db.execute(text("""
        SELECT o.id, u.email, u.role
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
    role = org_data[2]
    print(f"✅ Found organization: {org_id}")
    print(f"   - Email: {email}")
    print(f"   - Role: {role}")
    
    # Check ALL subscriptions (including cancelled)
    result = db.execute(text("""
        SELECT subscription_id, tier, status, subscription_fee, cancelled_at
        FROM organization_subscriptions
        WHERE organization_id = :org_id
        ORDER BY created_at DESC
    """), {"org_id": org_id})
    
    subscriptions = result.fetchall()
    
    if subscriptions:
        print(f"\n📋 Found {len(subscriptions)} subscription(s):")
        for idx, sub in enumerate(subscriptions, 1):
            print(f"\n   Subscription #{idx}:")
            print(f"   - ID: {sub[0]}")
            print(f"   - Tier: {sub[1]}")
            print(f"   - Status: {sub[2]}")
            print(f"   - Fee: {sub[3]} ETB")
            print(f"   - Cancelled At: {sub[4]}")
    else:
        print("\n📋 No subscriptions found (this is correct for testing)")
    
    # Check what the API endpoint would return
    print("\n🔍 What the API would return:")
    result = db.execute(text("""
        SELECT subscription_id, tier, status
        FROM organization_subscriptions
        WHERE organization_id = :org_id
        AND status IN ('ACTIVE', 'PENDING', 'SUSPENDED')
    """), {"org_id": org_id})
    
    active_sub = result.fetchone()
    if active_sub:
        print(f"   ✅ API returns: {active_sub[1]} ({active_sub[2]})")
    else:
        print(f"   ❌ API returns: 404 Not Found (no active subscription)")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    db.close()
