"""
Reset retest count for a finding to allow testing
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import sys

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/bugbounty')
engine = create_engine(DATABASE_URL)

finding_id = '992ced16-83e7-4c8e-896a-c5678e4d37b8'

if len(sys.argv) > 1:
    finding_id = sys.argv[1]

with engine.connect() as conn:
    # Delete all retest requests for this finding
    result = conn.execute(
        text('DELETE FROM ptaas_retest_requests WHERE finding_id = :finding_id'),
        {'finding_id': finding_id}
    )
    conn.commit()
    
    print(f'✓ Deleted {result.rowcount} retest requests for finding {finding_id}')
    print(f'✓ You can now test the retest functionality with this finding')
