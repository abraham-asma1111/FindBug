"""Check organization branding data."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models.organization import Organization

# Connect to database
engine = create_engine('postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production')
Session = sessionmaker(bind=engine)
db = Session()

# Get all organizations
orgs = db.query(Organization).all()
print(f"Found {len(orgs)} organizations\n")

for org in orgs:
    print(f"Organization: {org.company_name}")
    print(f"  ID: {org.id}")
    print(f"  Logo URL: {org.logo_url}")
    print(f"  Cover Image URL: {org.cover_image_url}")
    print(f"  Brand Color: {org.brand_color}")
    print(f"  Theme Settings: {org.theme_settings}")
    print()

db.close()
