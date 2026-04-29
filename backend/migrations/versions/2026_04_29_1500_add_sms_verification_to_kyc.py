"""add SMS verification to KYC

Revision ID: 2026_04_29_1500
Revises: 2026_04_29_1000
Create Date: 2026-04-29 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_04_29_1500'
down_revision = '2026_04_29_1000'
branch_labels = None
depends_on = None


def upgrade():
    # Add SMS verification fields to kyc_verifications table
    op.add_column('kyc_verifications', sa.Column('phone_number', sa.String(20), nullable=True))
    op.add_column('kyc_verifications', sa.Column('phone_verified', sa.Boolean(), default=False, nullable=False, server_default='false'))
    op.add_column('kyc_verifications', sa.Column('phone_verification_code', sa.String(10), nullable=True))
    op.add_column('kyc_verifications', sa.Column('phone_verification_code_expires', sa.DateTime(), nullable=True))
    op.add_column('kyc_verifications', sa.Column('phone_verification_attempts', sa.Integer(), default=0, nullable=False, server_default='0'))
    op.add_column('kyc_verifications', sa.Column('phone_verified_at', sa.DateTime(), nullable=True))
    
    # Add index on phone_number for faster lookups
    op.create_index('ix_kyc_verifications_phone_number', 'kyc_verifications', ['phone_number'])


def downgrade():
    # Remove SMS verification fields
    op.drop_index('ix_kyc_verifications_phone_number', table_name='kyc_verifications')
    op.drop_column('kyc_verifications', 'phone_verified_at')
    op.drop_column('kyc_verifications', 'phone_verification_attempts')
    op.drop_column('kyc_verifications', 'phone_verification_code_expires')
    op.drop_column('kyc_verifications', 'phone_verification_code')
    op.drop_column('kyc_verifications', 'phone_verified')
    op.drop_column('kyc_verifications', 'phone_number')
