import os
from typing import Annotated, Any, Generator

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.config.settings import Settings
from backend.database_models.base import CustomFilterQuery

load_dotenv()
SQLALCHEMY_DATABASE_URL = Settings().database.url
# if deployed to AWS ECS, use the service discovery endpoint for the database
TOOLKIT_AWS_DB_SERVICE = 'toolkit-app-db'
aws_discovery_endpoint = os.environ.get("COPILOT_SERVICE_DISCOVERY_ENDPOINT", None)
if aws_discovery_endpoint:
    SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://postgres:postgres@{TOOLKIT_AWS_DB_SERVICE}.{aws_discovery_endpoint}:5432"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_size=5, max_overflow=10, pool_timeout=30
)


def get_session() -> Generator[Session, Any, None]:
    with Session(engine, query_cls=CustomFilterQuery) as session:
        yield session


DBSessionDep = Annotated[Session, Depends(get_session)]
