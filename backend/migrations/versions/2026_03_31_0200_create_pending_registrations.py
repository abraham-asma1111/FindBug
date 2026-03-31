"""Create pending_registrations table

Revision ID: 2026_03_31_0200_create_pending_registrations
Revises: 2026_03_29_1400_create_vrt_tables
Create Date: 2026-03-31 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_31_0200_create_pending_registrations'
down_revision = 'a5d64b176487'
branch_labels = None
depends_on = None


def upgrade():
    """Create pending_registrations table"""
    
    # Create enum for registration type (check if exists first)
    connection = op.get_bind()
    result = connection.execute(
        sa.text("SELECT 1 FROM pg_type WHERE typname = 'registrationtype'")
    ).fetchone()
    
    if not result:
        registration_type_enum = postgresql.ENUM('researcher', 'organization', name='registrationtype')
        registration_type_enum.create(op.get_bind())
    
    # Create pending_registrations table
    op.create_table(
        'pending_registrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        
        # Basic info
        sa.Column('email', sa.String(255), nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('registration_type', postgresql.ENUM('researcher', 'organization', name='registrationtype'), nullable=False),
        
        # Personal info
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        
        # Organization-specific fields (nullable for researchers)
        sa.Column('company_name', sa.String(200), nullable=True),
        sa.Column('phone_number', sa.String(20), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        
        # Verification
        sa.Column('verification_token', sa.String(255), nullable=False, index=True),
        sa.Column('verification_otp', sa.String(10), nullable=True),
        sa.Column('otp_expires_at', sa.DateTime, nullable=True),
        
        # Metadata
        sa.Column('created_at', sa.DateTime, nullable=False, default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('verified_at', sa.DateTime, nullable=True),
        sa.Column('is_verified', sa.Boolean, nullable=False, default=False),
        
        # Request info
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        
        # Constraints
        sa.UniqueConstraint('email', name='uq_pending_registrations_email'),
        sa.Index('ix_pending_registrations_verification_token', 'verification_token'),
        sa.Index('ix_pending_registrations_expires_at', 'expires_at'),
        sa.Index('ix_pending_registrations_created_at', 'created_at'),
    )
    
    print("✅ Created pending_registrations table")


def downgrade():
    """Drop pending_registrations table"""
    op.drop_table('pending_registrations')
    
    # Drop enum
    registration_type_enum = postgresql.ENUM('researcher', 'organization', name='registrationtype')
    registration_type_enum.drop(op.get_bind())
    
    print("✅ Dropped pending_registrations table")