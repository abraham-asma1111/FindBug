"""Create scope_verifications table.

Revision ID: 2026_05_27_1030_create_scope_verifications
Revises: ptaas_bounty_payment_2026_05_26
Create Date: 2026-05-27 10:30:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_05_27_1030_sv'
down_revision = 'ptaas_bounty_payment_2026_05_26'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'scope_verifications',
        sa.Column('id',                  postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('scope_id',            postgresql.UUID(as_uuid=True), sa.ForeignKey('program_scopes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('program_id',          postgresql.UUID(as_uuid=True), sa.ForeignKey('bounty_programs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organization_id',     postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('domain',              sa.String(500), nullable=False),
        sa.Column('root_domain',         sa.String(255), nullable=False),
        sa.Column('verification_method', sa.String(20),  nullable=False),
        sa.Column('verification_token',  sa.String(100), nullable=False),
        sa.Column('verification_status', sa.String(20),  nullable=False, server_default='unverified'),
        sa.Column('verified_at',         sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at',          sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_checked',        sa.DateTime(timezone=True), nullable=True),
        sa.Column('failure_reason',      sa.Text, nullable=True),
        sa.Column('attempt_count',       sa.Integer, nullable=False, server_default='0'),
        sa.Column('last_attempt_at',     sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by',          postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('admin_note',          sa.Text, nullable=True),
        sa.Column('moderated_by',        postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('moderated_at',        sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at',          sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at',          sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # Indexes
    op.create_index('ix_sv_scope_id',    'scope_verifications', ['scope_id'])
    op.create_index('ix_sv_domain',      'scope_verifications', ['domain'])
    op.create_index('ix_sv_root_domain', 'scope_verifications', ['root_domain'])
    op.create_index('ix_sv_status',      'scope_verifications', ['verification_status'])
    op.create_index('ix_sv_org_id',      'scope_verifications', ['organization_id'])
    op.create_index('ix_sv_expires_at',  'scope_verifications', ['expires_at'])


def downgrade() -> None:
    op.drop_index('ix_sv_expires_at',  table_name='scope_verifications')
    op.drop_index('ix_sv_org_id',      table_name='scope_verifications')
    op.drop_index('ix_sv_status',      table_name='scope_verifications')
    op.drop_index('ix_sv_root_domain', table_name='scope_verifications')
    op.drop_index('ix_sv_domain',      table_name='scope_verifications')
    op.drop_index('ix_sv_scope_id',    table_name='scope_verifications')
    op.drop_table('scope_verifications')
