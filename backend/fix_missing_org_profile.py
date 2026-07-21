"""
Fix missing organization profile for user
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# User ID from logs
user_id = '3d0d53c3-35b6-4859-a1a8-e0d8f15ba622'

# Check if user exists and has no organization profile
result = session.execute(text('''
    SELECT u.id, u.email, u.role, o.id as org_id
    FROM users u
    LEFT JOIN organizations o ON o.user_id = u.id
    WHERE u.id = :user_id
'''), {'user_id': user_id})

user_data = result.fetchone()

if not user_data:
    print(f"User {user_id} not found")
    exit(1)

if user_data.org_id:
    print(f"User {user_data.email} already has an organization profile")
    exit(0)

print(f"Creating organization profile for user: {user_data.email}")

# Create organization profile with correct fields
org_id = str(uuid.uuid4())
session.execute(text('''
    INSERT INTO organizations (
        id, user_id, company_name, phone_number,
        subscription_type, verification_status, created_at
    ) VALUES (
        :id, :user_id, :company_name, :phone_number,
        :subscription_type, :verification_status, NOW()
    )
'''), {
    'id': org_id,
    'user_id': user_id,
    'company_name': 'Test Company',  # Default value
    'phone_number': '+251900000000',
    'subscription_type': 'basic',
    'verification_status': 'pending'
})

session.commit()
print(f"✅ Organization profile created with ID: {org_id}")
print("User can now access the organization dashboard")
