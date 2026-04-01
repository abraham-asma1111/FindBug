"""Create simulation tables

Revision ID: 002
Revises: 001
Create Date: 2026-03-30 08:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create simulation_targets table
    op.create_table('simulation_targets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('difficulty', sa.String(length=50), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('technology_stack', sa.JSON(), nullable=True),
        sa.Column('vulnerabilities', sa.JSON(), nullable=True),
        sa.Column('requires_isolation', sa.Boolean(), nullable=True),
        sa.Column('isolation_type', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create simulations table
    op.create_table('simulations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('level', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('max_hints', sa.Integer(), nullable=False),
        sa.Column('hints_used', sa.Integer(), nullable=False),
        sa.Column('time_spent', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['target_id'], ['simulation_targets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_simulations_user_id'), 'simulations', ['user_id'], unique=False)

    # Create simulation_progress table
    op.create_table('simulation_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('simulation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('current_step', sa.Integer(), nullable=False),
        sa.Column('total_steps', sa.Integer(), nullable=False),
        sa.Column('time_spent', sa.Integer(), nullable=False),
        sa.Column('hints_used', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['simulation_id'], ['simulations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('simulation_id')
    )

    # Create simulation_results table
    op.create_table('simulation_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('simulation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('accuracy', sa.Integer(), nullable=False),
        sa.Column('severity_accuracy', sa.Integer(), nullable=False),
        sa.Column('time_taken', sa.Integer(), nullable=False),
        sa.Column('hints_used', sa.Integer(), nullable=False),
        sa.Column('findings', sa.JSON(), nullable=False),
        sa.Column('total_findings', sa.Integer(), nullable=False),
        sa.Column('valid_findings', sa.Integer(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['simulation_id'], ['simulations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('simulation_id')
    )

    # Create isolation_sessions table
    op.create_table('isolation_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('simulation_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('isolation_type', sa.String(length=50), nullable=False),
        sa.Column('container_id', sa.String(length=100), nullable=True),
        sa.Column('network_id', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('terminated_at', sa.DateTime(), nullable=True),
        sa.Column('cpu_limit', sa.Integer(), nullable=False),
        sa.Column('memory_limit', sa.Integer(), nullable=False),
        sa.Column('disk_limit', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['simulation_id'], ['simulations.id'], ),
        sa.ForeignKeyConstraint(['target_id'], ['simulation_targets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_isolation_sessions_user_id'), 'isolation_sessions', ['user_id'], unique=False)

    # Create simulation_challenges table
    op.create_table('simulation_challenges',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('difficulty', sa.String(length=50), nullable=False),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('objectives', sa.JSON(), nullable=False),
        sa.Column('hints', sa.JSON(), nullable=True),
        sa.Column('solution', sa.Text(), nullable=True),
        sa.Column('max_score', sa.Integer(), nullable=False),
        sa.Column('time_limit', sa.Integer(), nullable=False),
        sa.Column('max_hints', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['target_id'], ['simulation_targets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('simulation_challenges')
    op.drop_index(op.f('ix_isolation_sessions_user_id'), table_name='isolation_sessions')
    op.drop_table('isolation_sessions')
    op.drop_table('simulation_results')
    op.drop_table('simulation_progress')
    op.drop_index(op.f('ix_simulations_user_id'), table_name='simulations')
    op.drop_table('simulations')
    op.drop_table('simulation_targets')