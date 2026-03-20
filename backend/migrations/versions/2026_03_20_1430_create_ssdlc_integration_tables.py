"""create ssdlc integration tables

Revision ID: 2026_03_20_1430
Revises: 2026_03_20_1400
Create Date: 2026-03-20 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_20_1430'
down_revision = '2026_03_20_1400'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create external_integrations table
    op.create_table(
        'external_integrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('config', postgresql.JSON, nullable=False),
        sa.Column('last_sync_at', sa.TIMESTAMP, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_external_integrations_org', 'external_integrations', ['organization_id'])
    op.create_index('idx_external_integrations_type', 'external_integrations', ['type'])

    # Create sync_logs table
    op.create_table(
        'sync_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('integration_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('external_integrations.id'), nullable=False),
        sa.Column('report_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vulnerability_reports.id'), nullable=True),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_sync_logs_integration', 'sync_logs', ['integration_id'])
    op.create_index('idx_sync_logs_status', 'sync_logs', ['status'])

    # Create integration_field_mappings table
    op.create_table(
        'integration_field_mappings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('integration_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('external_integrations.id'), nullable=False),
        sa.Column('source_field', sa.String(100), nullable=False),
        sa.Column('target_field', sa.String(100), nullable=False),
        sa.Column('transformation', sa.String(50), nullable=False, server_default='direct'),
        sa.Column('is_required', sa.Boolean, default=False),
        sa.Column('default_value', sa.Text, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_field_mappings_integration', 'integration_field_mappings', ['integration_id'])

    # Create integration_webhook_events table
    op.create_table(
        'integration_webhook_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('integration_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('external_integrations.id'), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('payload', postgresql.JSON, nullable=False),
        sa.Column('headers', postgresql.JSON, nullable=True),
        sa.Column('signature', sa.String(500), nullable=True),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('processed', sa.Boolean, default=False),
        sa.Column('processed_at', sa.TIMESTAMP, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_webhook_events_integration', 'integration_webhook_events', ['integration_id'])
    op.create_index('idx_webhook_events_processed', 'integration_webhook_events', ['processed'])

    # Create integration_templates table
    op.create_table(
        'integration_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('integration_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('default_config', postgresql.JSON, nullable=False),
        sa.Column('field_mappings', postgresql.JSON, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_templates_type', 'integration_templates', ['integration_type'])


def downgrade() -> None:
    op.drop_table('integration_templates')
    op.drop_table('integration_webhook_events')
    op.drop_table('integration_field_mappings')
    op.drop_table('sync_logs')
    op.drop_table('external_integrations')
