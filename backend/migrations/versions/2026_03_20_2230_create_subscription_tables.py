"""create subscription tables

Revision ID: 2026_03_20_2230
Revises: 2026_03_20_2200
Create Date: 2026-03-20 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_20_2230'
down_revision = '2026_03_20_2200'
branch_labels = None
depends_on = None


def upgrade():
    # Create subscription tier pricing table
    op.create_table(
        'subscription_tier_pricing',
        sa.Column('pricing_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tier', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('quarterly_price', sa.Numeric(15, 2), nullable=False),
        sa.Column('annual_price', sa.Numeric(15, 2), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False, server_default='ETB'),
        sa.Column('max_programs', sa.Numeric(5, 0), nullable=True),
        sa.Column('max_researchers', sa.Numeric(6, 0), nullable=True),
        sa.Column('max_reports_per_month', sa.Numeric(6, 0), nullable=True),
        sa.Column('ptaas_enabled', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('code_review_enabled', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('ai_red_teaming_enabled', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('live_events_enabled', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('ssdlc_integration_enabled', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('support_level', sa.String(50), nullable=False, server_default='email'),
        sa.Column('features', postgresql.JSON, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    op.create_index('ix_subscription_tier_pricing_tier', 'subscription_tier_pricing', ['tier'])
    
    # Create organization subscriptions table
    op.create_table(
        'organization_subscriptions',
        sa.Column('subscription_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tier', sa.String(50), nullable=False, server_default='basic'),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('subscription_fee', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='ETB'),
        sa.Column('billing_cycle_months', sa.Numeric(3, 0), nullable=False, server_default='4'),
        sa.Column('payments_per_year', sa.Numeric(2, 0), nullable=False, server_default='3'),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('next_billing_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancellation_reason', sa.String(500), nullable=True),
        sa.Column('trial_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_trial', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('features', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    op.create_index('ix_org_subscriptions_organization_id', 'organization_subscriptions', ['organization_id'])
    op.create_index('ix_org_subscriptions_status', 'organization_subscriptions', ['status'])
    op.create_index('ix_org_subscriptions_next_billing_date', 'organization_subscriptions', ['next_billing_date'])
    
    # Create subscription payments table
    op.create_table(
        'subscription_payments',
        sa.Column('payment_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('subscription_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organization_subscriptions.subscription_id', ondelete='CASCADE'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='ETB'),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('payment_gateway', sa.String(50), nullable=True),
        sa.Column('gateway_transaction_id', sa.String(200), nullable=True),
        sa.Column('gateway_response', postgresql.JSON, nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failure_reason', sa.String(500), nullable=True),
        sa.Column('retry_count', sa.Numeric(3, 0), nullable=False, server_default='0'),
        sa.Column('invoice_number', sa.String(100), nullable=True),
        sa.Column('invoice_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    op.create_index('ix_subscription_payments_subscription_id', 'subscription_payments', ['subscription_id'])
    op.create_index('ix_subscription_payments_organization_id', 'subscription_payments', ['organization_id'])
    op.create_index('ix_subscription_payments_status', 'subscription_payments', ['status'])
    op.create_index('ix_subscription_payments_due_date', 'subscription_payments', ['due_date'])


def downgrade():
    op.drop_table('subscription_payments')
    op.drop_table('organization_subscriptions')
    op.drop_table('subscription_tier_pricing')
