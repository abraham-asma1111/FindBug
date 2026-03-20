"""add matching configuration and assignments

Revision ID: 2026_03_20_1143
Revises: 2026_03_20_1130
Create Date: 2026-03-20 11:43:00.000000

Implements FREQ-33: Matching configuration and approval workflow
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_20_1143'
down_revision = '2026_03_20_1130'
branch_labels = None
depends_on = None


def upgrade():
    # Create matching_configurations table
    op.create_table(
        'matching_configurations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('skill_weight', sa.Numeric(precision=3, scale=2), nullable=False, server_default='0.30'),
        sa.Column('reputation_weight', sa.Numeric(precision=3, scale=2), nullable=False, server_default='0.20'),
        sa.Column('performance_weight', sa.Numeric(precision=3, scale=2), nullable=False, server_default='0.20'),
        sa.Column('expertise_weight', sa.Numeric(precision=3, scale=2), nullable=False, server_default='0.20'),
        sa.Column('availability_weight', sa.Numeric(precision=3, scale=2), nullable=False, server_default='0.10'),
        sa.Column('min_overall_score', sa.Numeric(precision=5, scale=2), nullable=False, server_default='50.00'),
        sa.Column('min_reputation', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('min_experience_years', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('require_approval', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('auto_approve_threshold', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('approval_timeout_hours', sa.Integer(), nullable=False, server_default='48'),
        sa.Column('preferred_timezones', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('excluded_researchers', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('preferred_researchers', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id')
    )
    op.create_index(op.f('ix_matching_configurations_organization_id'), 'matching_configurations', ['organization_id'], unique=False)

    # Create researcher_assignments table
    op.create_table(
        'researcher_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', sa.Integer(), nullable=False),
        sa.Column('engagement_type', sa.String(length=50), nullable=False),
        sa.Column('researcher_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_score', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('match_details', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('proposed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('proposed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['proposed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['researcher_id'], ['researchers.id'], ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_researcher_assignments_engagement_id'), 'researcher_assignments', ['engagement_id'], unique=False)
    op.create_index(op.f('ix_researcher_assignments_organization_id'), 'researcher_assignments', ['organization_id'], unique=False)
    op.create_index(op.f('ix_researcher_assignments_researcher_id'), 'researcher_assignments', ['researcher_id'], unique=False)
    op.create_index(op.f('ix_researcher_assignments_status'), 'researcher_assignments', ['status'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_researcher_assignments_status'), table_name='researcher_assignments')
    op.drop_index(op.f('ix_researcher_assignments_researcher_id'), table_name='researcher_assignments')
    op.drop_index(op.f('ix_researcher_assignments_organization_id'), table_name='researcher_assignments')
    op.drop_index(op.f('ix_researcher_assignments_engagement_id'), table_name='researcher_assignments')
    op.drop_table('researcher_assignments')
    
    op.drop_index(op.f('ix_matching_configurations_organization_id'), table_name='matching_configurations')
    op.drop_table('matching_configurations')
