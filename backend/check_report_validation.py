"""Check AI Red Teaming report validation status"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/bountyplatform')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

# Check the jailbreak report
query = text('''
    SELECT 
        report_id,
        title,
        status,
        validated_at,
        classification
    FROM ai_vulnerability_reports
    WHERE title = 'jailbreak'
    LIMIT 1
''')

result = db.execute(query)
report = result.fetchone()

if report:
    print('Report Details:')
    print('=' * 60)
    print(f'ID: {report[0]}')
    print(f'Title: {report[1]}')
    print(f'Status: {report[2]}')
    print(f'validated_at: {report[3]}')
    print(f'classification: {report[4]}')
    print('=' * 60)
    
    # Check if this should show validation status
    if report[3] is not None:
        print('\n✓ Validation status SHOULD be displayed')
        print(f'  Date: {report[3]}')
    else:
        print('\n✓ No validation data - status should NOT be displayed')
else:
    print('Report not found')

db.close()
