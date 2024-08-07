"""empty message

Revision ID: a9b07acef4e8
Revises: f5819b10ef2a
Create Date: 2024-06-10 15:10:58.650989

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a9b07acef4e8"
down_revision: Union[str, None] = "f5819b10ef2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("agents", "description", existing_type=sa.TEXT(), nullable=False)
    op.alter_column("agents", "preamble", existing_type=sa.TEXT(), nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("agents", "preamble", existing_type=sa.TEXT(), nullable=True)
    op.alter_column("agents", "description", existing_type=sa.TEXT(), nullable=True)
    # ### end Alembic commands ###
