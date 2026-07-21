"""Add organization branding fields

Revision ID: add_org_branding_2026_05_06
Revises: 
Create Date: 2026-05-06 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_org_branding_2026_05_06'
down_revision = None  # Update this to the latest migration
branch_labels = None
depends_on = None


def upgrade():
    """Add branding configuration columns to organizations table."""
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if not insp.has_table("organizations"):
        return
    existing = {c["name"] for c in insp.get_columns("organizations")}
    if "logo_url" not in existing:
        op.add_column("organizations", sa.Column("logo_url", sa.String(length=500), nullable=True))
    if "cover_image_url" not in existing:
        op.add_column("organizations", sa.Column("cover_image_url", sa.String(length=500), nullable=True))
    if "brand_color" not in existing:
        op.add_column("organizations", sa.Column("brand_color", sa.String(length=7), nullable=True))
    if "theme_settings" not in existing:
        op.add_column("organizations", sa.Column("theme_settings", sa.Text(), nullable=True))


def downgrade():
    """Remove branding configuration columns from organizations table."""
    op.drop_column('organizations', 'theme_settings')
    op.drop_column('organizations', 'brand_color')
    op.drop_column('organizations', 'cover_image_url')
    op.drop_column('organizations', 'logo_url')
