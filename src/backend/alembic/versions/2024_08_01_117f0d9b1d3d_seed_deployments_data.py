"""seed deployments data

Revision ID: 117f0d9b1d3d
Revises: 9891196e479a
Create Date: 2024-08-01 15:15:25.446575

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from backend.database_models.seeders.deplyments_models_seed import (
    delete_default_models,
    deployments_models_seed,
)

# revision identifiers, used by Alembic.
revision: str = "117f0d9b1d3d"
down_revision: Union[str, None] = "9891196e479a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    deployments_models_seed(op)


def downgrade() -> None:
    delete_default_models(op)
