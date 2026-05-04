"""
Clean up subscription data and fix duplicate payment issues.

This script:
1. Removes all existing subscriptions and payments
2. Resets the database to a clean state
3. Allows fresh testing of the subscription system
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

# Create database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def cleanup_subscription_data():
    """Remove all subscription and payment data."""
    db = SessionLocal()
    
    try:
        print("🧹 Starting subscription data cleanup...")
        
        # Delete all subscription payments first (foreign key constraint)
        result = db.execute(text("DELETE FROM subscription_payments"))
        payments_deleted = result.rowcount
        print(f"✅ Deleted {payments_deleted} subscription payments")
        
        # Delete all organization subscriptions
        result = db.execute(text("DELETE FROM organization_subscriptions"))
        subscriptions_deleted = result.rowcount
        print(f"✅ Deleted {subscriptions_deleted} organization subscriptions")
        
        # Commit the changes
        db.commit()
        
        print("\n✨ Database cleanup complete!")
        print("\n📊 Summary:")
        print(f"   - Subscription payments removed: {payments_deleted}")
        print(f"   - Organization subscriptions removed: {subscriptions_deleted}")
        print("\n✅ You can now test the subscription system with clean data")
        
        # Verify cleanup
        print("\n🔍 Verifying cleanup...")
        result = db.execute(text("SELECT COUNT(*) FROM subscription_payments"))
        payment_count = result.scalar()
        
        result = db.execute(text("SELECT COUNT(*) FROM organization_subscriptions"))
        subscription_count = result.scalar()
        
        if payment_count == 0 and subscription_count == 0:
            print("✅ Verification passed - all data cleaned successfully")
        else:
            print(f"⚠️  Warning: Found {subscription_count} subscriptions and {payment_count} payments remaining")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def show_current_data():
    """Show current subscription data before cleanup."""
    db = SessionLocal()
    
    try:
        print("\n📊 Current Database State:")
        print("=" * 60)
        
        # Count subscriptions
        result = db.execute(text("SELECT COUNT(*) FROM organization_subscriptions"))
        subscription_count = result.scalar()
        print(f"Organization Subscriptions: {subscription_count}")
        
        # Count payments
        result = db.execute(text("SELECT COUNT(*) FROM subscription_payments"))
        payment_count = result.scalar()
        print(f"Subscription Payments: {payment_count}")
        
        # Show payment status breakdown
        result = db.execute(text("""
            SELECT status, COUNT(*) as count 
            FROM subscription_payments 
            GROUP BY status
        """))
        print("\nPayment Status Breakdown:")
        for row in result:
            print(f"  - {row[0]}: {row[1]}")
        
        # Show subscriptions by tier
        result = db.execute(text("""
            SELECT tier, COUNT(*) as count 
            FROM organization_subscriptions 
            GROUP BY tier
        """))
        print("\nSubscriptions by Tier:")
        for row in result:
            print(f"  - {row[0]}: {row[1]}")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error showing data: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Subscription Data Cleanup Tool")
    print("=" * 60)
    
    # Show current state
    show_current_data()
    
    # Ask for confirmation
    print("\n⚠️  WARNING: This will delete ALL subscription and payment data!")
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    
    if response == 'yes':
        cleanup_subscription_data()
    else:
        print("\n❌ Cleanup cancelled")
