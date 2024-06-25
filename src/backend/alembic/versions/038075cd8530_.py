"""empty message

Revision ID: 038075cd8530
Revises: a6efd9f047b4
Create Date: 2024-06-25 14:58:27.531151

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "038075cd8530"
down_revision: Union[str, None] = "a6efd9f047b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "tool_calls",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=True),
        sa.Column("message_id", sa.String(), nullable=False),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("tool_call_message_id", "tool_calls", ["message_id"], unique=False)
    op.drop_index("tool_auth_index", table_name="tool_auth")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index("tool_auth_index", "tool_auth", ["user_id", "tool_id"], unique=True)
    op.drop_index("tool_call_message_id", table_name="tool_calls")
    op.drop_table("tool_calls")
    # ### end Alembic commands ###
