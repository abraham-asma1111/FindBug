"""Check program statistics for an organization."""
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bug_bounty_production")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def check_program_stats():
    """Check program statistics."""
    db = SessionLocal()
    
    try:
        # Get organization
        org_id = "7c3b13e0-afb3-460b-b240-a74eb83e574c"
        
        print(f"\n{'='*80}")
        print(f"PROGRAM STATISTICS FOR ORGANIZATION: {org_id}")
        print(f"{'='*80}\n")
        
        # Get programs for this organization
        programs_query = text("""
            SELECT 
                p.id,
                p.name,
                p.status,
                p.type as program_type,
                p.visibility,
                p.created_at,
                -- Count reports
                (SELECT COUNT(*) FROM vulnerability_reports vr WHERE vr.program_id = p.id) as total_reports,
                (SELECT COUNT(*) FROM vulnerability_reports vr WHERE vr.program_id = p.id AND vr.status = 'valid') as valid_reports,
                (SELECT COUNT(*) FROM vulnerability_reports vr WHERE vr.program_id = p.id AND vr.status = 'resolved') as resolved_reports,
                -- Count researchers
                (SELECT COUNT(DISTINCT researcher_id) FROM program_participations pp WHERE pp.program_id = p.id) as total_researchers,
                (SELECT COUNT(DISTINCT vr.researcher_id) FROM vulnerability_reports vr WHERE vr.program_id = p.id) as researchers_with_reports,
                -- Bounty stats
                (SELECT COALESCE(SUM(bp.total_amount), 0) FROM bounty_payments bp 
                 JOIN vulnerability_reports vr ON bp.report_id = vr.id 
                 WHERE vr.program_id = p.id AND bp.status = 'completed') as total_bounties_paid,
                (SELECT COUNT(*) FROM bounty_payments bp 
                 JOIN vulnerability_reports vr ON bp.report_id = vr.id 
                 WHERE vr.program_id = p.id AND bp.status = 'pending') as pending_payments,
                -- Reward tiers
                (SELECT MIN(min_amount) FROM reward_tiers rt WHERE rt.program_id = p.id) as min_bounty,
                (SELECT MAX(max_amount) FROM reward_tiers rt WHERE rt.program_id = p.id) as max_bounty,
                -- Scopes
                (SELECT COUNT(*) FROM program_scopes ps WHERE ps.program_id = p.id AND ps.is_in_scope = true) as in_scope_count,
                (SELECT COUNT(*) FROM program_scopes ps WHERE ps.program_id = p.id AND ps.is_in_scope = false) as out_of_scope_count
            FROM bounty_programs p
            WHERE p.organization_id = :org_id
            ORDER BY p.created_at DESC
        """)
        
        programs = db.execute(programs_query, {"org_id": org_id}).fetchall()
        
        if not programs:
            print("❌ No programs found for this organization")
            return
        
        print(f"✅ Found {len(programs)} program(s)\n")
        
        for idx, program in enumerate(programs, 1):
            print(f"\n{'─'*80}")
            print(f"PROGRAM #{idx}: {program.name}")
            print(f"{'─'*80}")
            print(f"ID: {program.id}")
            print(f"Status: {program.status}")
            print(f"Type: {program.program_type}")
            print(f"Visibility: {program.visibility}")
            print(f"Created: {program.created_at}")
            
            print(f"\n📊 REPORT STATISTICS:")
            print(f"  • Total Reports: {program.total_reports}")
            print(f"  • Valid Reports: {program.valid_reports}")
            print(f"  • Resolved Reports: {program.resolved_reports}")
            
            print(f"\n👥 RESEARCHER STATISTICS:")
            print(f"  • Total Researchers Joined: {program.total_researchers}")
            print(f"  • Researchers with Reports: {program.researchers_with_reports}")
            
            print(f"\n💰 BOUNTY STATISTICS:")
            print(f"  • Total Bounties Paid: {program.total_bounties_paid:,.2f} ETB")
            print(f"  • Pending Payments: {program.pending_payments}")
            print(f"  • Bounty Range: {program.min_bounty or 0:,.2f} - {program.max_bounty or 0:,.2f} ETB")
            
            print(f"\n🎯 SCOPE STATISTICS:")
            print(f"  • In Scope Assets: {program.in_scope_count}")
            print(f"  • Out of Scope Assets: {program.out_of_scope_count}")
            
            # Get severity breakdown
            severity_query = text("""
                SELECT 
                    severity,
                    COUNT(*) as count
                FROM vulnerability_reports
                WHERE program_id = :program_id
                GROUP BY severity
                ORDER BY 
                    CASE severity
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                        WHEN 'info' THEN 5
                        ELSE 6
                    END
            """)
            
            severities = db.execute(severity_query, {"program_id": program.id}).fetchall()
            
            if severities:
                print(f"\n🔥 SEVERITY BREAKDOWN:")
                for sev in severities:
                    print(f"  • {sev.severity.upper()}: {sev.count} reports")
        
        print(f"\n{'='*80}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_program_stats()
