"""add_email_verification_and_mfa_fields

Revision ID: 8a9b2c3d4e5f
Revises: 1fb65c158f19
Create Date: 2026-03-16 15:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a9b2c3d4e5f'
down_revision: Union[str, Sequence[str], None] = '1fb65c158f19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add email verification and MFA fields"""
    
    # Add email verification fields
    op.add_column('users', sa.Column('email_verification_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('email_verification_token_expires', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('email_verified_at', sa.DateTime(), nullable=True))
    
    # Add MFA backup codes
    op.add_column('users', sa.Column('mfa_backup_codes', sa.Text(), nullable=True))
    
    # Add last password change tracking
    op.add_column('users', sa.Column('password_changed_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Remove email verification and MFA fields"""
    
    op.drop_column('users', 'password_changed_at')
    op.drop_column('users', 'mfa_backup_codes')
    op.drop_column('users', 'email_verified_at')
    op.drop_column('users', 'email_verification_token_expires')
    op.drop_column('users', 'email_verification_token')
