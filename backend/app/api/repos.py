from fastapi import APIRouter
from pydantic import BaseModel
from app.services.repo_cloner import clone_repo
from app.services.repo_scanner import scan_repository as scan_repo
from pathlib import Path

router = APIRouter(prefix="/repos")

class CloneRequest(BaseModel):
    repo_url: str

@router.post("/clone")
def clone(request: CloneRequest):
    repo_url = request.repo_url.strip()
    repo_path = clone_repo(repo_url, "test-repo")
    return {"message": "cloned", "path": str(repo_path)}

@router.get("/scan")
def scan():
    repo_path = Path("../.repos/test-repo").resolve()
    files = scan_repo(repo_path)
    return {
        "total_files": len(files),
        "files": files[:20]
    }
