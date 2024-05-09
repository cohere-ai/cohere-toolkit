import logging
import os
from contextlib import asynccontextmanager

from alembic.command import upgrade
from alembic.config import Config
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from backend.config.auth import ENABLED_AUTH_STRATEGY_MAPPING
from backend.routers.auth import router as auth_router
from backend.routers.chat import router as chat_router
from backend.routers.conversation import router as conversation_router
from backend.routers.deployment import router as deployment_router
from backend.routers.experimental_features import router as experimental_feature_router
from backend.routers.tool import router as tool_router
from backend.routers.user import router as user_router
from backend.services.logger import LoggingMiddleware

load_dotenv()

ORIGINS = ["*"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app():
    app = FastAPI(lifespan=lifespan)

    # Add routers
    app.include_router(auth_router)
    app.include_router(chat_router)
    app.include_router(user_router)
    app.include_router(conversation_router)
    app.include_router(tool_router)
    app.include_router(deployment_router)
    app.include_router(experimental_feature_router)

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)

    if ENABLED_AUTH_STRATEGY_MAPPING:
        secret_key = os.environ.get("SESSION_SECRET_KEY", None)

        if not secret_key:
            raise ValueError(
                "Missing SESSION_SECRET_KEY environment variable to enable Authentication."
            )

        # Handle User sessions and Auth
        app.add_middleware(
            SessionMiddleware,
            secret_key=secret_key,
        )

        # Add auth
        for auth in ENABLED_AUTH_STRATEGY_MAPPING.values():
            if auth.SHOULD_ATTACH_TO_APP:
                # TODO: Add app attachment logic for eg OAuth:
                # https://docs.authlib.org/en/latest/client/fastapi.html
                pass

    return app


app = create_app()


@app.get("/health")
async def health():
    """
    Health check for backend APIs
    """
    return {"status": "OK"}


@app.post("/migrate")
async def apply_migrations():
    """
    Applies Alembic migrations - useful for serverless applications
    """
    try:
        alembic_cfg = Config("src/backend/alembic.ini")
        upgrade(alembic_cfg, "head")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error while applying Alembic migrations: {str(e)}"
        )

    return {"status": "Done"}
