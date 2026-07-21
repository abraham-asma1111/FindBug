"""Reset AI Red Teaming report to NEW status"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/bountyplatform')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

# Reset the jailbreak report to NEW status
query = text('''
    UPDATE ai_vulnerability_reports
    SET 
        status = 'NEW',
        validated_at = NULL
    WHERE title = 'jailbreak'
    RETURNING report_id, title, status, validated_at
''')

result = db.execute(query)
db.commit()

report = result.fetchone()

if report:
    print('Report Reset Successfully:')
    print('=' * 60)
    print(f'ID: {report[0]}')
    print(f'Title: {report[1]}')
    print(f'Status: {report[2]}')
    print(f'validated_at: {report[3]}')
    print('=' * 60)
    print('\n✓ Report is now in NEW status, awaiting triage')
else:
    print('Report not found')

db.close()
