"""empty message

Revision ID: ed17f144f4bf
Revises: f077676dfd5d
Create Date: 2024-07-16 10:00:50.507812

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from src.backend.schemas.user import DEFAULT_USER_ID, DEFAULT_USER_NAME

# revision identifiers, used by Alembic.
revision: str = "ed17f144f4bf"
down_revision: Union[str, None] = "f077676dfd5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Populate the users table with the default user
    op.execute(
        f"""
        INSERT INTO users (id, fullname, created_at, updated_at)
        VALUES ('{DEFAULT_USER_ID}', '{DEFAULT_USER_NAME}', now(), now())
        ON CONFLICT (id) DO NOTHING;
        """
    )


def downgrade() -> None:
    pass
