"""add_bugcrowd_2026_enhancements

Revision ID: 091e205b7685
Revises: 8a9b2c3d4e5f
Create Date: 2026-03-16 20:28:28.091756

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '091e205b7685'
down_revision: Union[str, Sequence[str], None] = '8a9b2c3d4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add Bugcrowd 2026 enhancements."""
    
    # Add Bugcrowd 2026 fields to researchers table
    op.add_column('researchers', sa.Column('first_name', sa.String(100), nullable=True))
    op.add_column('researchers', sa.Column('last_name', sa.String(100), nullable=True))
    op.add_column('researchers', sa.Column('username', sa.String(50), nullable=True))
    op.add_column('researchers', sa.Column('ninja_email', sa.String(255), nullable=True))
    op.add_column('researchers', sa.Column('linkedin', sa.String(255), nullable=True))
    op.add_column('researchers', sa.Column('skills', sa.Text(), nullable=True))
    op.add_column('researchers', sa.Column('kyc_status', sa.String(20), nullable=False, server_default='pending'))
    op.add_column('researchers', sa.Column('kyc_document_url', sa.String(500), nullable=True))
    
    # Add unique constraints for researchers
    op.create_unique_constraint('uq_researchers_username', 'researchers', ['username'])
    op.create_unique_constraint('uq_researchers_ninja_email', 'researchers', ['ninja_email'])
    
    # Add Bugcrowd 2026 fields to organizations table
    op.add_column('organizations', sa.Column('domain_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('organizations', sa.Column('domain_verification_token', sa.String(255), nullable=True))
    op.add_column('organizations', sa.Column('domain_verification_method', sa.String(20), nullable=True))
    op.add_column('organizations', sa.Column('verified_domains', sa.Text(), nullable=True))
    op.add_column('organizations', sa.Column('business_license_url', sa.String(500), nullable=True))
    op.add_column('organizations', sa.Column('tax_id', sa.String(100), nullable=True))
    op.add_column('organizations', sa.Column('verification_status', sa.String(20), nullable=False, server_default='pending'))
    op.add_column('organizations', sa.Column('sso_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('organizations', sa.Column('sso_provider', sa.String(50), nullable=True))
    op.add_column('organizations', sa.Column('sso_metadata_url', sa.String(500), nullable=True))


def downgrade() -> None:
    """Downgrade schema - Remove Bugcrowd 2026 enhancements."""
    
    # Remove unique constraints for researchers
    op.drop_constraint('uq_researchers_username', 'researchers', type_='unique')
    op.drop_constraint('uq_researchers_ninja_email', 'researchers', type_='unique')
    
    # Remove Bugcrowd 2026 fields from researchers table
    op.drop_column('researchers', 'kyc_document_url')
    op.drop_column('researchers', 'kyc_status')
    op.drop_column('researchers', 'skills')
    op.drop_column('researchers', 'linkedin')
    op.drop_column('researchers', 'ninja_email')
    op.drop_column('researchers', 'username')
    op.drop_column('researchers', 'last_name')
    op.drop_column('researchers', 'first_name')
    
    # Remove Bugcrowd 2026 fields from organizations table
    op.drop_column('organizations', 'sso_metadata_url')
    op.drop_column('organizations', 'sso_provider')
    op.drop_column('organizations', 'sso_enabled')
    op.drop_column('organizations', 'verification_status')
    op.drop_column('organizations', 'tax_id')
    op.drop_column('organizations', 'business_license_url')
    op.drop_column('organizations', 'verified_domains')
    op.drop_column('organizations', 'domain_verification_method')
    op.drop_column('organizations', 'domain_verification_token')
    op.drop_column('organizations', 'domain_verified')
