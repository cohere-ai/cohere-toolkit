"""seed tools data

Revision ID: 5d15eef23755
Revises: adcede7e18a5
Create Date: 2024-07-23 12:50:09.337508

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from backend.database_models.seeders.tools_seed import (
    delete_tools_data,
    seed_tools_data,
)

# revision identifiers, used by Alembic.
revision: str = "5d15eef23755"
down_revision: Union[str, None] = "124d5b7b9932"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    seed_tools_data(op)


def downgrade() -> None:
    delete_tools_data(op)
