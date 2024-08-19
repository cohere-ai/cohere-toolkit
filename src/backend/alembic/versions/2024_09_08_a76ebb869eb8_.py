"""Add agent_id foreign key to snapshots

Revision ID: a76ebb869eb8
Revises: 71d7b35c8a44
Create Date: 2024-08-09 11:25:46.222197

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a76ebb869eb8"
down_revision: Union[str, None] = "71d7b35c8a44"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("snapshots", sa.Column("agent_id", sa.String(), nullable=True))

    # populate current snapshots with agent_id -> use agent_id from conversation
    op.execute(
        """
        UPDATE snapshots
        SET agent_id = conversations.agent_id
        FROM conversations
        WHERE snapshots.conversation_id = conversations.id
        """
    )

    op.create_index("snapshot_agent_id", "snapshots", ["agent_id"], unique=False)
    op.create_foreign_key(
        None, "snapshots", "agents", ["agent_id"], ["id"], ondelete="CASCADE"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "snapshots", type_="foreignkey")
    op.drop_index("snapshot_agent_id", table_name="snapshots")
    op.drop_column("snapshots", "agent_id")
    # ### end Alembic commands ###
