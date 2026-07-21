"""Delete duplicate subscription payments."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine, text
from src.core.config import settings

def delete_duplicates():
    """Delete all duplicate subscription payments."""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Show current payments
        result = conn.execute(text('''
            SELECT 
                payment_id,
                invoice_number,
                amount,
                status,
                TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') as created_at
            FROM subscription_payments
            ORDER BY created_at
        '''))
        
        payments = list(result)
        print(f"Found {len(payments)} payments:\n")
        
        for p in payments:
            print(f"  {p[1]} - {p[2]} ETB - {p[3]} - Created: {p[4]}")
        
        if len(payments) == 0:
            print("\n✅ No payments to delete!")
            return
        
        # Delete ALL payments
        print(f"\n🗑️  Deleting all {len(payments)} payments...")
        conn.execute(text('DELETE FROM subscription_payments'))
        conn.commit()
        
        # Verify deletion
        result = conn.execute(text('SELECT COUNT(*) FROM subscription_payments'))
        count = result.scalar()
        
        print(f"\n✅ Deleted all payments! Remaining: {count}")

if __name__ == "__main__":
    delete_duplicates()
