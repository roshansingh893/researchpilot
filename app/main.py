import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.session import init_db
from app.routers import conversations, documents, hello, retrieve
from app.services.embedding_service import get_embedding_model

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO)
    init_db()
    # Eagerly load the embedding model so the first request isn't slow.
    # The @lru_cache inside get_embedding_model() ensures this runs once.
    get_embedding_model()
    logger.info("ResearchPilot startup complete.")
    yield


app = FastAPI(title="ResearchPilot", lifespan=lifespan)

app.include_router(hello.router)
app.include_router(documents.router)
app.include_router(conversations.router)
app.include_router(retrieve.router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "project": "ResearchPilot"}
