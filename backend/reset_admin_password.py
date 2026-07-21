"""Reset admin password."""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bounty_platform")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash the password
new_password = "admin123"
hashed = pwd_context.hash(new_password)

# Update admin user
result = session.execute(
    text("""
        UPDATE users 
        SET password_hash = :hash, is_active = true
        WHERE email = 'remainsecure@findbug.com'
        RETURNING id, email
    """),
    {"hash": hashed}
)
session.commit()

user = result.fetchone()
if user:
    print(f"✓ Password reset for: {user.email}")
    print(f"  New password: {new_password}")
else:
    print("✗ Admin user not found!")

session.close()
