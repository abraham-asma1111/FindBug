"""rename phone fields to email fields

Revision ID: 2026_04_29_1900
Revises: 
Create Date: 2026-04-29 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2026_04_29_1900'
down_revision = '2026_04_29_1500'
branch_labels = None
depends_on = None


def upgrade():
    # Rename phone_number to email_address and increase length
    op.alter_column('kyc_verifications', 'phone_number',
                    new_column_name='email_address',
                    existing_type=sa.VARCHAR(length=20),
                    type_=sa.VARCHAR(length=255),
                    existing_nullable=True)
    
    # Rename phone_verified to email_verified
    op.alter_column('kyc_verifications', 'phone_verified',
                    new_column_name='email_verified',
                    existing_type=sa.BOOLEAN(),
                    existing_nullable=False)
    
    # Rename phone_verification_code to email_verification_code
    op.alter_column('kyc_verifications', 'phone_verification_code',
                    new_column_name='email_verification_code',
                    existing_type=sa.VARCHAR(length=10),
                    type_=sa.VARCHAR(length=255),
                    existing_nullable=True)
    
    # Rename phone_verification_code_expires to email_verification_code_expires
    op.alter_column('kyc_verifications', 'phone_verification_code_expires',
                    new_column_name='email_verification_code_expires',
                    existing_type=sa.DateTime(),
                    existing_nullable=True)
    
    # Rename phone_verification_attempts to email_verification_attempts
    op.alter_column('kyc_verifications', 'phone_verification_attempts',
                    new_column_name='email_verification_attempts',
                    existing_type=sa.INTEGER(),
                    existing_nullable=False)
    
    # Rename phone_verified_at to email_verified_at
    op.alter_column('kyc_verifications', 'phone_verified_at',
                    new_column_name='email_verified_at',
                    existing_type=sa.DateTime(),
                    existing_nullable=True)


def downgrade():
    # Revert all changes
    op.alter_column('kyc_verifications', 'email_address',
                    new_column_name='phone_number',
                    existing_type=sa.VARCHAR(length=255),
                    type_=sa.VARCHAR(length=20),
                    existing_nullable=True)
    
    op.alter_column('kyc_verifications', 'email_verified',
                    new_column_name='phone_verified',
                    existing_type=sa.BOOLEAN(),
                    existing_nullable=False)
    
    op.alter_column('kyc_verifications', 'email_verification_code',
                    new_column_name='phone_verification_code',
                    existing_type=sa.VARCHAR(length=255),
                    type_=sa.VARCHAR(length=10),
                    existing_nullable=True)
    
    op.alter_column('kyc_verifications', 'email_verification_code_expires',
                    new_column_name='phone_verification_code_expires',
                    existing_type=sa.DateTime(),
                    existing_nullable=True)
    
    op.alter_column('kyc_verifications', 'email_verification_attempts',
                    new_column_name='phone_verification_attempts',
                    existing_type=sa.INTEGER(),
                    existing_nullable=False)
    
    op.alter_column('kyc_verifications', 'email_verified_at',
                    new_column_name='phone_verified_at',
                    existing_type=sa.DateTime(),
                    existing_nullable=True)
