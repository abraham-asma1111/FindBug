"""Add missing researcher fields

Revision ID: 2026_04_09_add_researcher_fields
Revises: 
Create Date: 2026-04-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2026_04_09_add_researcher_fields'
down_revision = None  # Set this to the latest migration
branch_labels = None
depends_on = None


def upgrade():
    # Add missing fields to researchers table if they don't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='researchers' AND column_name='total_reports'
            ) THEN
                ALTER TABLE researchers ADD COLUMN total_reports INTEGER DEFAULT 0 NOT NULL;
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='researchers' AND column_name='verified_reports'
            ) THEN
                ALTER TABLE researchers ADD COLUMN verified_reports INTEGER DEFAULT 0 NOT NULL;
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='researchers' AND column_name='is_active'
            ) THEN
                ALTER TABLE researchers ADD COLUMN is_active BOOLEAN DEFAULT true NOT NULL;
            END IF;
        END $$;
    """)


def downgrade():
    # Remove the added fields
    op.drop_column('researchers', 'is_active')
    op.drop_column('researchers', 'verified_reports')
    op.drop_column('researchers', 'total_reports')
