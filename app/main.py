from fastapi import FastAPI

from app.routers import hello

app = FastAPI(title="ResearchPilot")

app.include_router(hello.router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "project": "ResearchPilot"}
