#!/usr/bin/env python3
"""
Show all reports and programs data with correct column names
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bugbounty")

def show_data():
    """Show vulnerability_reports and bounty_programs with correct columns"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("=" * 100)
        print("WHERE ARE THE REPORTS AND PROGRAMS?")
        print("=" * 100)
        
        # Check vulnerability_reports
        print("\n📋 VULNERABILITY_REPORTS TABLE:")
        print("-" * 100)
        result = conn.execute(text("""
            SELECT 
                id,
                report_number,
                title,
                suggested_severity,
                status,
                researcher_id,
                program_id,
                submitted_at
            FROM vulnerability_reports
            ORDER BY submitted_at DESC
        """))
        
        reports = result.fetchall()
        if reports:
            print(f"\n✓ Found {len(reports)} vulnerability reports:\n")
            for i, report in enumerate(reports, 1):
                print(f"{i}. Report #{report[1]}")
                print(f"   ID: {report[0]}")
                print(f"   Title: {report[2]}")
                print(f"   Severity: {report[3]}")
                print(f"   Status: {report[4]}")
                print(f"   Researcher: {report[5]}")
                print(f"   Program: {report[6]}")
                print(f"   Submitted: {report[7]}")
                print()
        else:
            print("❌ No reports found!")
        
        # Check bounty_programs
        print("\n🎯 BOUNTY_PROGRAMS TABLE:")
        print("-" * 100)
        result = conn.execute(text("""
            SELECT 
                id,
                name,
                type,
                status,
                visibility,
                organization_id,
                created_at
            FROM bounty_programs
            ORDER BY created_at DESC
        """))
        
        programs = result.fetchall()
        if programs:
            print(f"\n✓ Found {len(programs)} bounty programs:\n")
            for i, program in enumerate(programs, 1):
                print(f"{i}. {program[1]}")
                print(f"   ID: {program[0]}")
                print(f"   Type: {program[2]}")
                print(f"   Status: {program[3]}")
                print(f"   Visibility: {program[4]}")
                print(f"   Organization: {program[5]}")
                print(f"   Created: {program[6]}")
                print()
        else:
            print("❌ No programs found!")
        
        # Check program_participations
        print("\n👥 PROGRAM_PARTICIPATIONS TABLE:")
        print("-" * 100)
        result = conn.execute(text("""
            SELECT 
                pp.program_id,
                pp.researcher_id,
                pp.joined_at,
                pp.status,
                bp.name as program_name
            FROM program_participations pp
            JOIN bounty_programs bp ON pp.program_id = bp.id
            ORDER BY pp.joined_at DESC
        """))
        
        participations = result.fetchall()
        if participations:
            print(f"\n✓ Found {len(participations)} program participations:\n")
            for i, part in enumerate(participations, 1):
                print(f"{i}. Program: {part[4]}")
                print(f"   Program ID: {part[0]}")
                print(f"   Researcher ID: {part[1]}")
                print(f"   Joined: {part[2]}")
                print(f"   Status: {part[3]}")
                print()
        else:
            print("❌ No participations found!")
        
        # Summary with cross-reference
        print("\n" + "=" * 100)
        print("🔍 CROSS-REFERENCE ANALYSIS:")
        print("=" * 100)
        
        # Check which programs have reports
        result = conn.execute(text("""
            SELECT 
                bp.id,
                bp.name,
                COUNT(vr.id) as report_count
            FROM bounty_programs bp
            LEFT JOIN vulnerability_reports vr ON bp.id = vr.program_id
            GROUP BY bp.id, bp.name
            ORDER BY report_count DESC
        """))
        
        program_reports = result.fetchall()
        print("\n📊 Reports per Program:")
        for prog in program_reports:
            print(f"  • {prog[1]}: {prog[2]} reports")
        
        # Check which researchers have submitted reports
        result = conn.execute(text("""
            SELECT 
                r.id,
                u.email,
                COUNT(vr.id) as report_count
            FROM researchers r
            JOIN users u ON r.user_id = u.id
            LEFT JOIN vulnerability_reports vr ON r.id = vr.researcher_id
            GROUP BY r.id, u.email
            HAVING COUNT(vr.id) > 0
            ORDER BY report_count DESC
        """))
        
        researcher_reports = result.fetchall()
        print("\n👤 Reports per Researcher:")
        for res in researcher_reports:
            print(f"  • {res[1]}: {res[2]} reports")
        
        print("\n" + "=" * 100)
        print("✅ SUMMARY:")
        print("=" * 100)
        print(f"Total Vulnerability Reports: {len(reports)}")
        print(f"Total Bounty Programs: {len(programs)}")
        print(f"Total Program Participations: {len(participations)}")
        print("=" * 100)

if __name__ == "__main__":
    show_data()
