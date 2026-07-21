#!/usr/bin/env python3
"""
Check for soft-deleted or missing data
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bugbounty")

def check_deleted_data():
    """Check for soft-deleted records and data history"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("=" * 100)
        print("CHECKING FOR MISSING/DELETED DATA")
        print("=" * 100)
        
        # Check vulnerability_reports with deleted_at
        print("\n1. VULNERABILITY_REPORTS (Including Soft-Deleted):")
        print("-" * 100)
        result = conn.execute(text("""
            SELECT 
                COUNT(*) FILTER (WHERE deleted_at IS NULL) as active_count,
                COUNT(*) FILTER (WHERE deleted_at IS NOT NULL) as deleted_count,
                COUNT(*) as total_count
            FROM vulnerability_reports
        """))
        
        counts = result.fetchone()
        print(f"  Active Reports: {counts[0]}")
        print(f"  Soft-Deleted Reports: {counts[1]}")
        print(f"  Total Reports: {counts[2]}")
        
        # Show deleted reports if any
        if counts[1] > 0:
            print("\n  Soft-Deleted Reports:")
            result = conn.execute(text("""
                SELECT 
                    id,
                    report_number,
                    title,
                    deleted_at
                FROM vulnerability_reports
                WHERE deleted_at IS NOT NULL
                ORDER BY deleted_at DESC
            """))
            
            deleted = result.fetchall()
            for rep in deleted:
                print(f"    - {rep[1]}: {rep[2]} (deleted: {rep[3]})")
        
        # Check bounty_programs with deleted_at
        print("\n\n2. BOUNTY_PROGRAMS (Including Soft-Deleted):")
        print("-" * 100)
        result = conn.execute(text("""
            SELECT 
                COUNT(*) FILTER (WHERE deleted_at IS NULL) as active_count,
                COUNT(*) FILTER (WHERE deleted_at IS NOT NULL) as deleted_count,
                COUNT(*) as total_count
            FROM bounty_programs
        """))
        
        counts = result.fetchone()
        print(f"  Active Programs: {counts[0]}")
        print(f"  Soft-Deleted Programs: {counts[1]}")
        print(f"  Total Programs: {counts[2]}")
        
        # Show deleted programs if any
        if counts[1] > 0:
            print("\n  Soft-Deleted Programs:")
            result = conn.execute(text("""
                SELECT 
                    id,
                    name,
                    deleted_at
                FROM bounty_programs
                WHERE deleted_at IS NOT NULL
                ORDER BY deleted_at DESC
            """))
            
            deleted = result.fetchall()
            for prog in deleted:
                print(f"    - {prog[1]} (deleted: {prog[2]})")
        
        # Check report_number sequence
        print("\n\n3. REPORT NUMBER SEQUENCE:")
        print("-" * 100)
        result = conn.execute(text("""
            SELECT 
                report_number,
                submitted_at,
                deleted_at IS NOT NULL as is_deleted
            FROM vulnerability_reports
            ORDER BY report_number
        """))
        
        reports = result.fetchall()
        print(f"  Report numbers found: {len(reports)}")
        if reports:
            print(f"  First: {reports[0][0]}")
            print(f"  Last: {reports[-1][0]}")
            
            # Check for gaps
            print("\n  All report numbers:")
            for rep in reports:
                status = " (DELETED)" if rep[2] else ""
                print(f"    - {rep[0]}{status}")
        
        # Check audit_logs for deletion events
        print("\n\n4. AUDIT LOGS (Deletion Events):")
        print("-" * 100)
        result = conn.execute(text("""
            SELECT 
                action,
                entity_type,
                entity_id,
                performed_at,
                details
            FROM audit_logs
            WHERE action LIKE '%delete%' OR action LIKE '%remove%'
            ORDER BY performed_at DESC
            LIMIT 20
        """))
        
        audit_logs = result.fetchall()
        if audit_logs:
            print(f"  Found {len(audit_logs)} deletion events (showing last 20):")
            for log in audit_logs:
                print(f"    - {log[0]}: {log[1]} (ID: {log[2]}) at {log[3]}")
        else:
            print("  No deletion events found in audit logs")
        
        # Check if there are other report-like tables
        print("\n\n5. OTHER REPORT TABLES:")
        print("-" * 100)
        
        # Check simulation_reports
        result = conn.execute(text("SELECT COUNT(*) FROM simulation_reports"))
        sim_count = result.scalar()
        print(f"  Simulation Reports: {sim_count}")
        
        # Check ai_vulnerability_reports
        result = conn.execute(text("SELECT COUNT(*) FROM ai_vulnerability_reports"))
        ai_count = result.scalar()
        print(f"  AI Vulnerability Reports: {ai_count}")
        
        # Check ptaas_findings
        result = conn.execute(text("SELECT COUNT(*) FROM ptaas_findings"))
        ptaas_count = result.scalar()
        print(f"  PTaaS Findings: {ptaas_count}")
        
        # Check code_review_findings
        result = conn.execute(text("SELECT COUNT(*) FROM code_review_findings"))
        code_count = result.scalar()
        print(f"  Code Review Findings: {code_count}")
        
        print("\n" + "=" * 100)
        print("SUMMARY:")
        print("=" * 100)
        print(f"Expected: 34 reports, 7 programs")
        print(f"Found in vulnerability_reports: {counts[0]} active + {counts[1]} deleted = {counts[2]} total")
        print(f"Found in bounty_programs: 4 active")
        print(f"Other findings: {sim_count} simulation + {ai_count} AI + {ptaas_count} PTaaS + {code_count} code review")
        print(f"Total findings across all tables: {counts[2] + sim_count + ai_count + ptaas_count + code_count}")
        print("=" * 100)

if __name__ == "__main__":
    check_deleted_data()
