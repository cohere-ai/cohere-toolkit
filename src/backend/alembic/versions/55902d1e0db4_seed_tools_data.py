"""seed tools data

Revision ID: 55902d1e0db4
Revises: f534a188bbf0
Create Date: 2024-07-24 13:41:59.355914

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from backend.database_models.seeders.tools_seed import (
    delete_tools_data,
    seed_tools_data,
)

# revision identifiers, used by Alembic.
revision: str = "55902d1e0db4"
down_revision: Union[str, None] = "f534a188bbf0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    seed_tools_data(op)


def downgrade() -> None:
    delete_tools_data(op)
