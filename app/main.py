from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request

from app.apis.base import router
from app.apis.exceptions import BaseAPIException
from app.core.logging import setup_logging
from app.core.middlewares import RequestIDMiddleware, RequestLoggingMiddleware

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Task Tracker API")

    yield  # Server is running

    # Shutdown
    logger.info("Shutting down Task Tracker API")


def include_routers(app: FastAPI):
    app.include_router(router)

    @app.get("/")
    def home():
        logger.info("Health Check", message="I am healthy")
        return {"message": "FastAPI Task Tracker Running!"}

    @app.exception_handler(BaseAPIException)
    def handle_base_api_exception(request: Request, e: BaseAPIException):
        return e.to_response()


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(
        title="Task Tracker API",
        description="Task Tracker API",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(middleware_class=RequestLoggingMiddleware)
    app.add_middleware(middleware_class=RequestIDMiddleware)

    include_routers(app=app)

    return app


app = create_app()
