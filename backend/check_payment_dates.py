#!/usr/bin/env python3
"""
Check payment dates and amounts to debug date filtering issue
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from src.domain.models.bounty_payment import BountyPayment
from dotenv import load_dotenv

load_dotenv()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/bountymatch')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

print("=" * 80)
print("PAYMENT DATE ANALYSIS")
print("=" * 80)

# Get all approved payments
all_payments = db.query(BountyPayment).filter(
    BountyPayment.status == 'approved'
).order_by(BountyPayment.created_at.desc()).all()

print(f"\nTotal Approved Payments: {len(all_payments)}")
print(f"Total Amount: {sum(p.researcher_amount for p in all_payments):,.2f} ETB")

# Show payment dates
print("\n" + "=" * 80)
print("PAYMENT DATES AND AMOUNTS:")
print("=" * 80)
for p in all_payments:
    print(f"Payment ID: {p.payment_id}")
    print(f"  Created: {p.created_at}")
    print(f"  Amount: {p.researcher_amount:,.2f} ETB")
    print(f"  Transaction: {p.transaction_id}")
    print()

# Calculate date ranges
now = datetime.utcnow()
last_30_days = now - timedelta(days=30)
last_90_days = now - timedelta(days=90)

print("=" * 80)
print("DATE RANGE ANALYSIS:")
print("=" * 80)
print(f"Current Date: {now}")
print(f"Last 30 Days Start: {last_30_days}")
print(f"Last 90 Days Start: {last_90_days}")

# Payments in last 30 days
payments_30d = [p for p in all_payments if p.created_at >= last_30_days]
print(f"\nPayments in Last 30 Days: {len(payments_30d)}")
print(f"Total Amount (30d): {sum(p.researcher_amount for p in payments_30d):,.2f} ETB")

# Payments in last 90 days
payments_90d = [p for p in all_payments if p.created_at >= last_90_days]
print(f"\nPayments in Last 90 Days: {len(payments_90d)}")
print(f"Total Amount (90d): {sum(p.researcher_amount for p in payments_90d):,.2f} ETB")

# Show which payments are in 90d but not in 30d
payments_30_to_90 = [p for p in all_payments if last_90_days <= p.created_at < last_30_days]
print(f"\nPayments between 30-90 days ago: {len(payments_30_to_90)}")
print(f"Total Amount (30-90d): {sum(p.researcher_amount for p in payments_30_to_90):,.2f} ETB")

db.close()
print("\n" + "=" * 80)
