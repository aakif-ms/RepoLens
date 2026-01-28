from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import repos
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="RepoLens")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)

app.include_router(repos.router)

@app.get("/health")
def health_check():
    return{
        "status": "OK",
        "service": "RepoLens Backend"
    }