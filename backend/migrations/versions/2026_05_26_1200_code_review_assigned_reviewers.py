"""Add assigned_reviewer_ids to code review engagements

Revision ID: code_review_assigned_reviewers_2026_05_26
Revises: merge_heads_2026_05_25
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "code_review_assigned_reviewers_2026_05_26"
down_revision: Union[str, None] = "merge_heads_2026_05_25"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "code_review_engagements",
        sa.Column("assigned_reviewer_ids", postgresql.JSON(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("code_review_engagements", "assigned_reviewer_ids")
