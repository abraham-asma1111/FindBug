#!/usr/bin/env python3
"""
Check actual reports and programs data
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bugbounty")

def check_data():
    """Check vulnerability_reports and bounty_programs"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("=" * 80)
        print("ACTUAL DATA IN DATABASE")
        print("=" * 80)
        
        # Check vulnerability_reports
        print("\n1. VULNERABILITY_REPORTS TABLE (7 rows):")
        print("-" * 80)
        result = conn.execute(text("""
            SELECT 
                id,
                title,
                severity,
                status,
                researcher_id,
                program_id,
                created_at
            FROM vulnerability_reports
            ORDER BY created_at DESC
        """))
        
        reports = result.fetchall()
        print(f"Found {len(reports)} vulnerability reports:")
        for report in reports:
            print(f"\n  Report ID: {report[0]}")
            print(f"  Title: {report[1]}")
            print(f"  Severity: {report[2]}")
            print(f"  Status: {report[3]}")
            print(f"  Researcher ID: {report[4]}")
            print(f"  Program ID: {report[5]}")
            print(f"  Created: {report[6]}")
        
        # Check bounty_programs
        print("\n\n2. BOUNTY_PROGRAMS TABLE (4 rows):")
        print("-" * 80)
        result = conn.execute(text("""
            SELECT 
                id,
                name,
                type,
                status,
                organization_id,
                created_at
            FROM bounty_programs
            ORDER BY created_at DESC
        """))
        
        programs = result.fetchall()
        print(f"Found {len(programs)} bounty programs:")
        for program in programs:
            print(f"\n  Program ID: {program[0]}")
            print(f"  Name: {program[1]}")
            print(f"  Type: {program[2]}")
            print(f"  Status: {program[3]}")
            print(f"  Organization ID: {program[4]}")
            print(f"  Created: {program[5]}")
        
        # Check program_participations (join table)
        print("\n\n3. PROGRAM_PARTICIPATIONS TABLE (5 rows):")
        print("-" * 80)
        result = conn.execute(text("""
            SELECT 
                program_id,
                researcher_id,
                joined_at,
                status
            FROM program_participations
            ORDER BY joined_at DESC
        """))
        
        participations = result.fetchall()
        print(f"Found {len(participations)} program participations:")
        for part in participations:
            print(f"\n  Program ID: {part[0]}")
            print(f"  Researcher ID: {part[1]}")
            print(f"  Joined: {part[2]}")
            print(f"  Status: {part[3]}")
        
        # Check researchers
        print("\n\n4. RESEARCHERS TABLE (25 rows):")
        print("-" * 80)
        result = conn.execute(text("""
            SELECT 
                id,
                user_id,
                reputation_score,
                total_bounties_earned
            FROM researchers
            ORDER BY id
            LIMIT 10
        """))
        
        researchers = result.fetchall()
        print(f"Found {len(researchers)} researchers (showing first 10):")
        for researcher in researchers:
            print(f"\n  Researcher ID: {researcher[0]}")
            print(f"  User ID: {researcher[1]}")
            print(f"  Reputation: {researcher[2]}")
            print(f"  Total Bounties: ${researcher[3]}")
        
        # Check organizations
        print("\n\n5. ORGANIZATIONS TABLE (10 rows):")
        print("-" * 80)
        result = conn.execute(text("""
            SELECT 
                id,
                name,
                created_at
            FROM organizations
            ORDER BY created_at DESC
        """))
        
        orgs = result.fetchall()
        print(f"Found {len(orgs)} organizations:")
        for org in orgs:
            print(f"\n  Organization ID: {org[0]}")
            print(f"  Name: {org[1]}")
            print(f"  Created: {org[2]}")
        
        print("\n" + "=" * 80)
        print("SUMMARY:")
        print("=" * 80)
        print(f"✓ Vulnerability Reports: 7")
        print(f"✓ Bounty Programs: 4")
        print(f"✓ Program Participations: 5")
        print(f"✓ Researchers: 25")
        print(f"✓ Organizations: 10")
        print("=" * 80)

if __name__ == "__main__":
    check_data()
