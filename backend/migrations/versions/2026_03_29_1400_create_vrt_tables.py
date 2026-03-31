"""create vrt tables

Revision ID: 2026_03_29_1400
Revises: 2026_03_24_0900
Create Date: 2026-03-29 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2026_03_29_1400'
down_revision = '2026_03_24_0900'
branch_labels = None
depends_on = None


def upgrade():
    # Create vrt_categories table
    op.create_table(
        'vrt_categories',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('icon', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Create vrt_entries table
    op.create_table(
        'vrt_entries',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('category_id', sa.String(36), sa.ForeignKey('vrt_categories.id'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(200), nullable=False),
        sa.Column('subcategory', sa.String(200), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('cvss_min', sa.Float, default=0.0, nullable=False),
        sa.Column('cvss_max', sa.Float, default=10.0, nullable=False),
        sa.Column('priority', sa.String(20), default='medium', nullable=False),
        sa.Column('remediation', sa.Text, nullable=True),
        sa.Column('references', sa.Text, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Create indexes
    op.create_index('ix_vrt_categories_slug', 'vrt_categories', ['slug'])
    op.create_index('ix_vrt_entries_slug', 'vrt_entries', ['slug'])
    op.create_index('ix_vrt_entries_category_id', 'vrt_entries', ['category_id'])


def downgrade():
    op.drop_index('ix_vrt_entries_category_id', 'vrt_entries')
    op.drop_index('ix_vrt_entries_slug', 'vrt_entries')
    op.drop_index('ix_vrt_categories_slug', 'vrt_categories')
    op.drop_table('vrt_entries')
    op.drop_table('vrt_categories')
