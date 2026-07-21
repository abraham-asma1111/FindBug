"""Test finance organization detail endpoint."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import requests

# Test Company ID
org_id = "7c3b13e0-afb3-460b-b240-a74eb83e574c"

# Finance officer token (you'll need to get this from your login)
# For now, let's just check the database query works

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models.organization import Organization
from src.domain.models.subscription import OrganizationSubscription
from uuid import UUID

# Connect to database
engine = create_engine('postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production')
Session = sessionmaker(bind=engine)
db = Session()

org_uuid = UUID(org_id)
organization = db.query(Organization).filter(Organization.id == org_uuid).first()

if organization:
    print(f"Organization found: {organization.company_name}")
    print(f"Logo URL: {organization.logo_url}")
    print(f"Cover Image URL: {organization.cover_image_url}")
    print(f"Brand Color: {organization.brand_color}")
    print(f"Theme Settings: {organization.theme_settings}")
    
    # Check subscription
    subscription = db.query(OrganizationSubscription).filter(
        OrganizationSubscription.organization_id == org_uuid
    ).first()
    
    if subscription:
        print(f"\nSubscription found:")
        print(f"  Tier: {subscription.tier}")
        print(f"  Status: {subscription.status}")
        print(f"  Fee: {subscription.subscription_fee}")
    else:
        print("\nNo subscription found")
else:
    print("Organization not found")

db.close()
