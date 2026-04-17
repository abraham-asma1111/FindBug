"""
Assign researcher to PTaaS engagement
"""
from sqlalchemy import create_engine, text
from src.core.config import settings
import json

engine = create_engine(settings.DATABASE_URL)

engagement_id = '983fbea0-683e-488a-97e1-44d93ba7f8d0'

print("=" * 80)
print("Getting current researcher user")
print("=" * 80)

with engine.connect() as conn:
    # Get researcher user (the one currently logged in)
    result = conn.execute(text("""
        SELECT id, email, role
        FROM users
        WHERE email LIKE '%researcher%'
        ORDER BY created_at DESC
        LIMIT 1
    """))
    
    researcher = result.fetchone()
    if researcher:
        researcher_id = str(researcher[0])
        print(f"Researcher ID: {researcher_id}")
        print(f"Email: {researcher[1]}")
        print(f"Role: {researcher[2]}")
        
        # Get current engagement
        result = conn.execute(text("""
            SELECT id, assigned_researchers
            FROM ptaas_engagements
            WHERE id = :engagement_id
        """), {"engagement_id": engagement_id})
        
        engagement = result.fetchone()
        if engagement:
            current_researchers = engagement[1] or []
            print(f"\nCurrent assigned researchers: {current_researchers}")
            
            if researcher_id not in current_researchers:
                # Add researcher to the list
                new_researchers = current_researchers + [researcher_id]
                
                conn.execute(text("""
                    UPDATE ptaas_engagements
                    SET assigned_researchers = :researchers
                    WHERE id = :engagement_id
                """), {
                    "researchers": json.dumps(new_researchers),
                    "engagement_id": engagement_id
                })
                conn.commit()
                
                print(f"\n✅ Added researcher {researcher_id} to engagement")
                print(f"New assigned researchers: {new_researchers}")
            else:
                print(f"\n✅ Researcher {researcher_id} is already assigned to engagement")
        else:
            print("Engagement not found!")
    else:
        print("No researcher user found!")

print("\n" + "=" * 80)
