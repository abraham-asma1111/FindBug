"""add missing ERD tables

Fills all tables defined in database-schema-erd-extended.puml that were
not yet present in the database:

  Group 1 — Staff role profiles:
    triage_specialists, administrators, financial_officers

  Group 2 — KYC & auth tracking:
    kyc_verifications, security_events, login_history

  Group 3 — Triage workflow:
    triage_queue, triage_assignments, validation_results, duplicate_detections

  Group 4 — Payment completeness:
    payout_requests, transactions, payment_gateways, payment_history

  Group 5 — Ops / platform tables:
    webhook_endpoints, webhook_logs, email_templates, data_exports, compliance_reports

Revision ID: 2026_03_24_0900
Revises: 2026_03_23_1200
Create Date: 2026-03-24 09:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "2026_03_24_0900"
down_revision = "2026_03_23_1200"
branch_labels = None
depends_on = None


def upgrade() -> None:

    # ------------------------------------------------------------------ #
    # GROUP 1 — Staff role profiles                                        #
    # ------------------------------------------------------------------ #

    op.create_table(
        "triage_specialists",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("specialization", postgresql.JSONB, nullable=True),
        sa.Column("years_experience", sa.Integer, nullable=False, server_default="0"),
        sa.Column("accuracy_rate", sa.Numeric(5, 2), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
    )
    op.create_index("ix_triage_specialists_user_id", "triage_specialists", ["user_id"])

    op.create_table(
        "administrators",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("admin_level", sa.String(20), nullable=False, server_default="admin"),
        sa.Column("permissions", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
    )
    op.create_index("ix_administrators_user_id", "administrators", ["user_id"])

    op.create_table(
        "financial_officers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("approval_limit", sa.Numeric(15, 2), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
    )
    op.create_index("ix_financial_officers_user_id", "financial_officers", ["user_id"])

    # ------------------------------------------------------------------ #
    # GROUP 2 — KYC & auth tracking                                        #
    # ------------------------------------------------------------------ #

    op.create_table(
        "kyc_verifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("document_type", sa.String(50), nullable=True),
        sa.Column("document_number", sa.String(100), nullable=True),
        sa.Column("document_front", sa.String(500), nullable=True),
        sa.Column("document_back", sa.String(500), nullable=True),
        sa.Column("selfie_photo", sa.String(500), nullable=True),
        sa.Column("verified_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("verified_at", sa.DateTime, nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
    )
    op.create_index("ix_kyc_verifications_user_id", "kyc_verifications", ["user_id"])
    op.create_index("ix_kyc_verifications_status", "kyc_verifications", ["status"])

    op.create_table(
        "security_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("is_blocked", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_security_events_user_id", "security_events", ["user_id"])
    op.create_index("ix_security_events_event_type", "security_events", ["event_type"])
    op.create_index("ix_security_events_severity", "security_events", ["severity"])
    op.create_index("ix_security_events_created_at", "security_events", ["created_at"])

    op.create_table(
        "login_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("is_successful", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("failure_reason", sa.String(200), nullable=True),
        sa.Column("mfa_used", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_login_history_user_id", "login_history", ["user_id"])
    op.create_index("ix_login_history_created_at", "login_history", ["created_at"])

    # ------------------------------------------------------------------ #
    # GROUP 3 — Triage workflow                                            #
    # ------------------------------------------------------------------ #

    op.create_table(
        "triage_queue",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("report_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("vulnerability_reports.id", ondelete="CASCADE"),
                  nullable=False, unique=True),
        sa.Column("priority", sa.Integer, nullable=False, server_default="5"),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("assigned_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_triage_queue_report_id", "triage_queue", ["report_id"])
    op.create_index("ix_triage_queue_status", "triage_queue", ["status"])
    op.create_index("ix_triage_queue_priority", "triage_queue", ["priority"])

    op.create_table(
        "triage_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("report_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("vulnerability_reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("specialist_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("assigned_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_triage_assignments_report_id", "triage_assignments", ["report_id"])
    op.create_index("ix_triage_assignments_specialist_id", "triage_assignments", ["specialist_id"])

    op.create_table(
        "validation_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("report_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("vulnerability_reports.id", ondelete="CASCADE"),
                  nullable=False, unique=True),
        sa.Column("validator_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_valid", sa.Boolean, nullable=False),
        sa.Column("severity_rating", sa.String(20), nullable=True),
        sa.Column("cvss_score", sa.Numeric(3, 1), nullable=True),
        sa.Column("recommended_reward", sa.Numeric(15, 2), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("validated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_validation_results_report_id", "validation_results", ["report_id"])

    op.create_table(
        "duplicate_detections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("report_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("vulnerability_reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("duplicate_of", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("vulnerability_reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("similarity_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("detection_method", sa.String(50), nullable=False, server_default="manual"),
        sa.Column("detected_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_duplicate_detections_report_id", "duplicate_detections", ["report_id"])
    op.create_index("ix_duplicate_detections_duplicate_of", "duplicate_detections", ["duplicate_of"])

    # ------------------------------------------------------------------ #
    # GROUP 4 — Payment completeness                                       #
    # ------------------------------------------------------------------ #

    op.create_table(
        "payment_gateways",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("config", postgresql.JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
    )

    op.create_table(
        "payout_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("researcher_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("researchers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("payment_method", sa.String(50), nullable=False),
        sa.Column("payment_details", postgresql.JSONB, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("processed_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("processed_at", sa.DateTime, nullable=True),
        sa.Column("failure_reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
    )
    op.create_index("ix_payout_requests_researcher_id", "payout_requests", ["researcher_id"])
    op.create_index("ix_payout_requests_status", "payout_requests", ["status"])
    op.create_index("ix_payout_requests_created_at", "payout_requests", ["created_at"])

    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reference_type", sa.String(50), nullable=True),
        sa.Column("gateway_response", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])
    op.create_index("ix_transactions_type", "transactions", ["type"])
    op.create_index("ix_transactions_status", "transactions", ["status"])
    op.create_index("ix_transactions_reference_id", "transactions", ["reference_id"])
    op.create_index("ix_transactions_created_at", "transactions", ["created_at"])

    op.create_table(
        "payment_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("payment_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("bounty_payments.payment_id", ondelete="CASCADE"), nullable=False),
        sa.Column("previous_status", sa.String(20), nullable=False),
        sa.Column("new_status", sa.String(20), nullable=False),
        sa.Column("changed_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("changed_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_payment_history_payment_id", "payment_history", ["payment_id"])
    op.create_index("ix_payment_history_changed_at", "payment_history", ["changed_at"])

    # ------------------------------------------------------------------ #
    # GROUP 5 — Ops / platform tables                                      #
    # ------------------------------------------------------------------ #

    op.create_table(
        "webhook_endpoints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("secret", sa.String(100), nullable=True),
        sa.Column("events", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
    )
    op.create_index("ix_webhook_endpoints_organization_id", "webhook_endpoints", ["organization_id"])

    op.create_table(
        "webhook_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("endpoint_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("webhook_endpoints.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event", sa.String(100), nullable=False),
        sa.Column("payload", postgresql.JSONB, nullable=True),
        sa.Column("response_status", sa.Integer, nullable=True),
        sa.Column("response_body", sa.Text, nullable=True),
        sa.Column("error_message", sa.String(500), nullable=True),
        sa.Column("retry_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_webhook_logs_endpoint_id", "webhook_logs", ["endpoint_id"])
    op.create_index("ix_webhook_logs_created_at", "webhook_logs", ["created_at"])

    op.create_table(
        "email_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("subject", sa.String(200), nullable=False),
        sa.Column("body_html", sa.Text, nullable=False),
        sa.Column("body_text", sa.Text, nullable=True),
        sa.Column("variables", postgresql.JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
    )

    op.create_table(
        "data_exports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("export_type", sa.String(50), nullable=False),
        sa.Column("format", sa.String(20), nullable=False, server_default="csv"),
        sa.Column("filters", postgresql.JSONB, nullable=True),
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("file_size", sa.BigInteger, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_data_exports_user_id", "data_exports", ["user_id"])
    op.create_index("ix_data_exports_status", "data_exports", ["status"])

    op.create_table(
        "compliance_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("report_type", sa.String(100), nullable=False),
        sa.Column("period_start", sa.DateTime, nullable=False),
        sa.Column("period_end", sa.DateTime, nullable=False),
        sa.Column("data", postgresql.JSONB, nullable=True),
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("generated_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("generated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_compliance_reports_report_type", "compliance_reports", ["report_type"])
    op.create_index("ix_compliance_reports_generated_at", "compliance_reports", ["generated_at"])


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table("compliance_reports")
    op.drop_table("data_exports")
    op.drop_table("email_templates")
    op.drop_table("webhook_logs")
    op.drop_table("webhook_endpoints")
    op.drop_table("payment_history")
    op.drop_table("transactions")
    op.drop_table("payout_requests")
    op.drop_table("payment_gateways")
    op.drop_table("duplicate_detections")
    op.drop_table("validation_results")
    op.drop_table("triage_assignments")
    op.drop_table("triage_queue")
    op.drop_table("login_history")
    op.drop_table("security_events")
    op.drop_table("kyc_verifications")
    op.drop_table("financial_officers")
    op.drop_table("administrators")
    op.drop_table("triage_specialists")
