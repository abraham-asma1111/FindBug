"""enhance ptaas findings structure

Revision ID: 2026_03_20_1230
Revises: 2026_03_20_1200
Create Date: 2026-03-20 12:30:00.000000

FREQ-35: Structured Finding Templates with Mandatory Fields
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_20_1230'
down_revision = '2026_03_20_1200'
branch_labels = None
depends_on = None


def upgrade():
    # Add structured template fields to ptaas_findings
    op.add_column('ptaas_findings', sa.Column('proof_of_exploit', sa.Text(), nullable=True))
    op.add_column('ptaas_findings', sa.Column('exploit_code', sa.Text(), nullable=True))
    op.add_column('ptaas_findings', sa.Column('exploit_screenshots', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('ptaas_findings', sa.Column('exploit_video_url', sa.String(length=500), nullable=True))
    
    # Impact analysis fields
    op.add_column('ptaas_findings', sa.Column('impact_analysis', sa.Text(), nullable=True))
    op.add_column('ptaas_findings', sa.Column('business_impact', sa.String(length=50), nullable=True))
    op.add_column('ptaas_findings', sa.Column('technical_impact', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('ptaas_findings', sa.Column('affected_users', sa.String(length=100), nullable=True))
    op.add_column('ptaas_findings', sa.Column('data_at_risk', sa.Text(), nullable=True))
    
    # Enhanced remediation fields
    op.add_column('ptaas_findings', sa.Column('remediation_priority', sa.String(length=50), nullable=True))
    op.add_column('ptaas_findings', sa.Column('remediation_effort', sa.String(length=50), nullable=True))
    op.add_column('ptaas_findings', sa.Column('remediation_steps', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('ptaas_findings', sa.Column('code_fix_example', sa.Text(), nullable=True))
    
    # Vulnerability classification
    op.add_column('ptaas_findings', sa.Column('vulnerability_type', sa.String(length=100), nullable=True))
    op.add_column('ptaas_findings', sa.Column('cwe_id', sa.String(length=50), nullable=True))
    op.add_column('ptaas_findings', sa.Column('owasp_category', sa.String(length=100), nullable=True))
    
    # Attack vector details
    op.add_column('ptaas_findings', sa.Column('attack_vector', sa.String(length=50), nullable=True))
    op.add_column('ptaas_findings', sa.Column('attack_complexity', sa.String(length=50), nullable=True))
    op.add_column('ptaas_findings', sa.Column('privileges_required', sa.String(length=50), nullable=True))
    op.add_column('ptaas_findings', sa.Column('user_interaction', sa.String(length=50), nullable=True))
    
    # Validation and review
    op.add_column('ptaas_findings', sa.Column('validated', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('ptaas_findings', sa.Column('validated_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('ptaas_findings', sa.Column('validated_at', sa.DateTime(), nullable=True))
    op.add_column('ptaas_findings', sa.Column('retest_required', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('ptaas_findings', sa.Column('retest_notes', sa.Text(), nullable=True))
    
    # Template compliance
    op.add_column('ptaas_findings', sa.Column('template_version', sa.String(length=20), nullable=True))
    op.add_column('ptaas_findings', sa.Column('mandatory_fields_complete', sa.Boolean(), nullable=True, server_default='false'))
    
    # Add foreign key for validated_by
    op.create_foreign_key(
        'fk_ptaas_findings_validated_by',
        'ptaas_findings',
        'users',
        ['validated_by'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Add indexes for new fields
    op.create_index('ix_ptaas_findings_vulnerability_type', 'ptaas_findings', ['vulnerability_type'])
    op.create_index('ix_ptaas_findings_validated', 'ptaas_findings', ['validated'])
    op.create_index('ix_ptaas_findings_mandatory_complete', 'ptaas_findings', ['mandatory_fields_complete'])


def downgrade():
    op.drop_index('ix_ptaas_findings_mandatory_complete', table_name='ptaas_findings')
    op.drop_index('ix_ptaas_findings_validated', table_name='ptaas_findings')
    op.drop_index('ix_ptaas_findings_vulnerability_type', table_name='ptaas_findings')
    
    op.drop_constraint('fk_ptaas_findings_validated_by', 'ptaas_findings', type_='foreignkey')
    
    op.drop_column('ptaas_findings', 'mandatory_fields_complete')
    op.drop_column('ptaas_findings', 'template_version')
    op.drop_column('ptaas_findings', 'retest_notes')
    op.drop_column('ptaas_findings', 'retest_required')
    op.drop_column('ptaas_findings', 'validated_at')
    op.drop_column('ptaas_findings', 'validated_by')
    op.drop_column('ptaas_findings', 'validated')
    op.drop_column('ptaas_findings', 'user_interaction')
    op.drop_column('ptaas_findings', 'privileges_required')
    op.drop_column('ptaas_findings', 'attack_complexity')
    op.drop_column('ptaas_findings', 'attack_vector')
    op.drop_column('ptaas_findings', 'owasp_category')
    op.drop_column('ptaas_findings', 'cwe_id')
    op.drop_column('ptaas_findings', 'vulnerability_type')
    op.drop_column('ptaas_findings', 'code_fix_example')
    op.drop_column('ptaas_findings', 'remediation_steps')
    op.drop_column('ptaas_findings', 'remediation_effort')
    op.drop_column('ptaas_findings', 'remediation_priority')
    op.drop_column('ptaas_findings', 'data_at_risk')
    op.drop_column('ptaas_findings', 'affected_users')
    op.drop_column('ptaas_findings', 'technical_impact')
    op.drop_column('ptaas_findings', 'business_impact')
    op.drop_column('ptaas_findings', 'impact_analysis')
    op.drop_column('ptaas_findings', 'exploit_video_url')
    op.drop_column('ptaas_findings', 'exploit_screenshots')
    op.drop_column('ptaas_findings', 'exploit_code')
    op.drop_column('ptaas_findings', 'proof_of_exploit')
