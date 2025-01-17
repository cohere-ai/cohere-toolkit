"""seed deployments data

Revision ID: 117f0d9b1d3d
Revises: 9891196e479a
Create Date: 2024-08-01 15:15:25.446575

"""

from typing import Sequence, Union

from alembic import op

from backend.database_models.seeders.organization_seed import (
    delete_default_organization,
    seed_default_organization,
)

# revision identifiers, used by Alembic.
revision: str = "117f0d9b1d3d"
down_revision: Union[str, None] = "9891196e479a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    seed_default_organization(op)


def downgrade() -> None:
    delete_default_organization(op)
