"""create bounty match tables

Revision ID: 2026_03_19_1500
Revises: 2026_03_18_2300
Create Date: 2026-03-19 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_19_1500'
down_revision = '2026_03_18_2300'
branch_labels = None
depends_on = None


def upgrade():
    # Create skill_tags table
    op.create_table(
        'skill_tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('parent_tag_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['parent_tag_id'], ['skill_tags.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_skill_tags_name', 'skill_tags', ['name'])
    op.create_index('ix_skill_tags_category', 'skill_tags', ['category'])
    
    # Create researcher_profiles table
    op.create_table(
        'researcher_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('researcher_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('skills', postgresql.JSONB, nullable=True),
        sa.Column('specializations', postgresql.JSONB, nullable=True),
        sa.Column('experience_years', sa.Integer, nullable=False, server_default='0'),
        sa.Column('timezone', sa.String(50), nullable=True),
        sa.Column('availability_hours', sa.Integer, nullable=True),
        sa.Column('current_workload', sa.Integer, nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['researcher_id'], ['researchers.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_researcher_profiles_researcher_id', 'researcher_profiles', ['researcher_id'])
    
    # Create researcher_skills table
    op.create_table(
        'researcher_skills',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('researcher_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('level', sa.String(20), nullable=False),
        sa.Column('years_experience', sa.Integer, nullable=False, server_default='0'),
        sa.Column('verified', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['researcher_id'], ['researchers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['skill_tags.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_researcher_skills_researcher_id', 'researcher_skills', ['researcher_id'])
    op.create_index('ix_researcher_skills_tag_id', 'researcher_skills', ['tag_id'])
    
    # Create matching_algorithms table
    op.create_table(
        'matching_algorithms',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('version', sa.String(20), nullable=False, unique=True),
        sa.Column('weights', postgresql.JSONB, nullable=False),
        sa.Column('parameters', postgresql.JSONB, nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_matching_algorithms_version', 'matching_algorithms', ['version'])
    op.create_index('ix_matching_algorithms_is_active', 'matching_algorithms', ['is_active'])
    
    # Create matching_requests table
    op.create_table(
        'matching_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_type', sa.String(50), nullable=False),
        sa.Column('criteria', postgresql.JSONB, nullable=False),
        sa.Column('required_skills', postgresql.JSONB, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_matching_requests_organization_id', 'matching_requests', ['organization_id'])
    op.create_index('ix_matching_requests_status', 'matching_requests', ['status'])
    op.create_index('ix_matching_requests_engagement_type', 'matching_requests', ['engagement_type'])
    
    # Create match_results table
    op.create_table(
        'match_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('researcher_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('skill_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('reputation_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('rank', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['request_id'], ['matching_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['researcher_id'], ['researchers.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_match_results_request_id', 'match_results', ['request_id'])
    op.create_index('ix_match_results_researcher_id', 'match_results', ['researcher_id'])
    op.create_index('ix_match_results_match_score', 'match_results', ['match_score'])
    
    # Create matching_invitations table
    op.create_table(
        'matching_invitations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('researcher_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('match_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('message', sa.Text, nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('viewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('response_note', sa.Text, nullable=True),
        sa.ForeignKeyConstraint(['request_id'], ['matching_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['researcher_id'], ['researchers.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_matching_invitations_request_id', 'matching_invitations', ['request_id'])
    op.create_index('ix_matching_invitations_researcher_id', 'matching_invitations', ['researcher_id'])
    op.create_index('ix_matching_invitations_status', 'matching_invitations', ['status'])
    
    # Create matching_feedback table
    op.create_table(
        'matching_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('researcher_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rating', sa.Integer, nullable=False),
        sa.Column('quality_score', sa.Integer, nullable=False),
        sa.Column('communication_score', sa.Integer, nullable=False),
        sa.Column('timeliness_score', sa.Integer, nullable=False),
        sa.Column('would_work_again', sa.Boolean, nullable=False),
        sa.Column('comments', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['request_id'], ['matching_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['researcher_id'], ['researchers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_matching_feedback_request_id', 'matching_feedback', ['request_id'])
    op.create_index('ix_matching_feedback_researcher_id', 'matching_feedback', ['researcher_id'])
    op.create_index('ix_matching_feedback_organization_id', 'matching_feedback', ['organization_id'])
    
    # Create matching_metrics table
    op.create_table(
        'matching_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('total_candidates', sa.Integer, nullable=False, server_default='0'),
        sa.Column('invited_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('accepted_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('declined_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('expired_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('average_match_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('average_response_time', sa.Integer, nullable=True),
        sa.Column('success_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['request_id'], ['matching_requests.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_matching_metrics_request_id', 'matching_metrics', ['request_id'])


def downgrade():
    op.drop_table('matching_metrics')
    op.drop_table('matching_feedback')
    op.drop_table('matching_invitations')
    op.drop_table('match_results')
    op.drop_table('matching_requests')
    op.drop_table('matching_algorithms')
    op.drop_table('researcher_skills')
    op.drop_table('researcher_profiles')
    op.drop_table('skill_tags')
