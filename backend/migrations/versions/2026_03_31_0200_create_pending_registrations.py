"""Create pending_registrations table

Revision ID: pending_reg_20260331
Revises: 2026_03_29_1400_create_vrt_tables
Create Date: 2026-03-31 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'pending_reg_20260331'
down_revision: Union[str, None] = 'a5d64b176487'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

REGISTRATION_TYPE = postgresql.ENUM(
    'researcher',
    'organization',
    name='registrationtype',
    create_type=False,
)


def _enum_exists(bind) -> bool:
    return (
        bind.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'registrationtype'")).fetchone()
        is not None
    )


def upgrade() -> None:
    """Create pending_registrations table — skip objects that already exist."""
    bind = op.get_bind()

    if not _enum_exists(bind):
        postgresql.ENUM(
            'researcher',
            'organization',
            name='registrationtype',
        ).create(bind)

    inspector = sa.inspect(bind)
    if 'pending_registrations' in inspector.get_table_names():
        return

    op.create_table(
        'pending_registrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('registration_type', REGISTRATION_TYPE, nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('company_name', sa.String(200), nullable=True),
        sa.Column('phone_number', sa.String(20), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('verification_token', sa.String(255), nullable=False, index=True),
        sa.Column('verification_otp', sa.String(10), nullable=True),
        sa.Column('otp_expires_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('verified_at', sa.DateTime, nullable=True),
        sa.Column('is_verified', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.UniqueConstraint('email', name='uq_pending_registrations_email'),
        sa.Index('ix_pending_registrations_verification_token', 'verification_token'),
        sa.Index('ix_pending_registrations_expires_at', 'expires_at'),
        sa.Index('ix_pending_registrations_created_at', 'created_at'),
    )


def downgrade() -> None:
    """Drop pending_registrations table."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if 'pending_registrations' in inspector.get_table_names():
        op.drop_table('pending_registrations')

    if _enum_exists(bind):
        postgresql.ENUM(
            'researcher',
            'organization',
            name='registrationtype',
        ).drop(bind, checkfirst=True)
