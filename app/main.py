from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.session import init_db
from app.routers import conversations, documents, hello


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="ResearchPilot", lifespan=lifespan)

app.include_router(hello.router)
app.include_router(documents.router)
app.include_router(conversations.router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "project": "ResearchPilot"}
