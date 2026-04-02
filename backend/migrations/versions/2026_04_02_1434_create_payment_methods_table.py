"""create payment_methods table

Revision ID: 8524f75065ff
Revises: 2026_03_31_0200_create_pending_registrations
Create Date: 2026-04-02 14:34:44.224404

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8524f75065ff'
down_revision: Union[str, Sequence[str], None] = 'a5d64b176487'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create payment_methods table
    op.create_table('payment_methods',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('method_type', sa.String(length=50), nullable=False),
        sa.Column('account_number', sa.String(length=100), nullable=True),
        sa.Column('account_name', sa.String(length=200), nullable=True),
        sa.Column('bank_name', sa.String(length=100), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_payment_methods_user_id', 'payment_methods', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_payment_methods_user_id', table_name='payment_methods')
    op.drop_table('payment_methods')
