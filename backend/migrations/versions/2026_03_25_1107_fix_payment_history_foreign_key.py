"""fix_payment_history_foreign_key

Revision ID: 6e1b9728908e
Revises: 2026_03_24_0900
Create Date: 2026-03-25 11:07:09.920743

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e1b9728908e'
down_revision: Union[str, Sequence[str], None] = '2026_03_24_0900'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Fix PaymentHistory foreign key to reference bounty_payments.payment_id."""
    # Drop the old foreign key constraint
    op.drop_constraint('payment_history_payment_id_fkey', 'payment_history', type_='foreignkey')
    
    # Create the new foreign key constraint pointing to payment_id
    op.create_foreign_key(
        'payment_history_payment_id_fkey',
        'payment_history', 'bounty_payments',
        ['payment_id'], ['payment_id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema - Revert to old foreign key reference."""
    # Drop the new foreign key constraint
    op.drop_constraint('payment_history_payment_id_fkey', 'payment_history', type_='foreignkey')
    
    # Restore the old foreign key constraint (incorrect one)
    op.create_foreign_key(
        'payment_history_payment_id_fkey',
        'payment_history', 'bounty_payments',
        ['payment_id'], ['id'],
        ondelete='CASCADE'
    )
