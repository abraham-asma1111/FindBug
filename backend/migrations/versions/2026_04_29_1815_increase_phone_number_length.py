"""increase phone_number length for email

Revision ID: 2026_04_29_1815
Revises: 
Create Date: 2026-04-29 18:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2026_04_29_1815'
down_revision = None  # Update this to your latest migration
branch_labels = None
depends_on = None


def upgrade():
    # Increase phone_number column length from VARCHAR(20) to VARCHAR(255)
    # to accommodate email addresses
    op.alter_column('kyc_verifications', 'phone_number',
                    existing_type=sa.VARCHAR(length=20),
                    type_=sa.VARCHAR(length=255),
                    existing_nullable=True)


def downgrade():
    # Revert back to VARCHAR(20)
    op.alter_column('kyc_verifications', 'phone_number',
                    existing_type=sa.VARCHAR(length=255),
                    type_=sa.VARCHAR(length=20),
                    existing_nullable=True)
