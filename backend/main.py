from fastapi import FastAPI
from app.api import repos, scan, query, ask
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="RepoLens")

app.include_router(repos.router)
app.include_router(scan.router)
app.include_router(query.router)
app.include_router(ask.router)

@app.get("/health")
def health_check():
    return{
        "status": "OK",
        "service": "RepoLens Backend"
    }
