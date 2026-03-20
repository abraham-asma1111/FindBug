"""create ptaas retest tables

Revision ID: 2026_03_20_1330
Revises: 2026_03_20_1300
Create Date: 2026-03-20 13:30:00.000000

FREQ-37: Free Retesting Support
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_20_1330'
down_revision = '2026_03_20_1300'
branch_labels = None
depends_on = None


def upgrade():
    # PTaaS Retest Policy
    op.create_table(
        'ptaas_retest_policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('engagement_id', sa.Integer(), nullable=False),
        sa.Column('retest_period_months', sa.Integer(), nullable=False, server_default='12'),
        sa.Column('max_free_retests_per_finding', sa.Integer(), nullable=True, server_default='3'),
        sa.Column('eligible_severities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('requires_fix_evidence', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('requires_approval', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('target_turnaround_days', sa.Integer(), nullable=True, server_default='5'),
        sa.Column('allow_partial_fixes', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('allow_new_findings_during_retest', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('notify_on_request', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('notify_on_completion', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['engagement_id'], ['ptaas_engagements.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('engagement_id')
    )
    op.create_index('ix_ptaas_retest_policies_id', 'ptaas_retest_policies', ['id'])
    op.create_index('ix_ptaas_retest_policies_engagement_id', 'ptaas_retest_policies', ['engagement_id'])
    
    # PTaaS Retest Requests
    op.create_table(
        'ptaas_retest_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('finding_id', sa.Integer(), nullable=False),
        sa.Column('engagement_id', sa.Integer(), nullable=False),
        sa.Column('requested_by', sa.Integer(), nullable=False),
        sa.Column('requested_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='PENDING'),
        sa.Column('fix_description', sa.Text(), nullable=False),
        sa.Column('fix_implemented_at', sa.DateTime(), nullable=True),
        sa.Column('fix_evidence', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
        sa.Column('retest_started_at', sa.DateTime(), nullable=True),
        sa.Column('retest_completed_at', sa.DateTime(), nullable=True),
        sa.Column('retest_result', sa.String(length=50), nullable=True),
        sa.Column('retest_notes', sa.Text(), nullable=True),
        sa.Column('retest_evidence', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_eligible', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('eligibility_expires_at', sa.DateTime(), nullable=False),
        sa.Column('eligibility_reason', sa.Text(), nullable=True),
        sa.Column('is_free_retest', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('retest_count', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['finding_id'], ['ptaas_findings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['engagement_id'], ['ptaas_engagements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['requested_by'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ptaas_retest_requests_id', 'ptaas_retest_requests', ['id'])
    op.create_index('ix_ptaas_retest_requests_finding_id', 'ptaas_retest_requests', ['finding_id'])
    op.create_index('ix_ptaas_retest_requests_engagement_id', 'ptaas_retest_requests', ['engagement_id'])
    op.create_index('ix_ptaas_retest_requests_status', 'ptaas_retest_requests', ['status'])
    
    # PTaaS Retest History
    op.create_table(
        'ptaas_retest_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('retest_request_id', sa.Integer(), nullable=False),
        sa.Column('finding_id', sa.Integer(), nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=False),
        sa.Column('activity_by', sa.Integer(), nullable=False),
        sa.Column('activity_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('previous_status', sa.String(length=50), nullable=True),
        sa.Column('new_status', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['retest_request_id'], ['ptaas_retest_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['finding_id'], ['ptaas_findings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['activity_by'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ptaas_retest_history_id', 'ptaas_retest_history', ['id'])
    op.create_index('ix_ptaas_retest_history_retest_request_id', 'ptaas_retest_history', ['retest_request_id'])
    op.create_index('ix_ptaas_retest_history_finding_id', 'ptaas_retest_history', ['finding_id'])


def downgrade():
    op.drop_index('ix_ptaas_retest_history_finding_id', table_name='ptaas_retest_history')
    op.drop_index('ix_ptaas_retest_history_retest_request_id', table_name='ptaas_retest_history')
    op.drop_index('ix_ptaas_retest_history_id', table_name='ptaas_retest_history')
    op.drop_table('ptaas_retest_history')
    
    op.drop_index('ix_ptaas_retest_requests_status', table_name='ptaas_retest_requests')
    op.drop_index('ix_ptaas_retest_requests_engagement_id', table_name='ptaas_retest_requests')
    op.drop_index('ix_ptaas_retest_requests_finding_id', table_name='ptaas_retest_requests')
    op.drop_index('ix_ptaas_retest_requests_id', table_name='ptaas_retest_requests')
    op.drop_table('ptaas_retest_requests')
    
    op.drop_index('ix_ptaas_retest_policies_engagement_id', table_name='ptaas_retest_policies')
    op.drop_index('ix_ptaas_retest_policies_id', table_name='ptaas_retest_policies')
    op.drop_table('ptaas_retest_policies')
