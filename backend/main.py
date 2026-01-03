from fastapi import FastAPI
from app.api import repos, scan

app = FastAPI(title="RepoLens")

app.include_router(repos.router)
app.include_router(scan.router)

@app.get("/health")
def health_check():
    return{
        "status": "OK",
        "service": "RepoLens Backend"
    }