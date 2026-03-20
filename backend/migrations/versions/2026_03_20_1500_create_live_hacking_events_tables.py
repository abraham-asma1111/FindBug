"""create live hacking events tables

Revision ID: 2026_03_20_1500
Revises: 2026_03_20_1430
Create Date: 2026-03-20 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_20_1500'
down_revision = '2026_03_20_1430'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create live_hacking_events table
    op.create_table(
        'live_hacking_events',
        sa.Column('event_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('start_time', sa.TIMESTAMP, nullable=False),
        sa.Column('end_time', sa.TIMESTAMP, nullable=False),
        sa.Column('max_participants', sa.Integer, nullable=True),
        sa.Column('prize_pool', sa.DECIMAL(15, 2), nullable=True),
        sa.Column('scope_description', sa.Text, nullable=True),
        sa.Column('target_assets', sa.Text, nullable=True),
        sa.Column('reward_policy', sa.Text, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_live_events_org', 'live_hacking_events', ['organization_id'])
    op.create_index('idx_live_events_status', 'live_hacking_events', ['status'])
    op.create_index('idx_live_events_time', 'live_hacking_events', ['start_time', 'end_time'])

    # Create event_participations table
    op.create_table(
        'event_participations',
        sa.Column('participation_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('live_hacking_events.event_id'), nullable=False),
        sa.Column('researcher_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('researchers.id'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='invited'),
        sa.Column('score', sa.Integer, default=0),
        sa.Column('rank', sa.Integer, nullable=True),
        sa.Column('submissions_count', sa.Integer, default=0),
        sa.Column('valid_submissions_count', sa.Integer, default=0),
        sa.Column('prize_amount', sa.DECIMAL(15, 2), nullable=True),
        sa.Column('joined_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('completed_at', sa.TIMESTAMP, nullable=True)
    )
    op.create_index('idx_participations_event', 'event_participations', ['event_id'])
    op.create_index('idx_participations_researcher', 'event_participations', ['researcher_id'])
    op.create_index('idx_participations_rank', 'event_participations', ['event_id', 'rank'])

    # Create event_invitations table
    op.create_table(
        'event_invitations',
        sa.Column('invitation_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('live_hacking_events.event_id'), nullable=False),
        sa.Column('researcher_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('researchers.id'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('invited_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('responded_at', sa.TIMESTAMP, nullable=True),
        sa.Column('expires_at', sa.TIMESTAMP, nullable=True)
    )
    op.create_index('idx_invitations_event', 'event_invitations', ['event_id'])
    op.create_index('idx_invitations_researcher', 'event_invitations', ['researcher_id'])
    op.create_index('idx_invitations_status', 'event_invitations', ['status'])

    # Create event_metrics table
    op.create_table(
        'event_metrics',
        sa.Column('metrics_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('live_hacking_events.event_id'), unique=True, nullable=False),
        sa.Column('total_invited', sa.Integer, default=0),
        sa.Column('total_accepted', sa.Integer, default=0),
        sa.Column('total_active', sa.Integer, default=0),
        sa.Column('total_submissions', sa.Integer, default=0),
        sa.Column('valid_submissions', sa.Integer, default=0),
        sa.Column('invalid_submissions', sa.Integer, default=0),
        sa.Column('duplicate_submissions', sa.Integer, default=0),
        sa.Column('critical_bugs', sa.Integer, default=0),
        sa.Column('high_bugs', sa.Integer, default=0),
        sa.Column('medium_bugs', sa.Integer, default=0),
        sa.Column('low_bugs', sa.Integer, default=0),
        sa.Column('info_bugs', sa.Integer, default=0),
        sa.Column('total_rewards_paid', sa.DECIMAL(15, 2), default=0),
        sa.Column('average_reward', sa.DECIMAL(15, 2), default=0),
        sa.Column('participation_rate', sa.DECIMAL(5, 2), default=0),
        sa.Column('average_time_to_first_bug', sa.Integer, nullable=True),
        sa.Column('last_updated', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_metrics_event', 'event_metrics', ['event_id'])

    # Add event_id to vulnerability_reports for linking submissions
    op.add_column('vulnerability_reports', sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_reports_event',
        'vulnerability_reports',
        'live_hacking_events',
        ['event_id'],
        ['event_id']
    )
    op.create_index('idx_reports_event', 'vulnerability_reports', ['event_id'])


def downgrade() -> None:
    op.drop_index('idx_reports_event', 'vulnerability_reports')
    op.drop_constraint('fk_reports_event', 'vulnerability_reports', type_='foreignkey')
    op.drop_column('vulnerability_reports', 'event_id')
    
    op.drop_table('event_metrics')
    op.drop_table('event_invitations')
    op.drop_table('event_participations')
    op.drop_table('live_hacking_events')
