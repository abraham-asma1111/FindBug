#!/usr/bin/env python3
"""
Simple script to reactivate a deactivated admin user using direct SQL
"""
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database connection
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "bounty_platform")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


def reactivate_admin():
    """Reactivate admin user"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # Get all admin users
        cursor.execute("""
            SELECT id, email, full_name, is_active, created_at 
            FROM users 
            WHERE role = 'admin'
            ORDER BY created_at
        """)
        admins = cursor.fetchall()
        
        if not admins:
            print("❌ No admin users found in database")
            return
        
        print("\n📋 Admin Users:")
        print("-" * 80)
        for idx, (user_id, email, full_name, is_active, created_at) in enumerate(admins, 1):
            status = "✅ ACTIVE" if is_active else "❌ INACTIVE"
            print(f"{idx}. {email}")
            print(f"   Name: {full_name or 'N/A'}")
            print(f"   ID: {user_id}")
            print(f"   Status: {status}")
            print(f"   Created: {created_at}")
            print("-" * 80)
        
        # Ask which admin to reactivate
        print("\nEnter the number of the admin to reactivate (or 'all' for all inactive admins):")
        choice = input("Choice: ").strip().lower()
        
        if choice == 'all':
            # Reactivate all inactive admins
            cursor.execute("""
                UPDATE users 
                SET is_active = true 
                WHERE role = 'admin' AND is_active = false
                RETURNING email
            """)
            reactivated = cursor.fetchall()
            
            if not reactivated:
                print("\n✅ All admin users are already active!")
            else:
                conn.commit()
                for (email,) in reactivated:
                    print(f"✅ Reactivated: {email}")
                print(f"\n✅ Successfully reactivated {len(reactivated)} admin user(s)")
        else:
            try:
                idx = int(choice) - 1
                if idx < 0 or idx >= len(admins):
                    print("❌ Invalid choice")
                    return
                
                user_id, email, full_name, is_active, created_at = admins[idx]
                
                if is_active:
                    print(f"\n✅ {email} is already active!")
                else:
                    cursor.execute("""
                        UPDATE users 
                        SET is_active = true 
                        WHERE id = %s
                    """, (user_id,))
                    conn.commit()
                    print(f"\n✅ Successfully reactivated: {email}")
                    print(f"   You can now log in with this account")
            except ValueError:
                print("❌ Invalid input. Please enter a number or 'all'")
        
        cursor.close()
        conn.close()
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🔧 Admin User Reactivation Tool")
    print("=" * 80)
    reactivate_admin()
