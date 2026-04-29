"""create triage templates table

Revision ID: 2026_04_20_1200_create_triage_templates
Revises: 2026_03_29_1400_create_vrt_tables
Create Date: 2026-04-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_04_20_1200_create_triage_templates'
down_revision = '2026_03_29_1400_create_vrt_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create triage_templates table
    op.create_table(
        'triage_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(50), nullable=False, index=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'))
    )
    
    # Insert default templates
    op.execute("""
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
    """)


def downgrade():
    op.drop_table('triage_templates')
