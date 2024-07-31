"""empty message

Revision ID: 208f735ed937
Revises: dc0d3f19222f
Create Date: 2024-07-24 18:40:59.287003

"""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision: str = "208f735ed937"
down_revision: Union[str, None] = "ed17f144f4bf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

AGENT_TABLE = "agents"
AGENT_ARRAY_COLUMN = "tools"

AGENT_TOOL_METADATA_TABLE = "agent_tool_metadata"
AGENT_TOOL_METADATA_ARRAY_COLUMN = "artifacts"

CITATION_TABLE = "citations"
CITATION_DOCUMENTS_TABLE = "citation_documents"


def is_postgresql():
    conn = op.get_bind()
    return conn.dialect.name == "postgresql"


def get_inspector():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    return inspector


def column_exists_and_is_postgresql_array(table_name, column_name):
    inspector = get_inspector()

    columns = inspector.get_columns(table_name)

    for column in columns:
        if column["name"] == column_name:
            if isinstance(column["type"], ARRAY):
                return True
            break

    return False


def column_exists_and_is_json(table_name, column_name):
    inspector = get_inspector()

    columns = inspector.get_columns(table_name)

    for column in columns:
        if column["name"] == column_name:
            if isinstance(column["type"], sa.JSON):
                return True
            break

    return False


def column_exists(table_name, column_name):
    inspector = get_inspector()

    columns = inspector.get_columns(table_name)

    for column in columns:
        if column["name"] == column_name:
            return True

    return False


def alter_array_column_to_json(table_name, column_name):
    op.execute(
        f"""
        ALTER TABLE {table_name}
        ALTER COLUMN {column_name}
        SET DATA TYPE JSON
        USING array_to_json({column_name})
    """
    )


def alter_to_text_array(table_name, column_name):
    temp_column_name = f"temp_{column_name}"

    # 1. Add a new temporary column of type Text[]
    op.add_column(table_name, sa.Column(temp_column_name, ARRAY(sa.Text)))

    # 2. Update the new temporary column with converted data
    op.execute(
        f"""
        UPDATE {table_name}
        SET {temp_column_name} = (
            SELECT array_agg(value::TEXT)
            FROM json_array_elements_text({column_name}) AS value
        )
    """
    )

    # 3. Drop the original column
    op.drop_column(table_name, column_name)

    # 4. Add the final column with the TEXT[] type
    op.add_column(table_name, sa.Column(column_name, ARRAY(sa.Text)))

    # 5. Copy data from the temporary column to the final column
    op.execute(
        f"""
        UPDATE {table_name}
        SET {column_name} = {temp_column_name}
    """
    )

    # 6. Drop the temporary column
    op.drop_column(table_name, temp_column_name)


def alter_to_jsonb_array(table_name, column_name):
    temp_column_name = f"temp_{column_name}"

    # 1. Add a new temporary column of type JSONB[]
    op.add_column(
        table_name, sa.Column(temp_column_name, ARRAY((JSONB(astext_type=sa.Text()))))
    )

    # 2. Update the new temporary column with converted data
    op.execute(
        f"""
        UPDATE {table_name}
        SET {temp_column_name} = (
            SELECT array_agg(value::JSONB)
            FROM json_array_elements({column_name}::json) AS value
        )
    """
    )

    # 3. Drop the original column
    op.drop_column(table_name, column_name)

    # 4. Add the final column with the JSONB[] type
    op.add_column(
        table_name, sa.Column(column_name, ARRAY((JSONB(astext_type=sa.Text()))))
    )

    # 5. Copy data from the temporary column to the final column
    op.execute(
        f"""
        UPDATE {table_name}
        SET {column_name} = {temp_column_name}
    """
    )

    # 6. Drop the temporary column
    op.drop_column(table_name, temp_column_name)


def upgrade() -> None:
    # Only run this migration for Postgres databases
    if is_postgresql():
        # Handle Agent table
        if column_exists_and_is_postgresql_array(AGENT_TABLE, AGENT_ARRAY_COLUMN):
            alter_array_column_to_json(AGENT_TABLE, AGENT_ARRAY_COLUMN)

        # Handle AgentToolMetadata table
        if column_exists_and_is_postgresql_array(
            AGENT_TOOL_METADATA_TABLE, AGENT_TOOL_METADATA_ARRAY_COLUMN
        ):
            alter_array_column_to_json(
                AGENT_TOOL_METADATA_TABLE, AGENT_TOOL_METADATA_ARRAY_COLUMN
            )

        # Handle Citation table
        if not column_exists(CITATION_DOCUMENTS_TABLE, "id"):
            op.add_column(
                CITATION_DOCUMENTS_TABLE,
                sa.Column(
                    "id",
                    sa.String(),
                    nullable=False,
                    server_default=str(uuid4()),
                ),
            )
        if not column_exists(CITATION_DOCUMENTS_TABLE, "created_at"):
            op.add_column(
                CITATION_DOCUMENTS_TABLE,
                sa.Column("created_at", sa.DateTime(), nullable=True),
            )
        if not column_exists(CITATION_DOCUMENTS_TABLE, "updated_at"):
            op.add_column(
                CITATION_DOCUMENTS_TABLE,
                sa.Column("updated_at", sa.DateTime(), nullable=True),
            )
        if column_exists_and_is_postgresql_array(CITATION_TABLE, "document_ids"):
            op.alter_column(
                CITATION_DOCUMENTS_TABLE,
                "left_id",
                existing_type=sa.String(),
                nullable=False,
            )
            op.alter_column(
                CITATION_DOCUMENTS_TABLE,
                "right_id",
                existing_type=sa.String(),
                nullable=False,
            )
            op.drop_column(CITATION_TABLE, "document_ids")


def downgrade() -> None:
    if is_postgresql():
        # Handle Agent table
        if column_exists_and_is_json(AGENT_TABLE, AGENT_ARRAY_COLUMN):
            alter_to_text_array(AGENT_TABLE, AGENT_ARRAY_COLUMN)

        # Handle AgentToolMetadata table
        if column_exists_and_is_json(
            AGENT_TOOL_METADATA_TABLE, AGENT_TOOL_METADATA_ARRAY_COLUMN
        ):
            alter_to_jsonb_array(
                AGENT_TOOL_METADATA_TABLE, AGENT_TOOL_METADATA_ARRAY_COLUMN
            )

        # Handle Citation table
        if column_exists(CITATION_DOCUMENTS_TABLE, "id"):
            op.drop_column(CITATION_DOCUMENTS_TABLE, "id")
        if not column_exists(CITATION_DOCUMENTS_TABLE, "created_at"):
            op.drop_column(CITATION_DOCUMENTS_TABLE, "created_at")
        if not column_exists(CITATION_DOCUMENTS_TABLE, "updated_at"):
            op.drop_column(CITATION_DOCUMENTS_TABLE, "updated_at")
        if not column_exists(CITATION_TABLE, "document_ids"):
            op.add_column(
                "citations",
                sa.Column(
                    "document_ids",
                    ARRAY(sa.VARCHAR()),
                    autoincrement=False,
                    nullable=False,
                    server_default="{}",
                ),
            )
            op.alter_column(
                CITATION_DOCUMENTS_TABLE,
                "left_id",
                existing_type=sa.String(),
                nullable=True,
            )
            op.alter_column(
                CITATION_DOCUMENTS_TABLE,
                "right_id",
                existing_type=sa.String(),
                nullable=True,
            )
