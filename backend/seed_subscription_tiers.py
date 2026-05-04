"""Seed subscription tier pricing data."""
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models.subscription import SubscriptionTierPricing
from datetime import datetime

# Database connection
DATABASE_URL = "postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Check if tiers already exist
    existing_count = db.query(SubscriptionTierPricing).count()
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing tiers. Updating...")
        db.query(SubscriptionTierPricing).delete()
        db.commit()
    
    # Seed tier pricing
    tiers = [
        {
            "tier": "BASIC",
            "name": "Basic",
            "description": "Perfect for small teams getting started",
            "quarterly_price": 15000.00,
            "currency": "ETB",
            "max_programs": 3,
            "max_researchers": 50,
            "max_reports_per_month": 100,
            "ptaas_enabled": False,
            "code_review_enabled": False,
            "ai_red_teaming_enabled": False,
            "live_events_enabled": False,
            "ssdlc_integration_enabled": False,
            "support_level": "email",
            "features": {
                "analytics": "basic",
                "api_access": False
            },
            "is_active": True
        },
        {
            "tier": "PROFESSIONAL",
            "name": "Professional",
            "description": "For growing organizations with multiple programs",
            "quarterly_price": 25000.00,
            "currency": "ETB",
            "max_programs": 10,
            "max_researchers": 200,
            "max_reports_per_month": 500,
            "ptaas_enabled": True,
            "code_review_enabled": False,
            "ai_red_teaming_enabled": False,
            "live_events_enabled": True,
            "ssdlc_integration_enabled": True,
            "support_level": "priority",
            "features": {
                "analytics": "advanced",
                "api_access": True,
                "custom_branding": True
            },
            "is_active": True
        },
        {
            "tier": "ENTERPRISE",
            "name": "Enterprise",
            "description": "For large enterprises with complex security needs",
            "quarterly_price": 50000.00,
            "currency": "ETB",
            "max_programs": None,  # unlimited
            "max_researchers": None,  # unlimited
            "max_reports_per_month": None,  # unlimited
            "ptaas_enabled": True,
            "code_review_enabled": True,
            "ai_red_teaming_enabled": True,
            "live_events_enabled": True,
            "ssdlc_integration_enabled": True,
            "support_level": "dedicated",
            "features": {
                "analytics": "enterprise",
                "api_access": True,
                "white_label": True,
                "sso": True,
                "custom_integrations": True
            },
            "is_active": True
        }
    ]
    
    for tier_data in tiers:
        tier = SubscriptionTierPricing(**tier_data)
        db.add(tier)
    
    db.commit()
    
    print("✅ Subscription tiers seeded successfully!")
    print("\nTiers created:")
    for tier in db.query(SubscriptionTierPricing).all():
        print(f"   - {tier.tier.value}: {tier.quarterly_price} {tier.currency} per quarter")
    
except Exception as e:
    print(f"❌ Error seeding tiers: {e}")
    db.rollback()
    sys.exit(1)
finally:
    db.close()
