"""add persona kyc fields

Revision ID: 2026_04_29_1000
Revises: 2026_03_24_0900
Create Date: 2026-04-29 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2026_04_29_1000'
down_revision = '2026_03_24_0900'
branch_labels = None
depends_on = None


def upgrade():
    # Add Persona integration fields to kyc_verifications table
    op.add_column('kyc_verifications', sa.Column('persona_inquiry_id', sa.String(length=100), nullable=True))
    op.add_column('kyc_verifications', sa.Column('persona_template_id', sa.String(length=100), nullable=True))
    op.add_column('kyc_verifications', sa.Column('persona_status', sa.String(length=50), nullable=True))
    op.add_column('kyc_verifications', sa.Column('persona_verified_at', sa.DateTime(), nullable=True))
    
    # Create unique index on persona_inquiry_id
    op.create_index('ix_kyc_verifications_persona_inquiry_id', 'kyc_verifications', ['persona_inquiry_id'], unique=True)


def downgrade():
    # Remove index
    op.drop_index('ix_kyc_verifications_persona_inquiry_id', table_name='kyc_verifications')
    
    # Remove columns
    op.drop_column('kyc_verifications', 'persona_verified_at')
    op.drop_column('kyc_verifications', 'persona_status')
    op.drop_column('kyc_verifications', 'persona_template_id')
    op.drop_column('kyc_verifications', 'persona_inquiry_id')
