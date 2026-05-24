#!/usr/bin/env python3
"""Check bounty payment data in database."""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Check bounty payments
result = session.execute(text('''
    SELECT 
        COUNT(*) as total_reports,
        COUNT(CASE WHEN bounty_status = 'paid' THEN 1 END) as paid_count,
        COUNT(CASE WHEN bounty_status = 'approved' THEN 1 END) as approved_count,
        SUM(CASE WHEN bounty_status = 'paid' THEN bounty_amount ELSE 0 END) as total_paid,
        SUM(CASE WHEN bounty_status = 'approved' THEN bounty_amount ELSE 0 END) as total_pending
    FROM vulnerability_reports
    WHERE bounty_amount IS NOT NULL
''')).fetchone()

print('📊 Bounty Payment Status:')
print(f'Total reports with bounty: {result[0]}')
print(f'Paid bounties: {result[1]}')
print(f'Approved (pending) bounties: {result[2]}')
print(f'Total paid amount: ${result[3] or 0}')
print(f'Total pending amount: ${result[4] or 0}')

# Check if there are any reports at all
total_reports = session.execute(text('SELECT COUNT(*) FROM vulnerability_reports')).scalar()
print(f'\n📋 Total reports in database: {total_reports}')

# Sample some reports
sample = session.execute(text('''
    SELECT id, title, bounty_amount, bounty_status 
    FROM vulnerability_reports 
    LIMIT 5
''')).fetchall()

print('\n📝 Sample reports:')
for r in sample:
    print(f'  - {r[1]}: ${r[2] or 0} ({r[3] or "no status"})')

session.close()
