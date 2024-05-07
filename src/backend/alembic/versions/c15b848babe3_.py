"""empty message

Revision ID: c15b848babe3
Revises: 6553b76de6ca, b88f00283a27
Create Date: 2024-05-07 15:59:05.436751

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c15b848babe3"
down_revision: Union[str, None] = ("6553b76de6ca", "b88f00283a27")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
