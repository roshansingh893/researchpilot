from fastapi import FastAPI

app = FastAPI(title="ResearchPilot")


@app.get("/health")
def health_check():
    return {"status": "healthy", "project": "ResearchPilot"}
