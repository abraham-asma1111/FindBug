"""merge simulation and subscription branches

Revision ID: df02a440f442
Revises: 2026_03_20_1545, 2026_03_20_2230
Create Date: 2026-03-22 10:19:19.084716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df02a440f442'
down_revision: Union[str, Sequence[str], None] = ('2026_03_20_1545', '2026_03_20_2230')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
