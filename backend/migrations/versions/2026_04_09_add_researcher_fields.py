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
    # Add missing fields to researchers table
    op.add_column('researchers', sa.Column('total_reports', sa.Integer(), server_default='0', nullable=False))
    op.add_column('researchers', sa.Column('verified_reports', sa.Integer(), server_default='0', nullable=False))
    op.add_column('researchers', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False))


def downgrade():
    # Remove the added fields
    op.drop_column('researchers', 'is_active')
    op.drop_column('researchers', 'verified_reports')
    op.drop_column('researchers', 'total_reports')
