"""Add simulation review, hint, and gamification columns

Revision ID: 2026_05_25_1200
Revises: 2026_05_02_1700
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "2026_05_25_1200"
down_revision = "2026_05_02_1700"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "simulation_reports",
        sa.Column("score", sa.Integer(), server_default="0"),
    )
    op.add_column("simulation_reports", sa.Column("remediation", sa.Text()))

    op.add_column(
        "simulation_leaderboard",
        sa.Column("rank_title", sa.String(64), server_default="Newbie"),
    )
    op.add_column(
        "simulation_leaderboard",
        sa.Column("current_streak", sa.Integer(), server_default="0"),
    )

    op.add_column(
        "simulation_progress",
        sa.Column("hints_unlocked", postgresql.JSON(), server_default="[]"),
    )


def downgrade():
    op.drop_column("simulation_progress", "hints_unlocked")
    op.drop_column("simulation_leaderboard", "current_streak")
    op.drop_column("simulation_leaderboard", "rank_title")
    op.drop_column("simulation_reports", "remediation")
    op.drop_column("simulation_reports", "score")
