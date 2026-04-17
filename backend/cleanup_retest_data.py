"""
Cleanup script to remove retest requests for testing purposes
"""
import sys
from sqlalchemy import create_engine, text
from src.core.config import settings

def cleanup_retest_data(finding_id: str):
    """Remove retest requests and history for a specific finding"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Delete retest history first (foreign key constraint)
        result1 = conn.execute(
            text("DELETE FROM ptaas_retest_history WHERE finding_id = :finding_id"),
            {"finding_id": finding_id}
        )
        print(f"Deleted {result1.rowcount} retest history records")
        
        # Delete retest requests
        result2 = conn.execute(
            text("DELETE FROM ptaas_retest_requests WHERE finding_id = :finding_id"),
            {"finding_id": finding_id}
        )
        print(f"Deleted {result2.rowcount} retest request records")
        
        conn.commit()
        print(f"✅ Cleanup complete for finding {finding_id}")

if __name__ == "__main__":
    finding_id = "992ced16-83e7-4c8e-896a-c5678e4d37b8"
    
    if len(sys.argv) > 1:
        finding_id = sys.argv[1]
    
    print(f"Cleaning up retest data for finding: {finding_id}")
    cleanup_retest_data(finding_id)
