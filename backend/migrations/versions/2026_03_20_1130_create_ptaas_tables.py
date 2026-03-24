"""create ptaas tables

Revision ID: 2026_03_20_1130
Revises: 2026_03_19_1600
Create Date: 2026-03-20 11:30:00.000000

Implements FREQ-29, FREQ-30, FREQ-31
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_20_1130'
down_revision = '2026_03_19_1600'
branch_labels = None
depends_on = None


def upgrade():
    # Create ptaas_engagements table
    op.create_table(
        'ptaas_engagements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('scope', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('testing_methodology', sa.String(length=50), nullable=False),
        sa.Column('custom_methodology_details', sa.Text(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('duration_days', sa.Integer(), nullable=True),
        sa.Column('compliance_requirements', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('compliance_notes', sa.Text(), nullable=True),
        sa.Column('deliverables', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('pricing_model', sa.String(length=50), nullable=False),
        sa.Column('base_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('platform_commission_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('platform_commission_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('subscription_interval', sa.String(length=50), nullable=True),
        sa.Column('subscription_start_date', sa.DateTime(), nullable=True),
        sa.Column('subscription_end_date', sa.DateTime(), nullable=True),
        sa.Column('assigned_researchers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('team_size', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ptaas_engagements_id'), 'ptaas_engagements', ['id'], unique=False)
    op.create_index(op.f('ix_ptaas_engagements_organization_id'), 'ptaas_engagements', ['organization_id'], unique=False)
    op.create_index(op.f('ix_ptaas_engagements_status'), 'ptaas_engagements', ['status'], unique=False)

    # Create ptaas_findings table
    op.create_table(
        'ptaas_findings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('cvss_score', sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column('affected_component', sa.String(length=255), nullable=True),
        sa.Column('reproduction_steps', sa.Text(), nullable=True),
        sa.Column('remediation', sa.Text(), nullable=True),
        sa.Column('references', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('discovered_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('discovered_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['discovered_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['engagement_id'], ['ptaas_engagements.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ptaas_findings_id'), 'ptaas_findings', ['id'], unique=False)
    op.create_index(op.f('ix_ptaas_findings_engagement_id'), 'ptaas_findings', ['engagement_id'], unique=False)
    op.create_index(op.f('ix_ptaas_findings_severity'), 'ptaas_findings', ['severity'], unique=False)

    # Create ptaas_deliverables table
    op.create_table(
        'ptaas_deliverables',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('deliverable_type', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_url', sa.String(length=500), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('submitted_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('approved', sa.Boolean(), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['engagement_id'], ['ptaas_engagements.id'], ),
        sa.ForeignKeyConstraint(['submitted_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ptaas_deliverables_id'), 'ptaas_deliverables', ['id'], unique=False)
    op.create_index(op.f('ix_ptaas_deliverables_engagement_id'), 'ptaas_deliverables', ['engagement_id'], unique=False)

    # Create ptaas_progress_updates table
    op.create_table(
        'ptaas_progress_updates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('update_text', sa.Text(), nullable=False),
        sa.Column('progress_percentage', sa.Integer(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['engagement_id'], ['ptaas_engagements.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ptaas_progress_updates_id'), 'ptaas_progress_updates', ['id'], unique=False)
    op.create_index(op.f('ix_ptaas_progress_updates_engagement_id'), 'ptaas_progress_updates', ['engagement_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_ptaas_progress_updates_engagement_id'), table_name='ptaas_progress_updates')
    op.drop_index(op.f('ix_ptaas_progress_updates_id'), table_name='ptaas_progress_updates')
    op.drop_table('ptaas_progress_updates')
    
    op.drop_index(op.f('ix_ptaas_deliverables_engagement_id'), table_name='ptaas_deliverables')
    op.drop_index(op.f('ix_ptaas_deliverables_id'), table_name='ptaas_deliverables')
    op.drop_table('ptaas_deliverables')
    
    op.drop_index(op.f('ix_ptaas_findings_severity'), table_name='ptaas_findings')
    op.drop_index(op.f('ix_ptaas_findings_engagement_id'), table_name='ptaas_findings')
    op.drop_index(op.f('ix_ptaas_findings_id'), table_name='ptaas_findings')
    op.drop_table('ptaas_findings')
    
    op.drop_index(op.f('ix_ptaas_engagements_status'), table_name='ptaas_engagements')
    op.drop_index(op.f('ix_ptaas_engagements_organization_id'), table_name='ptaas_engagements')
    op.drop_index(op.f('ix_ptaas_engagements_id'), table_name='ptaas_engagements')
    op.drop_table('ptaas_engagements')
