"""Main API."""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from orchestron.api.routes import pipelines, runs  # ty: ignore[unresolved-import]
from orchestron.config import get_config
from orchestron.constants import APP_DESCRIPTION, APP_TITLE
from orchestron.db.session import SessionManager, init_db
from orchestron.logger import get_logger
from orchestron.version import __version__

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """API lifespan."""
    config = get_config()
    logger.info("Starting %s version %s", APP_TITLE, __version__)
    logger.debug("Getting DB session")
    session = SessionManager(url=config.db_url)
    logger.debug("Initializing database")
    init_db(engine=session._engine)  # ty: ignore[invalid-argument-type]

    yield


app = FastAPI(title=APP_TITLE, description=APP_DESCRIPTION, version=__version__, lifespan=lifespan)
app.include_router(pipelines.router)
app.include_router(runs.router)


if __name__ == "__main__":
    uvicorn.run(app)
