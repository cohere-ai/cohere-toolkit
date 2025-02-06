import logging
import warnings
from contextlib import asynccontextmanager

from alembic.command import upgrade
from alembic.config import Config
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from backend.config.auth import (
    get_auth_strategy_endpoints,
    is_authentication_enabled,
    verify_migrate_token,
)
from backend.config.routers import ROUTER_DEPENDENCIES, RouterName
from backend.config.settings import Settings
from backend.exceptions import DeploymentNotFoundError
from backend.metrics import RequestMetricsMiddleware
from backend.routers.agent import router as agent_router
from backend.routers.auth import router as auth_router
from backend.routers.chat import router as chat_router
from backend.routers.conversation import router as conversation_router
from backend.routers.deployment import router as deployment_router
from backend.routers.experimental_features import router as experimental_feature_router
from backend.routers.model import router as model_router
from backend.routers.organization import router as organization_router
from backend.routers.scim import SCIMException, scim_exception_handler
from backend.routers.scim import router as scim_router
from backend.routers.snapshot import router as snapshot_router
from backend.routers.tool import router as tool_router
from backend.routers.user import router as user_router
from backend.services.context import ContextMiddleware, get_context
from backend.services.logger.middleware import LoggingMiddleware
from backend.services.logger.utils import LoggerFactory

# Only show errors for Pydantic
logging.getLogger('pydantic').setLevel(logging.ERROR)
# Supress UserWarnings clogging logs
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

load_dotenv()

# CORS Origins
ORIGINS = ["*"]


_RELEASE_VERSION = "v1.1.6"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Retrieves all the Auth provider endpoints if authentication is enabled.
    if is_authentication_enabled():
        await get_auth_strategy_endpoints()
    yield
    # Shutdown logic


def create_app() -> FastAPI:
    app = FastAPI(
        title="Cohere Toolkit API",
        description="This is the API for the Open Source Cohere Toolkit",
        version=_RELEASE_VERSION,
        lifespan=lifespan,
    )

    routers = [
        auth_router,
        chat_router,
        user_router,
        conversation_router,
        tool_router,
        deployment_router,
        experimental_feature_router,
        agent_router,
        snapshot_router,
        organization_router,
        model_router,
        scim_router,
    ]

    # Dynamically set router dependencies
    # These values must be set in config/routers.py
    dependencies_type = "default"
    settings = Settings()
    if is_authentication_enabled():
        # Required to save temporary OAuth state in session
        auth_secret = settings.get('auth.secret_key')
        app.add_middleware(SessionMiddleware, secret_key=auth_secret)
        dependencies_type = "auth"
    for router in routers:
        if getattr(router, "name", "") in ROUTER_DEPENDENCIES.keys():
            router_name = RouterName(getattr(router, "name"))
            dependencies = ROUTER_DEPENDENCIES[router_name][dependencies_type]
            app.include_router(router, dependencies=dependencies)
        else:
            app.include_router(router)

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)
    if settings.get("metrics.enabled"):
        logger = LoggerFactory().get_logger()
        logger.info(event="Metrics enabled")
        app.add_middleware(RequestMetricsMiddleware)
    app.add_middleware(ContextMiddleware)  # This should be the first middleware
    app.add_exception_handler(SCIMException, scim_exception_handler)  # pyright: ignore

    return app


app = create_app()


@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    ctx = get_context(request)
    logger = ctx.get_logger()

    logger.exception(
        event="Unhandled exception",
        error=str(exc),
        method=request.method,
        url=request.url,
        ctx=ctx,
    )

    return JSONResponse(
        status_code=500,
        content={
            "message": (
                f"Failed method {request.method} at URL {request.url}."
                f" Exception message is {exc!r}."
            )
        },
    )


@app.exception_handler(DeploymentNotFoundError)
async def deployment_not_found_handler(request: Request, exc: DeploymentNotFoundError):
    ctx = get_context(request)
    logger = ctx.get_logger()
    logger.error(
        event="Deployment not found",
        deployment_id=exc.deployment_id,
    )
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


@app.get("/health")
async def health():
    """
    Health check for backend APIs
    """
    return {"status": "OK"}


@app.post(
    "/migrate",
    dependencies=[Depends(verify_migrate_token)],
    include_in_schema=False,
)
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

    return {"status": "Migration successful"}
