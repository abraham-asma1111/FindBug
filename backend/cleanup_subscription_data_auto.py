"""
Clean up subscription data automatically (no prompt).
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
        
        # Show current state first
        result = db.execute(text("SELECT COUNT(*) FROM subscription_payments"))
        payment_count_before = result.scalar()
        
        result = db.execute(text("SELECT COUNT(*) FROM organization_subscriptions"))
        subscription_count_before = result.scalar()
        
        print(f"\n📊 Before cleanup:")
        print(f"   - Subscriptions: {subscription_count_before}")
        print(f"   - Payments: {payment_count_before}")
        
        # Show payment status breakdown
        result = db.execute(text("""
            SELECT status, COUNT(*) as count 
            FROM subscription_payments 
            GROUP BY status
        """))
        print(f"\n   Payment status:")
        for row in result:
            print(f"     - {row[0]}: {row[1]}")
        
        # Delete all subscription payments first (foreign key constraint)
        print("\n🗑️  Deleting subscription payments...")
        result = db.execute(text("DELETE FROM subscription_payments"))
        payments_deleted = result.rowcount
        print(f"   ✅ Deleted {payments_deleted} payments")
        
        # Delete all organization subscriptions
        print("🗑️  Deleting organization subscriptions...")
        result = db.execute(text("DELETE FROM organization_subscriptions"))
        subscriptions_deleted = result.rowcount
        print(f"   ✅ Deleted {subscriptions_deleted} subscriptions")
        
        # Commit the changes
        db.commit()
        
        print("\n✨ Database cleanup complete!")
        print("\n📊 Summary:")
        print(f"   - Subscription payments removed: {payments_deleted}")
        print(f"   - Organization subscriptions removed: {subscriptions_deleted}")
        
        # Verify cleanup
        print("\n🔍 Verifying cleanup...")
        result = db.execute(text("SELECT COUNT(*) FROM subscription_payments"))
        payment_count = result.scalar()
        
        result = db.execute(text("SELECT COUNT(*) FROM organization_subscriptions"))
        subscription_count = result.scalar()
        
        print(f"   - Remaining subscriptions: {subscription_count}")
        print(f"   - Remaining payments: {payment_count}")
        
        if payment_count == 0 and subscription_count == 0:
            print("\n✅ Verification passed - all data cleaned successfully!")
            print("✅ You can now test the subscription system with clean data")
        else:
            print(f"\n⚠️  Warning: Found {subscription_count} subscriptions and {payment_count} payments remaining")
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Subscription Data Cleanup Tool (Auto Mode)")
    print("=" * 60)
    cleanup_subscription_data()
    print("=" * 60)
