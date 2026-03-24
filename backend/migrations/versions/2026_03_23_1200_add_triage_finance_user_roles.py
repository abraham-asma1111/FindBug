"""add triage_specialist and finance_officer to userrole enum

Revision ID: 2026_03_23_1200
Revises: df02a440f442
Create Date: 2026-03-23 12:00:00.000000

RAD FREQ-01: distinct Triage Specialist and Finance Officer roles.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2026_03_23_1200"
down_revision: Union[str, Sequence[str], None] = "df02a440f442"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL: extend native enum (idempotent for re-runs)
    op.execute(
        sa.text(
            """
            DO $$ BEGIN
                ALTER TYPE userrole ADD VALUE 'triage_specialist';
            EXCEPTION
                WHEN duplicate_object THEN NULL;
            END $$;
            """
        )
    )
    op.execute(
        sa.text(
            """
            DO $$ BEGIN
                ALTER TYPE userrole ADD VALUE 'finance_officer';
            EXCEPTION
                WHEN duplicate_object THEN NULL;
            END $$;
            """
        )
    )


def downgrade() -> None:
    # PostgreSQL cannot remove enum values safely; no-op.
    pass
