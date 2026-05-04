#!/usr/bin/env python3
"""Test subscription query"""
import sys
sys.path.insert(0, '/home/abraham/Desktop/Final-year-project/backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models.subscription import OrganizationSubscription
from src.domain.models.organization import Organization
from src.domain.models.user import User

# Database connection
DATABASE_URL = "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

try:
    # Get user
    user = db.query(User).filter(User.email == "org@test.com").first()
    print(f"✅ User found: {user.email} (ID: {user.id}, Role: {user.role})")
    
    # Get organization
    organization = db.query(Organization).filter(
        Organization.user_id == user.id
    ).first()
    
    if organization:
        print(f"✅ Organization found: {organization.company_name} (ID: {organization.id})")
    else:
        print("❌ Organization NOT found!")
        sys.exit(1)
    
    # Try to get subscription
    print(f"\n🔍 Querying for subscription with organization_id: {organization.id}")
    
    subscription = db.query(OrganizationSubscription).filter(
        OrganizationSubscription.organization_id == organization.id
    ).first()
    
    if subscription:
        print(f"✅ Subscription found (no status filter):")
        print(f"   ID: {subscription.subscription_id}")
        print(f"   Tier: {subscription.tier} (type: {type(subscription.tier)})")
        print(f"   Status: {subscription.status} (type: {type(subscription.status)})")
        print(f"   Fee: {subscription.subscription_fee} {subscription.currency}")
    else:
        print("❌ Subscription NOT found (no status filter)!")
    
    # Try with status filter
    subscription2 = db.query(OrganizationSubscription).filter(
        OrganizationSubscription.organization_id == organization.id,
        OrganizationSubscription.status.in_(["active", "pending", "suspended"])
    ).first()
    
    if subscription2:
        print(f"\n✅ Subscription found (with status filter):")
        print(f"   Status: {subscription2.status}")
    else:
        print(f"\n❌ Subscription NOT found (with status filter)!")
        print(f"   Tried statuses: ['active', 'pending', 'suspended']")
        
finally:
    db.close()
