"""create ptaas dashboard tables

Revision ID: 2026_03_20_1200
Revises: 2026_03_20_1143
Create Date: 2026-03-20 12:00:00.000000

FREQ-34: PTaaS Progress Dashboard Tables
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_20_1200'
down_revision = '2026_03_20_1143'
branch_labels = None
depends_on = None


def upgrade():
    # PTaaS Testing Phases
    op.create_table(
        'ptaas_testing_phases',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('phase_name', sa.String(length=100), nullable=False),
        sa.Column('phase_order', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='NOT_STARTED'),
        sa.Column('progress_percentage', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('estimated_completion', sa.DateTime(), nullable=True),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['engagement_id'], ['ptaas_engagements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ptaas_testing_phases_id', 'ptaas_testing_phases', ['id'])
    op.create_index('ix_ptaas_testing_phases_engagement_id', 'ptaas_testing_phases', ['engagement_id'])
    
    # PTaaS Checklist Items
    op.create_table(
        'ptaas_checklist_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('phase_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_required', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('completed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('evidence_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['phase_id'], ['ptaas_testing_phases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['engagement_id'], ['ptaas_engagements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['completed_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ptaas_checklist_items_id', 'ptaas_checklist_items', ['id'])
    op.create_index('ix_ptaas_checklist_items_phase_id', 'ptaas_checklist_items', ['phase_id'])
    op.create_index('ix_ptaas_checklist_items_engagement_id', 'ptaas_checklist_items', ['engagement_id'])
    
    # PTaaS Collaboration Updates
    op.create_table(
        'ptaas_collaboration_updates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('update_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('mentioned_users', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_pinned', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('priority', sa.String(length=20), nullable=True, server_default='NORMAL'),
        sa.Column('related_finding_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('related_phase_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('attachments', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['engagement_id'], ['ptaas_engagements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['related_finding_id'], ['ptaas_findings.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['related_phase_id'], ['ptaas_testing_phases.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ptaas_collaboration_updates_id', 'ptaas_collaboration_updates', ['id'])
    op.create_index('ix_ptaas_collaboration_updates_engagement_id', 'ptaas_collaboration_updates', ['engagement_id'])
    
    # PTaaS Milestones
    op.create_table(
        'ptaas_milestones',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('milestone_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_date', sa.DateTime(), nullable=False),
        sa.Column('completed_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='PENDING'),
        sa.Column('deliverables', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['engagement_id'], ['ptaas_engagements.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ptaas_milestones_id', 'ptaas_milestones', ['id'])
    op.create_index('ix_ptaas_milestones_engagement_id', 'ptaas_milestones', ['engagement_id'])


def downgrade():
    op.drop_index('ix_ptaas_milestones_engagement_id', table_name='ptaas_milestones')
    op.drop_index('ix_ptaas_milestones_id', table_name='ptaas_milestones')
    op.drop_table('ptaas_milestones')
    
    op.drop_index('ix_ptaas_collaboration_updates_engagement_id', table_name='ptaas_collaboration_updates')
    op.drop_index('ix_ptaas_collaboration_updates_id', table_name='ptaas_collaboration_updates')
    op.drop_table('ptaas_collaboration_updates')
    
    op.drop_index('ix_ptaas_checklist_items_engagement_id', table_name='ptaas_checklist_items')
    op.drop_index('ix_ptaas_checklist_items_phase_id', table_name='ptaas_checklist_items')
    op.drop_index('ix_ptaas_checklist_items_id', table_name='ptaas_checklist_items')
    op.drop_table('ptaas_checklist_items')
    
    op.drop_index('ix_ptaas_testing_phases_engagement_id', table_name='ptaas_testing_phases')
    op.drop_index('ix_ptaas_testing_phases_id', table_name='ptaas_testing_phases')
    op.drop_table('ptaas_testing_phases')
