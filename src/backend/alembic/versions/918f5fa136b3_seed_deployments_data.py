"""seed_deployments_data

Revision ID: 918f5fa136b3
Revises: 8b303ecccde1
Create Date: 2024-07-04 23:36:45.159514

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from backend.database_models.seeders.deplyments_models_seed import (
    delete_default_models,
    deployments_models_seed,
)

# revision identifiers, used by Alembic.
revision: str = "918f5fa136b3"
down_revision: Union[str, None] = "3db4a6321b7a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    deployments_models_seed(op)


def downgrade() -> None:
    delete_default_models(op)
