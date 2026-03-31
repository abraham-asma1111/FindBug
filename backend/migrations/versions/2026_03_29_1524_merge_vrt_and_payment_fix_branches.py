"""merge vrt and payment fix branches

Revision ID: a5d64b176487
Revises: 6e1b9728908e, 2026_03_29_1400
Create Date: 2026-03-29 15:24:40.245503

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5d64b176487'
down_revision: Union[str, Sequence[str], None] = ('6e1b9728908e', '2026_03_29_1400')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
