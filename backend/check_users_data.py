"""Check users in database."""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bounty_platform")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

print("=== Checking Users Table ===\n")

# Count total users
result = session.execute(text("SELECT COUNT(*) FROM users"))
total = result.scalar()
print(f"Total users: {total}")

# Count by role
result = session.execute(text("""
    SELECT role, COUNT(*) as count 
    FROM users 
    WHERE deleted_at IS NULL
    GROUP BY role 
    ORDER BY count DESC
"""))
print("\nUsers by role:")
for row in result:
    print(f"  {row.role}: {row.count}")

# Show sample users
result = session.execute(text("""
    SELECT id, email, role, is_active, created_at
    FROM users 
    WHERE deleted_at IS NULL
    ORDER BY created_at DESC
    LIMIT 10
"""))
print("\nSample users (most recent 10):")
for row in result:
    print(f"  {row.email} | {row.role} | Active: {row.is_active} | Created: {row.created_at}")

# Check admin user
result = session.execute(text("""
    SELECT id, email, role, is_active 
    FROM users 
    WHERE email = 'remainsecure@findbug.com'
"""))
admin = result.fetchone()
if admin:
    print(f"\n✓ Admin user found: {admin.email} | Active: {admin.is_active}")
else:
    print("\n✗ Admin user NOT found!")

session.close()
