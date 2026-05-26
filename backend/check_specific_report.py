#!/usr/bin/env python3
"""
Check specific report that's causing 404/500 errors
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bugbounty")

def check_report():
    """Check if the specific report exists"""
    engine = create_engine(DATABASE_URL)
    
    report_id = "3c34a499-9122-4e2b-9033-0d1336e74170"
    
    with engine.connect() as conn:
        print("=" * 100)
        print(f"CHECKING REPORT: {report_id}")
        print("=" * 100)
        
        # Check if report exists
        print("\n1. CHECKING IF REPORT EXISTS:")
        print("-" * 100)
        result = conn.execute(text("""
            SELECT 
                id,
                report_number,
                title,
                status,
                deleted_at
            FROM vulnerability_reports
            WHERE id = :report_id
        """), {"report_id": report_id})
        
        report = result.fetchone()
        if report:
            print(f"✓ Report FOUND:")
            print(f"  ID: {report[0]}")
            print(f"  Number: {report[1]}")
            print(f"  Title: {report[2]}")
            print(f"  Status: {report[3]}")
            print(f"  Deleted: {report[4] or 'No'}")
        else:
            print(f"✗ Report NOT FOUND in database")
            print(f"\nSearching for similar IDs...")
            
            # Search for reports with similar IDs
            result = conn.execute(text("""
                SELECT 
                    id,
                    report_number,
                    title,
                    status
                FROM vulnerability_reports
                ORDER BY submitted_at DESC
                LIMIT 10
            """))
            
            reports = result.fetchall()
            print(f"\nFound {len(reports)} recent reports:")
            for rep in reports:
                print(f"  • {rep[0]}")
                print(f"    {rep[1]}: {rep[2]} ({rep[3]})")
        
        # Check report_attachments for this report
        print("\n\n2. CHECKING ATTACHMENTS:")
        print("-" * 100)
        result = conn.execute(text("""
            SELECT COUNT(*)
            FROM report_attachments
            WHERE report_id = :report_id
        """), {"report_id": report_id})
        
        count = result.scalar()
        print(f"  Attachments for this report: {count}")
        
        # Check bounty_payments for this report
        print("\n\n3. CHECKING BOUNTY PAYMENTS:")
        print("-" * 100)
        result = conn.execute(text("""
            SELECT COUNT(*)
            FROM bounty_payments
            WHERE report_id = :report_id
        """), {"report_id": report_id})
        
        count = result.scalar()
        print(f"  Bounty payments for this report: {count}")
        
        print("\n" + "=" * 100)
        print("CONCLUSION:")
        print("=" * 100)
        if not report:
            print("❌ The report ID does NOT exist in the database")
            print("   This explains the 404 'Report not found' error")
            print("\n💡 SOLUTION:")
            print("   The frontend is trying to access a report that doesn't exist.")
            print("   This could be:")
            print("   - An old/cached report ID")
            print("   - A deleted report")
            print("   - A report from a different database/environment")
        else:
            print("✓ Report exists - the 500 error is likely a backend code issue")
        print("=" * 100)

if __name__ == "__main__":
    check_report()
