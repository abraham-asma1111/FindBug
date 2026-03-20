"""create bounty payment tables

Revision ID: 2026_03_20_2200
Revises: 2026_03_20_2100
Create Date: 2026-03-20 22:00:00.000000

FREQ-20: RAD-compliant payout system with 30% commission
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_20_2200'
down_revision = '2026_03_20_2100'
branch_labels = None
depends_on = None


def upgrade():
    # Create wallets table
    op.create_table(
        'wallets',
        sa.Column('wallet_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('owner_type', sa.String(50), nullable=False),
        sa.Column('balance', sa.Numeric(15, 2), server_default='0.00', nullable=False),
        sa.Column('reserved_balance', sa.Numeric(15, 2), server_default='0.00', nullable=False),
        sa.Column('available_balance', sa.Numeric(15, 2), server_default='0.00', nullable=False),
        sa.Column('currency', sa.String(3), server_default='ETB', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('wallet_id'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'])
    )
    
    op.create_index('ix_wallets_owner_id', 'wallets', ['owner_id'])
    op.create_index('ix_wallets_owner_type', 'wallets', ['owner_type'])
    
    # Create bounty_payments table
    op.create_table(
        'bounty_payments',
        sa.Column('payment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_id', sa.String(100), nullable=False),
        sa.Column('report_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('researcher_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('researcher_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('commission_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('total_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('status', sa.String(50), server_default='pending', nullable=False),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('payment_gateway', sa.String(50), nullable=True),
        sa.Column('gateway_transaction_id', sa.String(200), nullable=True),
        sa.Column('gateway_response', postgresql.JSON, nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('payout_deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('failure_reason', sa.String(500), nullable=True),
        sa.Column('retry_count', sa.Numeric(3, 0), server_default='0', nullable=False),
        sa.Column('kyc_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('kyc_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('payment_id'),
        sa.ForeignKeyConstraint(['report_id'], ['vulnerability_reports.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['researcher_id'], ['researchers.id']),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
        sa.UniqueConstraint('transaction_id')
    )
    
    op.create_index('ix_bounty_payments_report_id', 'bounty_payments', ['report_id'])
    op.create_index('ix_bounty_payments_researcher_id', 'bounty_payments', ['researcher_id'])
    op.create_index('ix_bounty_payments_organization_id', 'bounty_payments', ['organization_id'])
    op.create_index('ix_bounty_payments_status', 'bounty_payments', ['status'])
    op.create_index('ix_bounty_payments_transaction_id', 'bounty_payments', ['transaction_id'])
    op.create_index('ix_bounty_payments_payout_deadline', 'bounty_payments', ['payout_deadline'])
    
    # Create wallet_transactions table
    op.create_table(
        'wallet_transactions',
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('wallet_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_type', sa.String(50), nullable=False),
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('balance_before', sa.Numeric(15, 2), nullable=False),
        sa.Column('balance_after', sa.Numeric(15, 2), nullable=False),
        sa.Column('reference_type', sa.String(50), nullable=True),
        sa.Column('reference_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('saga_id', sa.String(100), nullable=True),
        sa.Column('compensated', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('compensated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('transaction_id'),
        sa.ForeignKeyConstraint(['wallet_id'], ['wallets.wallet_id'], ondelete='CASCADE')
    )
    
    op.create_index('ix_wallet_transactions_wallet_id', 'wallet_transactions', ['wallet_id'])
    op.create_index('ix_wallet_transactions_saga_id', 'wallet_transactions', ['saga_id'])
    op.create_index('ix_wallet_transactions_reference', 'wallet_transactions', ['reference_type', 'reference_id'])


def downgrade():
    op.drop_index('ix_wallet_transactions_reference', table_name='wallet_transactions')
    op.drop_index('ix_wallet_transactions_saga_id', table_name='wallet_transactions')
    op.drop_index('ix_wallet_transactions_wallet_id', table_name='wallet_transactions')
    op.drop_table('wallet_transactions')
    
    op.drop_index('ix_bounty_payments_payout_deadline', table_name='bounty_payments')
    op.drop_index('ix_bounty_payments_transaction_id', table_name='bounty_payments')
    op.drop_index('ix_bounty_payments_status', table_name='bounty_payments')
    op.drop_index('ix_bounty_payments_organization_id', table_name='bounty_payments')
    op.drop_index('ix_bounty_payments_researcher_id', table_name='bounty_payments')
    op.drop_index('ix_bounty_payments_report_id', table_name='bounty_payments')
    op.drop_table('bounty_payments')
    
    op.drop_index('ix_wallets_owner_type', table_name='wallets')
    op.drop_index('ix_wallets_owner_id', table_name='wallets')
    op.drop_table('wallets')
