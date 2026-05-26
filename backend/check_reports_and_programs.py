#!/usr/bin/env python3
"""
Check reports and programs in the database
"""
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bugbounty")

def check_database():
    """Check reports and programs in database"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("=" * 80)
        print("CHECKING REPORTS AND PROGRAMS IN DATABASE")
        print("=" * 80)
        
        # Check reports table
        print("\n1. REPORTS TABLE:")
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
            FROM reports
            ORDER BY created_at DESC
            LIMIT 10
        """))
        
        reports = result.fetchall()
        if reports:
            print(f"Found {len(reports)} reports (showing first 10):")
            for report in reports:
                print(f"  - ID: {report[0]}")
                print(f"    Title: {report[1]}")
                print(f"    Severity: {report[2]}")
                print(f"    Status: {report[3]}")
                print(f"    Researcher ID: {report[4]}")
                print(f"    Program ID: {report[5]}")
                print(f"    Created: {report[6]}")
                print()
        else:
            print("  No reports found!")
        
        # Get total count
        result = conn.execute(text("SELECT COUNT(*) FROM reports"))
        total_reports = result.scalar()
        print(f"\nTotal reports in database: {total_reports}")
        
        # Check programs table
        print("\n2. PROGRAMS TABLE:")
        print("-" * 80)
        result = conn.execute(text("""
            SELECT 
                id,
                name,
                type,
                status,
                organization_id,
                created_at
            FROM programs
            ORDER BY created_at DESC
            LIMIT 10
        """))
        
        programs = result.fetchall()
        if programs:
            print(f"Found {len(programs)} programs (showing first 10):")
            for program in programs:
                print(f"  - ID: {program[0]}")
                print(f"    Name: {program[1]}")
                print(f"    Type: {program[2]}")
                print(f"    Status: {program[3]}")
                print(f"    Organization ID: {program[4]}")
                print(f"    Created: {program[5]}")
                print()
        else:
            print("  No programs found!")
        
        # Get total count
        result = conn.execute(text("SELECT COUNT(*) FROM programs"))
        total_programs = result.scalar()
        print(f"\nTotal programs in database: {total_programs}")
        
        # Check program_researchers (join table)
        print("\n3. PROGRAM_RESEARCHERS (Join Table):")
        print("-" * 80)
        result = conn.execute(text("""
            SELECT 
                program_id,
                researcher_id,
                joined_at,
                status
            FROM program_researchers
            ORDER BY joined_at DESC
            LIMIT 10
        """))
        
        joins = result.fetchall()
        if joins:
            print(f"Found {len(joins)} program-researcher relationships (showing first 10):")
            for join in joins:
                print(f"  - Program ID: {join[0]}, Researcher ID: {join[1]}")
                print(f"    Joined: {join[2]}, Status: {join[3]}")
        else:
            print("  No program-researcher relationships found!")
        
        # Get total count
        result = conn.execute(text("SELECT COUNT(*) FROM program_researchers"))
        total_joins = result.scalar()
        print(f"\nTotal program-researcher relationships: {total_joins}")
        
        # Check researchers table
        print("\n4. RESEARCHERS TABLE:")
        print("-" * 80)
        result = conn.execute(text("""
            SELECT 
                id,
                user_id,
                reputation_score,
                total_bounties_earned
            FROM researchers
            LIMIT 10
        """))
        
        researchers = result.fetchall()
        if researchers:
            print(f"Found {len(researchers)} researchers (showing first 10):")
            for researcher in researchers:
                print(f"  - ID: {researcher[0]}, User ID: {researcher[1]}")
                print(f"    Reputation: {researcher[2]}, Bounties: {researcher[3]}")
        else:
            print("  No researchers found!")
        
        # Get total count
        result = conn.execute(text("SELECT COUNT(*) FROM researchers"))
        total_researchers = result.scalar()
        print(f"\nTotal researchers: {total_researchers}")
        
        # Check organizations table
        print("\n5. ORGANIZATIONS TABLE:")
        print("-" * 80)
        result = conn.execute(text("""
            SELECT 
                id,
                name,
                created_at
            FROM organizations
            LIMIT 10
        """))
        
        orgs = result.fetchall()
        if orgs:
            print(f"Found {len(orgs)} organizations (showing first 10):")
            for org in orgs:
                print(f"  - ID: {org[0]}, Name: {org[1]}, Created: {org[2]}")
        else:
            print("  No organizations found!")
        
        # Get total count
        result = conn.execute(text("SELECT COUNT(*) FROM organizations"))
        total_orgs = result.scalar()
        print(f"\nTotal organizations: {total_orgs}")
        
        print("\n" + "=" * 80)
        print("SUMMARY:")
        print("=" * 80)
        print(f"Total Reports: {total_reports}")
        print(f"Total Programs: {total_programs}")
        print(f"Total Researchers: {total_researchers}")
        print(f"Total Organizations: {total_orgs}")
        print(f"Total Program-Researcher Joins: {total_joins}")
        print("=" * 80)

if __name__ == "__main__":
    check_database()
