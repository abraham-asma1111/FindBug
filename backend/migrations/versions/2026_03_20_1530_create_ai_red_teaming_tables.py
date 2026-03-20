"""create ai red teaming tables

Revision ID: 2026_03_20_1530
Revises: 2026_03_20_1500
Create Date: 2026-03-20 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_20_1530'
down_revision = '2026_03_20_1500'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ai_red_teaming_engagements table
    op.create_table(
        'ai_red_teaming_engagements',
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('target_ai_system', sa.String(255), nullable=False),
        sa.Column('model_type', sa.String(50), nullable=False),
        sa.Column('testing_environment', sa.String(500), nullable=False),
        sa.Column('ethical_guidelines', sa.Text, nullable=False),
        sa.Column('scope_description', sa.Text, nullable=True),
        sa.Column('allowed_attack_types', postgresql.JSON, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('start_date', sa.TIMESTAMP, nullable=True),
        sa.Column('end_date', sa.TIMESTAMP, nullable=True),
        sa.Column('assigned_experts', postgresql.JSON, nullable=True),
        sa.Column('total_findings', sa.Integer, default=0),
        sa.Column('critical_findings', sa.Integer, default=0),
        sa.Column('high_findings', sa.Integer, default=0),
        sa.Column('medium_findings', sa.Integer, default=0),
        sa.Column('low_findings', sa.Integer, default=0),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_ai_engagements_org', 'ai_red_teaming_engagements', ['organization_id'])
    op.create_index('idx_ai_engagements_status', 'ai_red_teaming_engagements', ['status'])

    # Create ai_testing_environments table
    op.create_table(
        'ai_testing_environments',
        sa.Column('environment_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_red_teaming_engagements.engagement_id'), unique=True, nullable=False),
        sa.Column('model_type', sa.String(100), nullable=False),
        sa.Column('sandbox_url', sa.String(500), nullable=False),
        sa.Column('api_endpoint', sa.String(500), nullable=False),
        sa.Column('access_token', sa.String(500), nullable=False),
        sa.Column('access_controls', postgresql.JSON, nullable=False),
        sa.Column('rate_limits', postgresql.JSON, nullable=True),
        sa.Column('is_isolated', sa.Boolean, default=True),
        sa.Column('monitoring_enabled', sa.Boolean, default=True),
        sa.Column('log_all_interactions', sa.Boolean, default=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_ai_env_engagement', 'ai_testing_environments', ['engagement_id'])

    # Create ai_vulnerability_reports table
    op.create_table(
        'ai_vulnerability_reports',
        sa.Column('report_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_red_teaming_engagements.engagement_id'), nullable=False),
        sa.Column('researcher_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('researchers.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('input_prompt', sa.Text, nullable=False),
        sa.Column('model_response', sa.Text, nullable=False),
        sa.Column('attack_type', sa.String(50), nullable=False),
        sa.Column('classification', sa.String(50), nullable=True),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('impact', sa.Text, nullable=False),
        sa.Column('reproduction_steps', sa.Text, nullable=False),
        sa.Column('mitigation_recommendation', sa.Text, nullable=True),
        sa.Column('model_version', sa.String(100), nullable=True),
        sa.Column('environment_details', postgresql.JSON, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='new'),
        sa.Column('submitted_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('validated_at', sa.TIMESTAMP, nullable=True)
    )
    op.create_index('idx_ai_reports_engagement', 'ai_vulnerability_reports', ['engagement_id'])
    op.create_index('idx_ai_reports_researcher', 'ai_vulnerability_reports', ['researcher_id'])
    op.create_index('idx_ai_reports_status', 'ai_vulnerability_reports', ['status'])
    op.create_index('idx_ai_reports_attack_type', 'ai_vulnerability_reports', ['attack_type'])

    # Create ai_finding_classifications table
    op.create_table(
        'ai_finding_classifications',
        sa.Column('classification_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('report_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_vulnerability_reports.report_id'), unique=True, nullable=False),
        sa.Column('primary_category', sa.String(50), nullable=False),
        sa.Column('secondary_categories', postgresql.JSON, nullable=True),
        sa.Column('risk_score', sa.DECIMAL(5, 2), nullable=True),
        sa.Column('confidence_level', sa.DECIMAL(5, 2), nullable=True),
        sa.Column('classified_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('staff.id'), nullable=True),
        sa.Column('classified_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('justification', sa.Text, nullable=False),
        sa.Column('affected_components', postgresql.JSON, nullable=True),
        sa.Column('remediation_priority', sa.String(20), nullable=True)
    )
    op.create_index('idx_ai_classifications_report', 'ai_finding_classifications', ['report_id'])

    # Create ai_security_reports table
    op.create_table(
        'ai_security_reports',
        sa.Column('report_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_red_teaming_engagements.engagement_id'), nullable=False),
        sa.Column('report_title', sa.String(255), nullable=False),
        sa.Column('generated_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('staff.id'), nullable=True),
        sa.Column('total_findings', sa.Integer, default=0),
        sa.Column('security_findings', sa.Integer, default=0),
        sa.Column('safety_findings', sa.Integer, default=0),
        sa.Column('trust_findings', sa.Integer, default=0),
        sa.Column('privacy_findings', sa.Integer, default=0),
        sa.Column('fairness_findings', sa.Integer, default=0),
        sa.Column('critical_count', sa.Integer, default=0),
        sa.Column('high_count', sa.Integer, default=0),
        sa.Column('medium_count', sa.Integer, default=0),
        sa.Column('low_count', sa.Integer, default=0),
        sa.Column('executive_summary', sa.Text, nullable=True),
        sa.Column('key_findings', postgresql.JSON, nullable=True),
        sa.Column('recommendations', sa.Text, nullable=True),
        sa.Column('generated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('report_file_url', sa.String(500), nullable=True)
    )
    op.create_index('idx_ai_security_reports_engagement', 'ai_security_reports', ['engagement_id'])


def downgrade() -> None:
    op.drop_table('ai_security_reports')
    op.drop_table('ai_finding_classifications')
    op.drop_table('ai_vulnerability_reports')
    op.drop_table('ai_testing_environments')
    op.drop_table('ai_red_teaming_engagements')
