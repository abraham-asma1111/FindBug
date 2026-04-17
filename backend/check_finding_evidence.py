"""Check PTaaS finding evidence in database"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

# Create engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Get the most recent finding
    result = db.execute(text("""
        SELECT 
            id,
            title,
            severity,
            exploit_screenshots,
            discovered_at
        FROM ptaas_findings
        ORDER BY discovered_at DESC
        LIMIT 1
    """))
    
    finding = result.fetchone()
    
    if finding:
        print(f"\n=== Most Recent Finding ===")
        print(f"ID: {finding[0]}")
        print(f"Title: {finding[1]}")
        print(f"Severity: {finding[2]}")
        print(f"Exploit Screenshots: {finding[3]}")
        print(f"Discovered At: {finding[4]}")
    else:
        print("\nNo findings found in database")
        
finally:
    db.close()
