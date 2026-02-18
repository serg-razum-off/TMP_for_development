import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fin_app.settings.config import HOST, PORT
from fin_app.routers.users import users_router
from fin_app.routers.base import base_router
from fin_app.routers.transactions import transaction_router
from fin_app.db.db_manager import DBManager

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(asctime)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application."""
    logger.info(f">> \n  🔧 Project is starting up on {HOST}:{PORT}")
    try:
        logger.info(">> \n 🔧 Checking database status...")
        with DBManager() as db:
            logger.info("✅ Database is ready and tables are verified.")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    try:
        yield
    finally:
        logger.info(f">> \n  ❌ Project is shutting down on {HOST}:{PORT}")


def create_app() -> FastAPI:
    """Create FastAPI financial tracker application."""
    app = FastAPI(
        title="Financial Tracker",
        description="Financial tracker API application with CRUD operations",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(users_router)
    app.include_router(base_router)
    app.include_router(transaction_router)
    return app
