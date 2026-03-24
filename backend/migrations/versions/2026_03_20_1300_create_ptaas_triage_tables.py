"""create ptaas triage tables

Revision ID: 2026_03_20_1300
Revises: 2026_03_20_1230
Create Date: 2026-03-20 13:00:00.000000

FREQ-36: PTaaS Triage and Executive Reporting
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_20_1300'
down_revision = '2026_03_20_1230'
branch_labels = None
depends_on = None


def upgrade():
    # PTaaS Finding Triage
    op.create_table(
        'ptaas_finding_triage',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('finding_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('triaged_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('triaged_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('triage_status', sa.String(length=50), nullable=True, server_default='PENDING'),
        sa.Column('triage_notes', sa.Text(), nullable=True),
        sa.Column('priority_score', sa.Integer(), nullable=False),
        sa.Column('priority_level', sa.String(length=50), nullable=False),
        sa.Column('priority_justification', sa.Text(), nullable=True),
        sa.Column('risk_rating', sa.String(length=50), nullable=False),
        sa.Column('likelihood', sa.String(length=50), nullable=True),
        sa.Column('impact_score', sa.Integer(), nullable=True),
        sa.Column('exploitability_score', sa.Integer(), nullable=True),
        sa.Column('compliance_frameworks', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('compliance_controls', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('regulatory_impact', sa.Text(), nullable=True),
        sa.Column('evidence_validated', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('evidence_quality', sa.String(length=50), nullable=True),
        sa.Column('evidence_notes', sa.Text(), nullable=True),
        sa.Column('recommended_action', sa.String(length=100), nullable=True),
        sa.Column('estimated_fix_time', sa.String(length=50), nullable=True),
        sa.Column('executive_summary', sa.Text(), nullable=True),
        sa.Column('business_context', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['finding_id'], ['ptaas_findings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['triaged_by'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('finding_id')
    )
    op.create_index('ix_ptaas_finding_triage_id', 'ptaas_finding_triage', ['id'])
    op.create_index('ix_ptaas_finding_triage_finding_id', 'ptaas_finding_triage', ['finding_id'])
    op.create_index('ix_ptaas_finding_triage_status', 'ptaas_finding_triage', ['triage_status'])
    op.create_index('ix_ptaas_finding_triage_priority', 'ptaas_finding_triage', ['priority_level'])
    
    # PTaaS Executive Reports
    op.create_table(
        'ptaas_executive_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('report_title', sa.String(length=255), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=True, server_default='EXECUTIVE'),
        sa.Column('generated_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('report_period_start', sa.DateTime(), nullable=True),
        sa.Column('report_period_end', sa.DateTime(), nullable=True),
        sa.Column('executive_summary', sa.Text(), nullable=False),
        sa.Column('key_findings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('overall_risk_rating', sa.String(length=50), nullable=False),
        sa.Column('total_findings', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('critical_findings', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('high_findings', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('medium_findings', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('low_findings', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('risk_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('risk_trend', sa.String(length=50), nullable=True),
        sa.Column('compliance_status', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('compliance_gaps', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('compliance_recommendations', sa.Text(), nullable=True),
        sa.Column('immediate_actions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('short_term_actions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('long_term_actions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('evidence_summary', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('report_file_path', sa.String(length=500), nullable=True),
        sa.Column('report_file_url', sa.String(length=500), nullable=True),
        sa.Column('approved', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('distributed_to', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('distributed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['engagement_id'], ['ptaas_engagements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['generated_by'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ptaas_executive_reports_id', 'ptaas_executive_reports', ['id'])
    op.create_index('ix_ptaas_executive_reports_engagement_id', 'ptaas_executive_reports', ['engagement_id'])
    op.create_index('ix_ptaas_executive_reports_approved', 'ptaas_executive_reports', ['approved'])
    
    # PTaaS Finding Prioritization
    op.create_table(
        'ptaas_finding_prioritization',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('finding_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('prioritized_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('prioritized_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('old_priority', sa.String(length=50), nullable=True),
        sa.Column('new_priority', sa.String(length=50), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('factors_considered', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['finding_id'], ['ptaas_findings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['prioritized_by'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ptaas_finding_prioritization_id', 'ptaas_finding_prioritization', ['id'])
    op.create_index('ix_ptaas_finding_prioritization_finding_id', 'ptaas_finding_prioritization', ['finding_id'])


def downgrade():
    op.drop_index('ix_ptaas_finding_prioritization_finding_id', table_name='ptaas_finding_prioritization')
    op.drop_index('ix_ptaas_finding_prioritization_id', table_name='ptaas_finding_prioritization')
    op.drop_table('ptaas_finding_prioritization')
    
    op.drop_index('ix_ptaas_executive_reports_approved', table_name='ptaas_executive_reports')
    op.drop_index('ix_ptaas_executive_reports_engagement_id', table_name='ptaas_executive_reports')
    op.drop_index('ix_ptaas_executive_reports_id', table_name='ptaas_executive_reports')
    op.drop_table('ptaas_executive_reports')
    
    op.drop_index('ix_ptaas_finding_triage_priority', table_name='ptaas_finding_triage')
    op.drop_index('ix_ptaas_finding_triage_status', table_name='ptaas_finding_triage')
    op.drop_index('ix_ptaas_finding_triage_finding_id', table_name='ptaas_finding_triage')
    op.drop_index('ix_ptaas_finding_triage_id', table_name='ptaas_finding_triage')
    op.drop_table('ptaas_finding_triage')
