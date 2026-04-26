"""merge multiple heads

Revision ID: b6e1ef4870ce
Revises: 2026_03_31_0200_create_pending_registrations, 8524f75065ff, 2026_04_19_staff_deleted
Create Date: 2026-04-19 10:39:49.211357

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6e1ef4870ce'
down_revision: Union[str, Sequence[str], None] = ('2026_03_31_0200_create_pending_registrations', '8524f75065ff', '2026_04_19_staff_deleted')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
