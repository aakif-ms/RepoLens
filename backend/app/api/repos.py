from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path
from fastapi.responses import StreamingResponse

from app.services.repo_cloner import clone_repo
from app.services.repo_scanner import scan_repository as scan_repo
from app.services.lazy_emberdder import maybe_embed
from app.services.chat_service import chat_service

router = APIRouter(prefix="/repos")

class CloneRequest(BaseModel):
    repo_url: str

class AskRequest(BaseModel):
    session_id: str
    q: str

@router.post("/clone")
def clone(request: CloneRequest):
    repo_url = request.repo_url.strip()
    repo_path = clone_repo(repo_url, "test-repo")
    
    files = scan_repo(repo_path)
    for f in files:
        if f["language"] in {"python", "javascript", "typescript"} and f["num_lines"] < 800:
            maybe_embed(f, repo_path)
    
    session_id = chat_service.create_session(repo_id="test-repo")
    
    return {"message": "cloned and indexed", "path": str(repo_path), "total_files": len(files), "session_id": session_id}

@router.post("/ask")
def ask(request: AskRequest):
    repo_path = Path("../.repos/test-repo").resolve()
    if not repo_path.exists():
        return {"error": f"Repository does not exist at {repo_path}. Please clone a repository first."}
    
    from app.agents.graph import app as graph_app
    
    session = chat_service.get_session(request.session_id)
    if not session:
        return {
            "error": "Invalid session_id"
        }
    
    chat_service.add_message_to_session(
        request.session_id,
        "user",
        request.q
    )
    
    initial_state = {
        "query": request.q,
        "contexts": [],
        "answer": "",
        "verified": False
    }
    
    result = graph_app.invoke(initial_state)
    
    chat_service.add_message_to_session(
        request.session_id,
        "assistant",
        result["answer"]
    )
    
    return {"answer": result["answer"], "verified": result["verified"],
            "history": chat_service.get_chat_history(request.session_id)}

@router.post("/ask/stream")
async def ask_stream(request: AskRequest):
    generator = chat_service.stream_chat_response(
        session_id=request.session_id,
        user_message=request.q
    )
    
    return StreamingResponse(generator, media_type="application/json")

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
