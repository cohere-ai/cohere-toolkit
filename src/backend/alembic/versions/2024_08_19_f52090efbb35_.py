"""empty message

Revision ID: f52090efbb35
Revises: 0091b3b3b4dc, c301506b3676
Create Date: 2024-08-19 17:30:35.031698

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f52090efbb35'
down_revision: Union[str, None] = ('0091b3b3b4dc', 'c301506b3676')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
