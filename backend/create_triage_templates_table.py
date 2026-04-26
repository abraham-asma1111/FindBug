"""
Create triage_templates table directly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from src.core.database import engine

def create_table():
    with engine.connect() as conn:
        # Create table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS triage_templates (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(100) NOT NULL UNIQUE,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                category VARCHAR(50) NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT true,
                created_by UUID REFERENCES users(id) ON DELETE SET NULL,
                created_at TIMESTAMP NOT NULL DEFAULT now(),
                updated_at TIMESTAMP NOT NULL DEFAULT now()
            );
        """))
        
        # Create indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_triage_templates_name ON triage_templates(name);
            CREATE INDEX IF NOT EXISTS idx_triage_templates_category ON triage_templates(category);
        """))
        
        # Insert default templates
        conn.execute(text("""
            INSERT INTO triage_templates (id, name, title, content, category, is_active, created_at, updated_at)
            VALUES 
            (gen_random_uuid(), 'validation_accepted', 'Report Validated', 
             'Thank you for your submission. We have validated this vulnerability and it has been accepted. Our team will review the severity and assign an appropriate reward.', 
             'validation', true, now(), now()),
            (gen_random_uuid(), 'validation_rejected', 'Report Rejected', 
             'Thank you for your submission. After careful review, we have determined this does not meet our program criteria. This may be due to: out of scope, insufficient impact, or not a security vulnerability.', 
             'rejection', true, now(), now()),
            (gen_random_uuid(), 'duplicate_found', 'Duplicate Report', 
             'This vulnerability has already been reported by another researcher. Please see the original report for details. Thank you for your submission.', 
             'duplicate', true, now(), now()),
            (gen_random_uuid(), 'need_more_info', 'Additional Information Needed', 
             'We need more information to validate this report. Please provide: detailed steps to reproduce, proof of concept, and impact assessment.', 
             'need_info', true, now(), now()),
            (gen_random_uuid(), 'resolved_confirmed', 'Vulnerability Resolved', 
             'The vulnerability has been successfully resolved and verified. Thank you for your contribution to improving our security.', 
             'resolved', true, now(), now())
            ON CONFLICT (name) DO NOTHING;
        """))
        
        conn.commit()
        print("✅ triage_templates table created successfully with 5 default templates")

if __name__ == "__main__":
    create_table()
