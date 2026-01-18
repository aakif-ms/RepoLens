from fastapi import APIRouter
from pydantic import BaseModel
from app.services.repo_cloner import clone_repo
from app.services.repo_scanner import scan_repository as scan_repo
from app.services.lazy_emberdder import maybe_embed
from pathlib import Path

router = APIRouter(prefix="/repos")

class CloneRequest(BaseModel):
    repo_url: str

class AskRequest(BaseModel):
    q: str

@router.post("/clone")
def clone(request: CloneRequest):
    repo_url = request.repo_url.strip()
    repo_path = clone_repo(repo_url, "test-repo")
    
    files = scan_repo(repo_path)
    for f in files:
        if f["language"] in {"python", "javascript", "typescript"} and f["num_lines"] < 800:
            maybe_embed(f, repo_path)
    
    return {"message": "cloned and indexed", "path": str(repo_path), "total_files": len(files)}

@router.post("/ask")
def ask(request: AskRequest):
    repo_path = Path("../.repos/test-repo").resolve()
    if not repo_path.exists():
        return {"error": f"Repository does not exist at {repo_path}. Please clone a repository first."}
    
    from app.agents.graph import app as graph_app
    
    initial_state = {
        "query": request.q,
        "contexts": [],
        "answer": "",
        "verified": False
    }
    
    result = graph_app.invoke(initial_state)
    return {"answer": result["answer"], "verified": result["verified"]}

@router.get("/scan")
def scan():
    """Get repository scan results for debugging"""
    repo_path = Path("../.repos/test-repo").resolve()
    if not repo_path.exists():
        return {"error": "Repository not found"}
    
    files = scan_repo(repo_path)
    return {
        "total_files": len(files),
        "files": files[:20]
    }
