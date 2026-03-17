"""add_refresh_tokens_and_password_reset

Revision ID: 3f4e5a6b7c8d
Revises: 091e205b7685
Create Date: 2026-03-16 20:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f4e5a6b7c8d'
down_revision: Union[str, Sequence[str], None] = '091e205b7685'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add refresh tokens and password reset."""
    
    # Add refresh token fields to users table
    op.add_column('users', sa.Column('refresh_token', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('refresh_token_expires', sa.DateTime(), nullable=True))
    
    # Add password reset fields to users table
    op.add_column('users', sa.Column('password_reset_token', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('password_reset_token_expires', sa.DateTime(), nullable=True))
    
    # Add session tracking
    op.add_column('users', sa.Column('last_login_ip', sa.String(45), nullable=True))
    op.add_column('users', sa.Column('last_login_device', sa.String(255), nullable=True))


def downgrade() -> None:
    """Downgrade schema - Remove refresh tokens and password reset."""
    
    # Remove session tracking
    op.drop_column('users', 'last_login_device')
    op.drop_column('users', 'last_login_ip')
    
    # Remove password reset fields
    op.drop_column('users', 'password_reset_token_expires')
    op.drop_column('users', 'password_reset_token')
    
    # Remove refresh token fields
    op.drop_column('users', 'refresh_token_expires')
    op.drop_column('users', 'refresh_token')
