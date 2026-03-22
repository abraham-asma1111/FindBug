"""create simulation tables

Revision ID: 2026_03_20_1545
Revises: 2026_03_20_1530
Create Date: 2026-03-20 15:45:00.000000

Implements FREQ-23 to FREQ-28: Bug Bounty Simulation Platform
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_20_1545'
down_revision = '2026_03_20_1530'
branch_labels = None
depends_on = None


def upgrade():
    # FREQ-23, FREQ-25: Simulation Challenges
    op.create_table(
        'simulation_challenges',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('category', sa.String(100)),
        sa.Column('vulnerability_type', sa.String(100)),
        sa.Column('difficulty_level', sa.String(20)),  # beginner, intermediate, advanced, expert
        sa.Column('severity', sa.String(20)),  # low, medium, high, critical
        sa.Column('points', sa.Integer, default=0),
        sa.Column('estimated_time_minutes', sa.Integer),
        
        # Docker Configuration
        sa.Column('docker_image', sa.String(255), nullable=False),
        sa.Column('docker_registry', sa.String(255)),
        sa.Column('container_memory_limit', sa.String(20), default='256m'),
        sa.Column('container_cpu_limit', sa.String(20), default='0.5'),
        sa.Column('exposed_port', sa.Integer, default=80),
        sa.Column('environment_variables', postgresql.JSON),
        
        # Learning Resources (FREQ-28)
        sa.Column('tutorial_video_url', sa.String(500)),
        sa.Column('documentation', sa.Text),
        sa.Column('external_resources', postgresql.JSON),
        
        # Hints (FREQ-28)
        sa.Column('hints', postgresql.JSON),
        sa.Column('hint_costs', postgresql.JSON),
        
        # Validation (FREQ-28)
        sa.Column('expected_vulnerability_type', sa.String(100)),
        sa.Column('expected_severity', sa.String(20)),
        sa.Column('validation_keywords', postgresql.JSON),
        sa.Column('validation_rules', postgresql.JSON),
        
        # Solution
        sa.Column('official_solution', sa.Text),
        sa.Column('solution_video_url', sa.String(500)),
        
        # Metadata (FREQ-27: Isolation)
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_published', sa.Boolean, default=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('published_at', sa.TIMESTAMP),
        
        # Stats
        sa.Column('total_attempts', sa.Integer, default=0),
        sa.Column('total_completions', sa.Integer, default=0),
        sa.Column('average_completion_time_minutes', sa.Integer),
        sa.Column('success_rate', sa.Numeric(5, 2))
    )
    
    # FREQ-23, FREQ-27: Active Container Instances (Isolation)
    op.create_table(
        'simulation_instances',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('instance_id', sa.String(50), unique=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('challenge_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('simulation_challenges.id'), nullable=False),
        sa.Column('container_id', sa.String(100)),
        sa.Column('unique_url', sa.String(500)),
        sa.Column('port', sa.Integer),
        sa.Column('status', sa.String(20), default='running'),
        sa.Column('started_at', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('expires_at', sa.TIMESTAMP),
        sa.Column('stopped_at', sa.TIMESTAMP)
    )
    
    # FREQ-24: User Progress Tracking
    op.create_table(
        'simulation_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('challenge_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('simulation_challenges.id'), nullable=False),
        sa.Column('status', sa.String(20), default='not_started'),
        sa.Column('attempts', sa.Integer, default=0),
        sa.Column('hints_used', sa.Integer, default=0),
        sa.Column('completed_at', sa.TIMESTAMP),
        sa.Column('time_spent_seconds', sa.Integer, default=0),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'challenge_id', name='uq_user_challenge_progress')
    )
    
    # FREQ-24, FREQ-26, FREQ-27: Simulation Reports (Isolated from real reports)
    op.create_table(
        'simulation_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('challenge_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('simulation_challenges.id'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('steps_to_reproduce', sa.Text, nullable=False),
        sa.Column('impact_assessment', sa.Text),
        sa.Column('suggested_severity', sa.String(20)),
        sa.Column('proof_of_concept', sa.Text),
        sa.Column('status', sa.String(20), default='submitted'),
        sa.Column('is_correct', sa.Boolean),
        sa.Column('feedback', sa.Text),  # FREQ-28: Automated feedback
        sa.Column('points_awarded', sa.Integer, default=0),
        sa.Column('submitted_at', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('validated_at', sa.TIMESTAMP)
    )
    
    # FREQ-28: Community Solutions (Learning Resources)
    op.create_table(
        'simulation_solutions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('challenge_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('simulation_challenges.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text),
        sa.Column('video_url', sa.String(500)),
        sa.Column('is_approved', sa.Boolean, default=False),
        sa.Column('likes_count', sa.Integer, default=0),
        sa.Column('views_count', sa.Integer, default=0),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Community Solution Comments
    op.create_table(
        'simulation_solution_comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('solution_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('simulation_solutions.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now())
    )
    
    # Community Solution Likes
    op.create_table(
        'simulation_solution_likes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('solution_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('simulation_solutions.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.UniqueConstraint('solution_id', 'user_id', name='uq_solution_user_like')
    )
    
    # FREQ-24, FREQ-27: Leaderboard (Isolated from real platform)
    op.create_table(
        'simulation_leaderboard',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), unique=True, nullable=False),
        sa.Column('total_points', sa.Integer, default=0),
        sa.Column('challenges_completed', sa.Integer, default=0),
        sa.Column('rank', sa.Integer),
        sa.Column('last_updated', sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create indexes for performance
    op.create_index('idx_sim_challenges_difficulty_severity', 'simulation_challenges', ['difficulty_level', 'severity'])
    op.create_index('idx_sim_challenges_category', 'simulation_challenges', ['category'])
    op.create_index('idx_sim_instances_user_challenge', 'simulation_instances', ['user_id', 'challenge_id'])
    op.create_index('idx_sim_instances_status', 'simulation_instances', ['status'])
    op.create_index('idx_sim_progress_user', 'simulation_progress', ['user_id'])
    op.create_index('idx_sim_reports_user', 'simulation_reports', ['user_id'])
    op.create_index('idx_sim_reports_challenge', 'simulation_reports', ['challenge_id'])
    op.create_index('idx_sim_solutions_challenge', 'simulation_solutions', ['challenge_id'])
    op.create_index('idx_sim_leaderboard_rank', 'simulation_leaderboard', ['rank'])


def downgrade():
    # Drop tables in reverse order
    op.drop_table('simulation_leaderboard')
    op.drop_table('simulation_solution_likes')
    op.drop_table('simulation_solution_comments')
    op.drop_table('simulation_solutions')
    op.drop_table('simulation_reports')
    op.drop_table('simulation_progress')
    op.drop_table('simulation_instances')
    op.drop_table('simulation_challenges')
