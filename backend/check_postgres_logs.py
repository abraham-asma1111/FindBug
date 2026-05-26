#!/usr/bin/env python3
"""
Check PostgreSQL logs and database deletion history
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bugbounty")

def check_deletion_history():
    """Check for deletion history in the database"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("=" * 100)
        print("DATABASE DELETION HISTORY CHECK")
        print("=" * 100)
        
        # 1. Check PostgreSQL version and logging settings
        print("\n1. POSTGRESQL CONFIGURATION:")
        print("-" * 100)
        try:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"PostgreSQL Version: {version}")
            
            # Check logging settings
            result = conn.execute(text("SHOW log_statement"))
            log_statement = result.scalar()
            print(f"log_statement: {log_statement}")
            
            result = conn.execute(text("SHOW log_min_duration_statement"))
            log_duration = result.scalar()
            print(f"log_min_duration_statement: {log_duration}")
            
            result = conn.execute(text("SHOW data_directory"))
            data_dir = result.scalar()
            print(f"data_directory: {data_dir}")
        except Exception as e:
            print(f"Error checking config: {e}")
        
        # 2. Check for soft-deleted records with timestamps
        print("\n\n2. SOFT-DELETED RECORDS:")
        print("-" * 100)
        
        # Vulnerability reports
        result = conn.execute(text("""
            SELECT 
                report_number,
                title,
                deleted_at,
                submitted_at
            FROM vulnerability_reports
            WHERE deleted_at IS NOT NULL
            ORDER BY deleted_at DESC
        """))
        
        deleted_reports = result.fetchall()
        if deleted_reports:
            print(f"\n✓ Found {len(deleted_reports)} soft-deleted vulnerability reports:")
            for rep in deleted_reports:
                print(f"  • {rep[0]}: {rep[1]}")
                print(f"    Submitted: {rep[3]}")
                print(f"    Deleted: {rep[2]}")
                print()
        else:
            print("  No soft-deleted reports found")
        
        # 3. Check report_status_history for deletion patterns
        print("\n3. REPORT STATUS HISTORY (Status Changes):")
        print("-" * 100)
        result = conn.execute(text("""
            SELECT 
                rsh.report_id,
                vr.report_number,
                rsh.from_status,
                rsh.to_status,
                rsh.change_reason,
                rsh.changed_at,
                u.email as changed_by_email
            FROM report_status_history rsh
            LEFT JOIN vulnerability_reports vr ON rsh.report_id = vr.id
            LEFT JOIN users u ON rsh.changed_by = u.id
            ORDER BY rsh.changed_at DESC
            LIMIT 20
        """))
        
        status_changes = result.fetchall()
        if status_changes:
            print(f"\n✓ Found {len(status_changes)} recent status changes (showing last 20):")
            for change in status_changes:
                print(f"  • Report {change[1] or 'Unknown'}")
                print(f"    {change[2]} → {change[3]}")
                print(f"    Reason: {change[4] or 'N/A'}")
                print(f"    Changed by: {change[6] or 'Unknown'}")
                print(f"    When: {change[5]}")
                print()
        else:
            print("  No status history found")
        
        # 4. Check for TRUNCATE or DROP operations in pg_stat_statements (if available)
        print("\n4. CHECKING FOR pg_stat_statements EXTENSION:")
        print("-" * 100)
        try:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
                )
            """))
            has_pg_stat = result.scalar()
            
            if has_pg_stat:
                print("✓ pg_stat_statements extension is installed")
                result = conn.execute(text("""
                    SELECT 
                        query,
                        calls,
                        total_exec_time,
                        mean_exec_time
                    FROM pg_stat_statements
                    WHERE query ILIKE '%DELETE%' 
                       OR query ILIKE '%TRUNCATE%'
                       OR query ILIKE '%DROP%'
                    ORDER BY calls DESC
                    LIMIT 10
                """))
                
                queries = result.fetchall()
                if queries:
                    print(f"\nFound {len(queries)} DELETE/TRUNCATE/DROP queries:")
                    for q in queries:
                        print(f"  • Calls: {q[1]}, Query: {q[0][:100]}...")
                else:
                    print("  No DELETE/TRUNCATE/DROP queries found")
            else:
                print("✗ pg_stat_statements extension is NOT installed")
                print("  To enable: CREATE EXTENSION pg_stat_statements;")
        except Exception as e:
            print(f"  Error checking pg_stat_statements: {e}")
        
        # 5. Check database activity/connections
        print("\n\n5. CURRENT DATABASE ACTIVITY:")
        print("-" * 100)
        try:
            result = conn.execute(text("""
                SELECT 
                    datname,
                    usename,
                    application_name,
                    state,
                    query_start,
                    LEFT(query, 100) as query_preview
                FROM pg_stat_activity
                WHERE datname = current_database()
                  AND pid != pg_backend_pid()
                ORDER BY query_start DESC
                LIMIT 10
            """))
            
            activities = result.fetchall()
            if activities:
                print(f"\n✓ Found {len(activities)} active connections:")
                for act in activities:
                    print(f"  • User: {act[1]}, App: {act[2]}, State: {act[3]}")
                    print(f"    Query: {act[5] or 'idle'}...")
                    print()
            else:
                print("  No other active connections")
        except Exception as e:
            print(f"  Error checking activity: {e}")
        
        # 6. Check for database size changes (if we have historical data)
        print("\n6. DATABASE SIZE:")
        print("-" * 100)
        try:
            result = conn.execute(text("""
                SELECT 
                    pg_size_pretty(pg_database_size(current_database())) as db_size,
                    pg_database_size(current_database()) as db_size_bytes
            """))
            
            size_info = result.fetchone()
            print(f"  Current database size: {size_info[0]} ({size_info[1]:,} bytes)")
            
            # Check table sizes
            result = conn.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                LIMIT 10
            """))
            
            tables = result.fetchall()
            print("\n  Top 10 largest tables:")
            for table in tables:
                print(f"    • {table[1]}: {table[2]}")
        except Exception as e:
            print(f"  Error checking size: {e}")
        
        # 7. Summary
        print("\n" + "=" * 100)
        print("SUMMARY:")
        print("=" * 100)
        print(f"Soft-deleted reports found: {len(deleted_reports)}")
        print(f"Status changes recorded: {len(status_changes)}")
        print("\nTo view PostgreSQL server logs, check:")
        print("  • Docker: docker logs <postgres_container_name>")
        print("  • System: /var/log/postgresql/postgresql-*.log")
        print("  • Or run: docker-compose logs postgres")
        print("=" * 100)

if __name__ == "__main__":
    check_deletion_history()
