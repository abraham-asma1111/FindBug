"""Fix subscription next_billing_date to match billing_cycle_months."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine, text
from datetime import datetime
from dateutil.relativedelta import relativedelta
from src.core.config import settings

def fix_subscription_dates():
    """Fix next_billing_date to be start_date + billing_cycle_months."""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Get all subscriptions
        result = conn.execute(text('''
            SELECT 
                subscription_id,
                tier,
                start_date,
                next_billing_date,
                billing_cycle_months,
                current_period_start,
                current_period_end
            FROM organization_subscriptions
        '''))
        
        subscriptions = list(result)
        print(f"Found {len(subscriptions)} subscriptions\n")
        
        for sub in subscriptions:
            sub_id, tier, start_date, next_billing, cycle_months, period_start, period_end = sub
            
            # Calculate correct next_billing_date
            correct_next_billing = start_date + relativedelta(months=int(cycle_months))
            correct_period_end = start_date + relativedelta(months=int(cycle_months))
            
            print(f"Subscription: {tier}")
            print(f"  Start Date: {start_date}")
            print(f"  Billing Cycle: {cycle_months} months")
            print(f"  Current Next Billing: {next_billing}")
            print(f"  Correct Next Billing: {correct_next_billing}")
            
            if next_billing != correct_next_billing:
                print(f"  ❌ INCORRECT - Updating...")
                
                # Update the subscription
                conn.execute(text('''
                    UPDATE organization_subscriptions
                    SET 
                        next_billing_date = :next_billing,
                        current_period_end = :period_end
                    WHERE subscription_id = :sub_id
                '''), {
                    'next_billing': correct_next_billing,
                    'period_end': correct_period_end,
                    'sub_id': sub_id
                })
                conn.commit()
                print(f"  ✅ Updated!")
            else:
                print(f"  ✅ Already correct")
            
            print()

if __name__ == "__main__":
    fix_subscription_dates()
    print("✅ All subscription dates fixed!")
