"""
Verification script to check retest count for a finding
"""
import sys
from sqlalchemy import create_engine, text
from src.core.config import settings

def verify_retest_count(finding_id: str):
    """Check how many retest requests exist for a finding"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Count retest requests
        result = conn.execute(
            text("SELECT COUNT(*) FROM ptaas_retest_requests WHERE finding_id = :finding_id"),
            {"finding_id": finding_id}
        )
        count = result.scalar()
        print(f"Found {count} retest requests for finding {finding_id}")
        
        # Show details
        result = conn.execute(
            text("SELECT id, status, requested_at, is_free_retest FROM ptaas_retest_requests WHERE finding_id = :finding_id ORDER BY requested_at"),
            {"finding_id": finding_id}
        )
        rows = result.fetchall()
        
        if rows:
            print("\nRetest Request Details:")
            for row in rows:
                print(f"  - ID: {row[0]}, Status: {row[1]}, Requested: {row[2]}, Free: {row[3]}")
        else:
            print("\n✅ No retest requests found - database is clean!")

if __name__ == "__main__":
    finding_id = "992ced16-83e7-4c8e-896a-c5678e4d37b8"
    
    if len(sys.argv) > 1:
        finding_id = sys.argv[1]
    
    print(f"Verifying retest count for finding: {finding_id}\n")
    verify_retest_count(finding_id)
