from typing import Annotated, Any, Generator

from backend.config.settings import Settings
from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

load_dotenv()

SQLALCHEMY_DATABASE_URL = Settings().database.url
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_size=5, max_overflow=10, pool_timeout=30
)


def get_session() -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session


DBSessionDep = Annotated[Session, Depends(get_session)]
