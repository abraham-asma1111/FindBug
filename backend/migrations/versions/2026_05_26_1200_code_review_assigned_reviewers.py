"""Add assigned_reviewer_ids to code review engagements

Revision ID: code_review_rev_20260526
Revises: merge_heads_2026_05_25
"""
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "code_review_rev_20260526"
down_revision: Union[str, None] = "merge_heads_2026_05_25"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    cols = {c["name"] for c in sa.inspect(bind).get_columns("code_review_engagements")}
    if "assigned_reviewer_ids" not in cols:
        op.add_column(
            "code_review_engagements",
            sa.Column("assigned_reviewer_ids", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    cols = {c["name"] for c in sa.inspect(bind).get_columns("code_review_engagements")}
    if "assigned_reviewer_ids" in cols:
        op.drop_column("code_review_engagements", "assigned_reviewer_ids")
