"""seed_deployments_data

Revision ID: 5e9bf7c18c13
Revises: 2c0fe1677ebf
Create Date: 2024-07-10 23:18:58.751302

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from backend.database_models.seeders.deplyments_models_seed import (
    delete_default_models,
    seed_default_models,
)

# revision identifiers, used by Alembic.
revision: str = "5e9bf7c18c13"
down_revision: Union[str, None] = "2c0fe1677ebf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    seed_default_models(op)


def downgrade() -> None:
    delete_default_models(op)
