"""create audit logs table

Revision ID: 2026_03_19_1600
Revises: 2026_03_19_1500
Create Date: 2026-03-19 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_19_1600'
down_revision = '2026_03_19_1500'
branch_labels = None
depends_on = None


def upgrade():
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('action_type', sa.String(100), nullable=False),
        sa.Column('action_category', sa.String(50), nullable=False),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('actor_role', sa.String(50), nullable=True),
        sa.Column('actor_email', sa.String(255), nullable=True),
        sa.Column('target_type', sa.String(50), nullable=False),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('severity', sa.String(20), nullable=False, server_default='info'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create indexes
    op.create_index('ix_audit_logs_action_type', 'audit_logs', ['action_type'])
    op.create_index('ix_audit_logs_action_category', 'audit_logs', ['action_category'])
    op.create_index('ix_audit_logs_actor_id', 'audit_logs', ['actor_id'])
    op.create_index('ix_audit_logs_target_type', 'audit_logs', ['target_type'])
    op.create_index('ix_audit_logs_target_id', 'audit_logs', ['target_id'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])
    op.create_index('ix_audit_logs_severity', 'audit_logs', ['severity'])


def downgrade():
    op.drop_table('audit_logs')
