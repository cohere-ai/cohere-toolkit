from sqlalchemy.orm import Session

from backend.config.auth import ENABLED_AUTH_STRATEGY_MAPPING
from backend.crud import user as user_crud
from backend.database_models import User


def is_enabled_authentication_strategy(strategy_name: str) -> bool:
    # Check the strategy is valid and enabled
    if strategy_name not in ENABLED_AUTH_STRATEGY_MAPPING.keys():
        return False

    return True


def get_or_create_user(session: Session, token_user: dict[str, str]) -> User:
    email = token_user.get("email")
    fullname = token_user.get("name")

    user = Session.query(User).filter(User.email == email).first()

    # Create User if DNE
    if not user:
        db_user = User(fullname=fullname, email=email)
        user = user_crud.create_user(session, db_user)

    return user
