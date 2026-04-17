"""
Check PTaaS Retest Schema
"""
from sqlalchemy import create_engine, inspect, text
from src.core.config import settings

# Create engine
engine = create_engine(settings.DATABASE_URL)

# Check table schema
inspector = inspect(engine)

print("=" * 80)
print("PTaaS Retest Requests Table Schema")
print("=" * 80)

if 'ptaas_retest_requests' in inspector.get_table_names():
    columns = inspector.get_columns('ptaas_retest_requests')
    for col in columns:
        print(f"{col['name']:30} {str(col['type']):20} nullable={col['nullable']}")
    
    print("\n" + "=" * 80)
    print("Sample Data from ptaas_retest_requests")
    print("=" * 80)
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, finding_id, engagement_id, requested_by, assigned_to, 
                   status, retest_result, retest_notes
            FROM ptaas_retest_requests
            LIMIT 5
        """))
        
        rows = result.fetchall()
        if rows:
            for row in rows:
                print(f"\nID: {row[0]}")
                print(f"Finding ID: {row[1]}")
                print(f"Engagement ID: {row[2]}")
                print(f"Requested By: {row[3]} (type: {type(row[3])})")
                print(f"Assigned To: {row[4]} (type: {type(row[4])})")
                print(f"Status: {row[5]}")
                print(f"Result: {row[6]}")
                print(f"Notes: {row[7]}")
        else:
            print("No retest requests found")
else:
    print("Table 'ptaas_retest_requests' does not exist!")

print("\n" + "=" * 80)
