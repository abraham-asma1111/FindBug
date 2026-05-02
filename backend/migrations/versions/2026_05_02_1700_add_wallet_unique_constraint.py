"""Add unique constraint to wallets table

Revision ID: 2026_05_02_1700
Revises: 2026_04_20_1200
Create Date: 2026-05-02 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2026_05_02_1700'
down_revision = '2026_04_29_1900'
branch_labels = None
depends_on = None


def upgrade():
    """Add unique constraint to prevent duplicate wallets."""
    
    # First, clean up any existing duplicates
    # This SQL will keep only the wallet with the highest balance for each owner_id+owner_type combination
    op.execute("""
        -- Delete duplicate wallets, keeping only the one with highest balance
        DELETE FROM wallets
        WHERE wallet_id NOT IN (
            SELECT DISTINCT ON (owner_id, owner_type) wallet_id
            FROM wallets
            ORDER BY owner_id, owner_type, balance DESC, created_at ASC
        );
    """)
    
    # Now add the unique constraint
    op.create_unique_constraint(
        'uq_wallets_owner_id_owner_type',
        'wallets',
        ['owner_id', 'owner_type']
    )


def downgrade():
    """Remove unique constraint."""
    op.drop_constraint('uq_wallets_owner_id_owner_type', 'wallets', type_='unique')
