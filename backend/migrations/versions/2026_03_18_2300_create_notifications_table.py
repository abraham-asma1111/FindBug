"""create notifications table

Revision ID: 2026_03_18_2300
Revises: 2026_03_18_2200
Create Date: 2026-03-18 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_18_2300'
down_revision = '2026_03_18_2200'
branch_labels = None
depends_on = None


def upgrade():
    # Create notifications table (enums will be created automatically)
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('notification_type', postgresql.ENUM(
            'report_submitted', 'report_status_changed', 'report_triaged', 
            'report_validated', 'report_invalid', 'report_duplicate', 
            'report_resolved', 'report_acknowledged',
            'bounty_approved', 'bounty_rejected', 'bounty_paid',
            'reputation_updated', 'rank_changed',
            'new_message', 'new_comment',
            'program_published', 'program_updated', 'program_closed',
            'account_verified', 'password_changed', 'mfa_enabled',
            name='notificationtype',
            create_type=True
        ), nullable=False),
        sa.Column('priority', postgresql.ENUM(
            'low', 'medium', 'high', 'urgent',
            name='notificationpriority',
            create_type=True
        ), nullable=False, server_default='medium'),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('related_entity_type', sa.String(50), nullable=True),
        sa.Column('related_entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action_url', sa.String(500), nullable=True),
        sa.Column('action_text', sa.String(100), nullable=True),
        sa.Column('is_read', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('read_at', sa.DateTime, nullable=True),
        sa.Column('email_sent', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('email_sent_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), index=True),
        sa.Column('expires_at', sa.DateTime, nullable=True)
    )
    
    # Create indexes for better query performance
    op.create_index('ix_notifications_user_id_is_read', 'notifications', ['user_id', 'is_read'])
    op.create_index('ix_notifications_user_id_created_at', 'notifications', ['user_id', 'created_at'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_notifications_user_id_created_at', table_name='notifications')
    op.drop_index('ix_notifications_user_id_is_read', table_name='notifications')
    
    # Drop table
    op.drop_table('notifications')
    
    # Drop enums
    sa.Enum(name='notificationpriority').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='notificationtype').drop(op.get_bind(), checkfirst=True)
