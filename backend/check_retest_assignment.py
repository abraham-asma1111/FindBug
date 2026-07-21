"""
Check Retest Assignment and Engagement Researchers
"""
from sqlalchemy import create_engine, text
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL)

print("=" * 80)
print("Retest Request Details")
print("=" * 80)

with engine.connect() as conn:
    # Get retest details
    result = conn.execute(text("""
        SELECT 
            r.id as retest_id,
            r.finding_id,
            r.engagement_id,
            r.requested_by,
            r.assigned_to,
            r.status,
            f.title as finding_title
        FROM ptaas_retest_requests r
        JOIN ptaas_findings f ON f.id = r.finding_id
        WHERE r.id = '9edf8d63-fc5f-4565-a45e-ebaf79a8bf9b'
    """))
    
    retest = result.fetchone()
    if retest:
        print(f"Retest ID: {retest[0]}")
        print(f"Finding ID: {retest[1]}")
        print(f"Engagement ID: {retest[2]}")
        print(f"Requested By: {retest[3]}")
        print(f"Assigned To: {retest[4]}")
        print(f"Status: {retest[5]}")
        print(f"Finding Title: {retest[6]}")
        
        engagement_id = retest[2]
        
        print("\n" + "=" * 80)
        print("Engagement Details")
        print("=" * 80)
        
        # Get engagement details
        result = conn.execute(text("""
            SELECT 
                id,
                organization_id,
                assigned_researchers,
                status
            FROM ptaas_engagements
            WHERE id = :engagement_id
        """), {"engagement_id": engagement_id})
        
        engagement = result.fetchone()
        if engagement:
            print(f"Engagement ID: {engagement[0]}")
            print(f"Organization ID: {engagement[1]}")
            print(f"Assigned Researchers: {engagement[2]}")
            print(f"Status: {engagement[3]}")
        else:
            print("Engagement not found!")
        
        print("\n" + "=" * 80)
        print("Current User (Researcher)")
        print("=" * 80)
        
        # Get researcher user
        result = conn.execute(text("""
            SELECT 
                id,
                email,
                role,
                is_active
            FROM users
            WHERE role = 'researcher'
            LIMIT 1
        """))
        
        user = result.fetchone()
        if user:
            print(f"User ID: {user[0]}")
            print(f"Email: {user[1]}")
            print(f"Role: {user[2]}")
            print(f"Active: {user[3]}")
            
            # Check if user is in assigned_researchers
            if engagement and engagement[2]:
                assigned_list = engagement[2]
                user_id_str = str(user[0])
                print(f"\nUser ID as string: {user_id_str}")
                print(f"Is in assigned_researchers? {user_id_str in assigned_list}")
        else:
            print("No researcher user found!")
    else:
        print("Retest not found!")

print("\n" + "=" * 80)
