"""
Update tool_auth tokens

Revision ID: dab39bfc1d29
Revises: 208f735ed937
Create Date: 2024-07-30 19:16:44.363172

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import Session

from backend.database_models import ToolAuth
from backend.services.auth.crypto import convert_string_encryption_to_cipher_encryption

# revision identifiers, used by Alembic.
revision: str = "dab39bfc1d29"
down_revision: Union[str, None] = "208f735ed937"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def is_encoded_string(token):
    try:
        token.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        with session.begin():
            res = session.query(ToolAuth).all()

            for tool_auth in res:
                if is_encoded_string(
                    tool_auth.encrypted_access_token
                ) or is_encoded_string(tool_auth.encrypted_refresh_token):
                    new_access_token = convert_string_encryption_to_cipher_encryption(
                        tool_auth.encrypted_access_token
                    )
                    new_refresh_token = convert_string_encryption_to_cipher_encryption(
                        tool_auth.encrypted_refresh_token
                    )

                    tool_auth.encrypted_access_token = new_access_token
                    tool_auth.encrypted_refresh_token = new_refresh_token

            session.commit()

    except Exception as e:
        session.rollback()


def downgrade() -> None:
    pass
