"""
Add test evidence (screenshots) to a finding
"""
import sys
import json
from sqlalchemy import create_engine, text
from src.core.config import settings

def add_test_evidence(finding_id: str):
    """Add test screenshot URLs to a finding"""
    engine = create_engine(settings.DATABASE_URL)
    
    # Using placeholder images from a reliable CDN
    test_screenshots = [
        "https://picsum.photos/800/600?random=1",
        "https://picsum.photos/800/600?random=2",
        "https://picsum.photos/800/600?random=3"
    ]
    
    with engine.connect() as conn:
        # Update the finding with test screenshots (as JSON)
        # Convert to JSON string and cast in PostgreSQL
        result = conn.execute(
            text("""
                UPDATE ptaas_findings 
                SET exploit_screenshots = CAST(:screenshots AS json)
                WHERE id = :finding_id
            """),
            {
                "finding_id": finding_id,
                "screenshots": json.dumps(test_screenshots)  # Convert to JSON string
            }
        )
        conn.commit()
        
        if result.rowcount > 0:
            print(f"✅ Added {len(test_screenshots)} test screenshots to finding {finding_id}")
            print("\nScreenshot URLs:")
            for i, url in enumerate(test_screenshots, 1):
                print(f"  {i}. {url}")
        else:
            print(f"❌ Finding {finding_id} not found")

if __name__ == "__main__":
    finding_id = "992ced16-83e7-4c8e-896a-c5678e4d37b8"
    
    if len(sys.argv) > 1:
        finding_id = sys.argv[1]
    
    print(f"Adding test evidence to finding: {finding_id}\n")
    add_test_evidence(finding_id)
