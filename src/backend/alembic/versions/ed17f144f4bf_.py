"""empty message

Revision ID: ed17f144f4bf
Revises: 1acff4138b79
Create Date: 2024-07-10 10:00:50.507812

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from src.backend.schemas.user import DEFAULT_USER_ID

# revision identifiers, used by Alembic.
revision: str = "ed17f144f4bf"
down_revision: Union[str, None] = "1acff4138b79"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Populate the users table with the default user
    op.execute(
        f"""
        INSERT INTO users (id, fullname)
        VALUES ('{DEFAULT_USER_ID}', 'Default User')
        ON CONFLICT (id) DO NOTHING;
        """
    )


def downgrade() -> None:
    pass
