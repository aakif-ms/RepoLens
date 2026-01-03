from fastapi import APIRouter, HTTPException
from pathlib import Path

from app.services.repo_scanner import scan_repository

router = APIRouter(prefix="/scan")

@router.get("/")
def scan(repo_id: str):
    repo_path = Path("repos") / repo_id
    
    if not repo_path.exists():
        raise HTTPException(status_code=404, detail="repo not found")

    files = scan_repository(repo_path)

    return{
        "repo_id": repo_id,
        "file_count": len(files),
        "files": files  
    }
    
    