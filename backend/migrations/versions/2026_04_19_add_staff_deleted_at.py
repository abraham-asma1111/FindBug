"""add staff deleted_at column

Revision ID: 2026_04_19_staff_deleted
Revises: 2026_03_29_1400_create_vrt_tables
Create Date: 2026-04-19 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_04_19_staff_deleted'
down_revision = '2026_04_09_add_researcher_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Add deleted_at column to staff table if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='staff' AND column_name='deleted_at'
            ) THEN
                ALTER TABLE staff ADD COLUMN deleted_at TIMESTAMP;
            END IF;
        END $$;
    """)


def downgrade():
    # Remove deleted_at column from staff table
    op.drop_column('staff', 'deleted_at')
