"""Merge divergent Alembic heads into a single lineage

Revision ID: merge_heads_2026_05_25
Revises: 20260420_1200, b6e1ef4870ce, 2026_04_20_1200_create_triage_templates,
         2026_04_29_1815, add_org_branding_2026_05_06, 2026_05_25_1200
"""
from typing import Sequence, Union

from alembic import op

revision: str = "merge_heads_2026_05_25"
down_revision: Union[str, Sequence[str], None] = (
    "20260420_1200",
    "b6e1ef4870ce",
    "tri_tpl_20260420",
    "2026_04_29_1815",
    "add_org_branding_2026_05_06",
    "2026_05_25_1200",
)
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
