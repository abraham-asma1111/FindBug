"""
Check engagement dates for a finding
"""
import sys
from sqlalchemy import create_engine, text
from src.core.config import settings

def check_engagement_dates(finding_id: str):
    """Check engagement dates for a finding"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Get finding and engagement info
        result = conn.execute(
            text("""
                SELECT 
                    f.id as finding_id,
                    f.title,
                    f.severity,
                    e.id as engagement_id,
                    e.start_date,
                    e.end_date,
                    e.status
                FROM ptaas_findings f
                JOIN ptaas_engagements e ON f.engagement_id = e.id
                WHERE f.id = :finding_id
            """),
            {"finding_id": finding_id}
        )
        row = result.fetchone()
        
        if row:
            print(f"Finding: {row[1]}")
            print(f"Severity: {row[2]}")
            print(f"Engagement ID: {row[3]}")
            print(f"Start Date: {row[4]}")
            print(f"End Date: {row[5]}")
            print(f"Status: {row[6]}")
            
            if row[5] is None:
                print("\n⚠️  WARNING: Engagement has no end_date!")
                print("This might cause issues with retest eligibility checks.")
        else:
            print(f"Finding {finding_id} not found")

if __name__ == "__main__":
    finding_id = "992ced16-83e7-4c8e-896a-c5678e4d37b8"
    
    if len(sys.argv) > 1:
        finding_id = sys.argv[1]
    
    print(f"Checking engagement dates for finding: {finding_id}\n")
    check_engagement_dates(finding_id)
