"""PTaaS bounty fields and bounty_payments ptaas_finding_id

Revision ID: ptaas_bounty_payment_2026_05_26
Revises: code_review_rev_20260526
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "ptaas_bounty_payment_2026_05_26"
down_revision: Union[str, None] = "code_review_rev_20260526"
branch_labels = None
depends_on = None


def _columns(table: str) -> set:
    bind = op.get_bind()
    return {c["name"] for c in sa.inspect(bind).get_columns(table)}


def _indexes(table: str) -> set:
    bind = op.get_bind()
    return {i["name"] for i in sa.inspect(bind).get_indexes(table)}


def upgrade() -> None:
    ptaas_cols = _columns("ptaas_findings")

    if "bounty_amount" not in ptaas_cols:
        op.add_column("ptaas_findings", sa.Column("bounty_amount", sa.Numeric(15, 2), nullable=True))
    if "bounty_status" not in ptaas_cols:
        op.add_column(
            "ptaas_findings",
            sa.Column("bounty_status", sa.String(50), nullable=True, server_default="pending"),
        )
    if "bounty_approved_by" not in ptaas_cols:
        op.add_column(
            "ptaas_findings",
            sa.Column(
                "bounty_approved_by",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("users.id"),
                nullable=True,
            ),
        )
    if "bounty_approved_at" not in ptaas_cols:
        op.add_column(
            "ptaas_findings",
            sa.Column("bounty_approved_at", sa.DateTime(timezone=True), nullable=True),
        )

    payment_cols = _columns("bounty_payments")
    if "report_id" in payment_cols:
        op.alter_column("bounty_payments", "report_id", existing_type=postgresql.UUID(), nullable=True)

    if "ptaas_finding_id" not in payment_cols:
        op.add_column(
            "bounty_payments",
            sa.Column(
                "ptaas_finding_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("ptaas_findings.id", ondelete="CASCADE"),
                nullable=True,
            ),
        )
    if "payment_source" not in payment_cols:
        op.add_column(
            "bounty_payments",
            sa.Column("payment_source", sa.String(50), nullable=False, server_default="bug_bounty"),
        )

    if "ix_bounty_payments_ptaas_finding_id" not in _indexes("bounty_payments"):
        op.create_index(
            "ix_bounty_payments_ptaas_finding_id",
            "bounty_payments",
            ["ptaas_finding_id"],
        )


def downgrade() -> None:
    if "ix_bounty_payments_ptaas_finding_id" in _indexes("bounty_payments"):
        op.drop_index("ix_bounty_payments_ptaas_finding_id", table_name="bounty_payments")

    payment_cols = _columns("bounty_payments")
    if "payment_source" in payment_cols:
        op.drop_column("bounty_payments", "payment_source")
    if "ptaas_finding_id" in payment_cols:
        op.drop_column("bounty_payments", "ptaas_finding_id")
    op.alter_column("bounty_payments", "report_id", existing_type=postgresql.UUID(), nullable=False)

    ptaas_cols = _columns("ptaas_findings")
    for col in ("bounty_approved_at", "bounty_approved_by", "bounty_status", "bounty_amount"):
        if col in ptaas_cols:
            op.drop_column("ptaas_findings", col)
