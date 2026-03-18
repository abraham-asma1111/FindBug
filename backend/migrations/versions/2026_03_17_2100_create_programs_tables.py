"""create programs tables

Revision ID: 2026_03_17_2100
Revises: 2026_03_16_2045
Create Date: 2026-03-17 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '2026_03_17_2100'
down_revision = '3f4e5a6b7c8d'
branch_labels = None
depends_on = None


def upgrade():
    # Create bounty_programs table
    op.create_table(
        'bounty_programs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('type', sa.String(20), nullable=False),  # bounty, vdp
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),  # draft, private, public, paused, closed
        sa.Column('visibility', sa.String(20), nullable=False, server_default='private'),  # private, public
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('budget', sa.Numeric(15, 2), nullable=True),
        sa.Column('policy', sa.Text, nullable=True),
        sa.Column('rules_of_engagement', sa.Text, nullable=True),
        sa.Column('safe_harbor', sa.Text, nullable=True),
        sa.Column('response_sla_hours', sa.Integer, nullable=True, server_default='72'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True)
    )
    
    # Create program_scopes table
    op.create_table(
        'program_scopes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('bounty_programs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('asset_type', sa.String(50), nullable=False),  # domain, api, mobile_app, web_app, other
        sa.Column('asset_identifier', sa.String(500), nullable=False),  # example.com, api.example.com, etc.
        sa.Column('is_in_scope', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('max_severity', sa.String(20), nullable=True),  # critical, high, medium, low
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create reward_tiers table
    op.create_table(
        'reward_tiers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('bounty_programs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),  # critical, high, medium, low
        sa.Column('min_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('max_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create program_invitations table
    op.create_table(
        'program_invitations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('bounty_programs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('researcher_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('researchers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),  # pending, accepted, declined, expired
        sa.Column('invited_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('message', sa.Text, nullable=True),
        sa.Column('invited_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Create indexes
    op.create_index('idx_programs_organization', 'bounty_programs', ['organization_id'])
    op.create_index('idx_programs_status', 'bounty_programs', ['status'])
    op.create_index('idx_programs_visibility', 'bounty_programs', ['visibility'])
    op.create_index('idx_scopes_program', 'program_scopes', ['program_id'])
    op.create_index('idx_rewards_program', 'reward_tiers', ['program_id'])
    op.create_index('idx_invitations_program', 'program_invitations', ['program_id'])
    op.create_index('idx_invitations_researcher', 'program_invitations', ['researcher_id'])
    op.create_index('idx_invitations_status', 'program_invitations', ['status'])


def downgrade():
    op.drop_table('program_invitations')
    op.drop_table('reward_tiers')
    op.drop_table('program_scopes')
    op.drop_table('bounty_programs')
