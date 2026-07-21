"""
Check payment method status in database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models.payment_extended import PaymentMethod
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("=" * 80)
print("PAYMENT METHODS STATUS")
print("=" * 80)

# Get all payment methods
payment_methods = db.query(PaymentMethod).order_by(PaymentMethod.created_at.desc()).all()

print(f"\nTotal payment methods: {len(payment_methods)}\n")

for pm in payment_methods:
    status = "APPROVED" if pm.is_verified else "PENDING"
    print(f"ID: {pm.id}")
    print(f"  User ID: {pm.user_id}")
    print(f"  Type: {pm.method_type}")
    print(f"  Account: {pm.account_number}")
    print(f"  Status: {status}")
    print(f"  is_verified: {pm.is_verified}")
    print(f"  Created: {pm.created_at}")
    print()

db.close()
