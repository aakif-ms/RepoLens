from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path
from app.services.repo_scanner import scan_repository
from app.services.lazy_emberdder import maybe_embed
from app.services.vector_store import query

router = APIRouter(prefix="/query")

class QueryRequest(BaseModel):
    q: str

@router.post("/")
def ask(request: QueryRequest):
    repo_path = Path("../.repos/test-repo").resolve()
    if not repo_path.exists():
        return {"error": f"Repositry does not exist at file location {repo_path}"}
    files = scan_repository(repo_path)

    for f in files:
        if f["language"] in {"python", "javascript", "typescript"} and f["num_lines"] < 800:
            maybe_embed(f, repo_path)
    
    results = query(request.q)
    return results