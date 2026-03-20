"""create code review tables

Revision ID: 2026_03_20_1400
Revises: 2026_03_20_1330
Create Date: 2026-03-20 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_20_1400'
down_revision = '2026_03_20_1330'
branch_labels = None
depends_on = None


def upgrade():
    # Create code_review_engagements table
    op.create_table(
        'code_review_engagements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('repository_url', sa.String(length=500), nullable=False),
        sa.Column('review_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('findings_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('report_submitted_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['researchers.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_code_review_engagements_organization_id', 'code_review_engagements', ['organization_id'])
    op.create_index('ix_code_review_engagements_reviewer_id', 'code_review_engagements', ['reviewer_id'])
    op.create_index('ix_code_review_engagements_status', 'code_review_engagements', ['status'])

    # Create code_review_findings table
    op.create_table(
        'code_review_findings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('issue_type', sa.String(length=50), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('line_number', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['engagement_id'], ['code_review_engagements.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_code_review_findings_engagement_id', 'code_review_findings', ['engagement_id'])
    op.create_index('ix_code_review_findings_severity', 'code_review_findings', ['severity'])
    op.create_index('ix_code_review_findings_status', 'code_review_findings', ['status'])


def downgrade():
    op.drop_index('ix_code_review_findings_status', table_name='code_review_findings')
    op.drop_index('ix_code_review_findings_severity', table_name='code_review_findings')
    op.drop_index('ix_code_review_findings_engagement_id', table_name='code_review_findings')
    op.drop_table('code_review_findings')
    
    op.drop_index('ix_code_review_engagements_status', table_name='code_review_engagements')
    op.drop_index('ix_code_review_engagements_reviewer_id', table_name='code_review_engagements')
    op.drop_index('ix_code_review_engagements_organization_id', table_name='code_review_engagements')
    op.drop_table('code_review_engagements')
