"""
Create test organizations for Finance Organizations page testing
"""
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/bug_bounty_production')

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def create_test_organizations():
    """Create test organizations with subscriptions"""
    
    test_orgs = [
        {
            'company_name': 'TechCorp Solutions',
            'industry': 'Technology',
            'email': 'contact@techcorp.com',
            'website': 'https://techcorp.com',
            'subscription_type': 'premium',
            'subscription_amount': 500,
            'subscription_status': 'active'
        },
        {
            'company_name': 'FinanceHub Inc',
            'industry': 'Finance',
            'email': 'info@financehub.com',
            'website': 'https://financehub.com',
            'subscription_type': 'enterprise',
            'subscription_amount': 1000,
            'subscription_status': 'active'
        },
        {
            'company_name': 'HealthTech Medical',
            'industry': 'Healthcare',
            'email': 'support@healthtech.com',
            'website': 'https://healthtech.com',
            'subscription_type': 'standard',
            'subscription_amount': 250,
            'subscription_status': 'active'
        },
        {
            'company_name': 'EduLearn Platform',
            'industry': 'Education',
            'email': 'hello@edulearn.com',
            'website': 'https://edulearn.com',
            'subscription_type': 'premium',
            'subscription_amount': 500,
            'subscription_status': 'active'
        },
        {
            'company_name': 'RetailMax Commerce',
            'industry': 'Retail',
            'email': 'contact@retailmax.com',
            'website': 'https://retailmax.com',
            'subscription_type': 'standard',
            'subscription_amount': 250,
            'subscription_status': 'suspended'
        }
    ]
    
    print("Creating test organizations...")
    
    for org_data in test_orgs:
        try:
            # Check if organization already exists
            result = session.execute(
                text("SELECT id FROM organizations WHERE company_name = :name"),
                {'name': org_data['company_name']}
            ).fetchone()
            
            if result:
                print(f"✓ Organization '{org_data['company_name']}' already exists")
                continue
            
            # Create organization
            org_result = session.execute(
                text("""
                    INSERT INTO organizations (company_name, industry, email, website, created_at, updated_at)
                    VALUES (:company_name, :industry, :email, :website, :created_at, :updated_at)
                    RETURNING id
                """),
                {
                    'company_name': org_data['company_name'],
                    'industry': org_data['industry'],
                    'email': org_data['email'],
                    'website': org_data['website'],
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            )
            org_id = org_result.fetchone()[0]
            
            # Create subscription for the organization
            session.execute(
                text("""
                    INSERT INTO subscriptions (
                        organization_id, tier, status, subscription_fee, currency,
                        start_date, next_billing_date, billing_cycle_months,
                        is_trial, created_at, updated_at
                    )
                    VALUES (
                        :org_id, :tier, :status, :fee, 'ETB',
                        :start_date, :next_billing, 1,
                        false, :created_at, :updated_at
                    )
                """),
                {
                    'org_id': org_id,
                    'tier': org_data['subscription_type'],
                    'status': org_data['subscription_status'].upper(),
                    'fee': org_data['subscription_amount'],
                    'start_date': datetime.utcnow() - timedelta(days=30),
                    'next_billing': datetime.utcnow() + timedelta(days=30),
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            )
            
            session.commit()
            print(f"✓ Created organization: {org_data['company_name']} ({org_data['subscription_type']} - {org_data['subscription_status']})")
            
        except Exception as e:
            session.rollback()
            print(f"✗ Error creating {org_data['company_name']}: {str(e)}")
    
    # Show summary
    print("\n" + "="*60)
    result = session.execute(text("SELECT COUNT(*) FROM organizations"))
    count = result.scalar()
    print(f"Total organizations in database: {count}")
    print("="*60)
    
    session.close()

if __name__ == "__main__":
    create_test_organizations()
