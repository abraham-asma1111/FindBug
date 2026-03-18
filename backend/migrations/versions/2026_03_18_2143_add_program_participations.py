"""add program participations

Revision ID: 2026_03_18_2143
Revises: 2026_03_17_2100
Create Date: 2026-03-18 21:43:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_18_2143'
down_revision = '2026_03_17_2100'
branch_labels = None
depends_on = None


def upgrade():
    # Create program_participations table
    op.create_table(
        'program_participations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('researcher_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='active', nullable=False),
        sa.Column('left_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['program_id'], ['bounty_programs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['researcher_id'], ['researchers.id'], ondelete='CASCADE')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_program_participations_program_id', 'program_participations', ['program_id'])
    op.create_index('ix_program_participations_researcher_id', 'program_participations', ['researcher_id'])
    op.create_index('ix_program_participations_status', 'program_participations', ['status'])
    
    # Create unique constraint to prevent duplicate active participations
    op.create_index(
        'ix_program_participations_unique_active',
        'program_participations',
        ['program_id', 'researcher_id'],
        unique=True,
        postgresql_where=sa.text("status = 'active'")
    )


def downgrade():
    op.drop_index('ix_program_participations_unique_active', table_name='program_participations')
    op.drop_index('ix_program_participations_status', table_name='program_participations')
    op.drop_index('ix_program_participations_researcher_id', table_name='program_participations')
    op.drop_index('ix_program_participations_program_id', table_name='program_participations')
    op.drop_table('program_participations')
