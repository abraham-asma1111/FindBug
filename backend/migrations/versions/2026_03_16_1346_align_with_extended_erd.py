"""align_with_extended_erd

Revision ID: 1fb65c158f19
Revises: 5d7117b589e9
Create Date: 2026-03-16 13:46:04.715757

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1fb65c158f19'
down_revision: Union[str, Sequence[str], None] = '5d7117b589e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Align database schema with Extended ERD"""
    
    # Drop existing tables (in reverse order of dependencies)
    op.drop_table('staff')
    op.drop_table('researchers')
    op.drop_table('organizations')
    
    # Recreate organizations table according to Extended ERD (8 columns)
    op.create_table('organizations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('company_name', sa.String(length=200), nullable=False),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('subscription_type', sa.String(length=20), nullable=True),
        sa.Column('subscription_expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Recreate researchers table according to Extended ERD (10 columns)
    op.create_table('researchers',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('github', sa.String(length=255), nullable=True),
        sa.Column('twitter', sa.String(length=255), nullable=True),
        sa.Column('reputation_score', sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('total_earnings', sa.DECIMAL(precision=15, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Recreate staff table (keeping original structure for now)
    op.create_table('staff',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('position', sa.String(length=100), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )


def downgrade() -> None:
    """Revert to previous schema"""
    
    # Drop new tables
    op.drop_table('staff')
    op.drop_table('researchers')
    op.drop_table('organizations')
    
    # Recreate old tables
    op.create_table('organizations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('contact_phone', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    op.create_table('researchers',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('reputation_score', sa.Integer(), nullable=True),
        sa.Column('rank', sa.String(length=50), nullable=True),
        sa.Column('signal_strength', sa.Integer(), nullable=True),
        sa.Column('total_reports', sa.Integer(), nullable=True),
        sa.Column('valid_reports', sa.Integer(), nullable=True),
        sa.Column('total_earnings', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    op.create_table('staff',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('position', sa.String(length=100), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
