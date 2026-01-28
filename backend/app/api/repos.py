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
    
    # Create a meaningful repo ID from the URL
    repo_id = repo_url.split("/")[-1].replace(".git", "")
    if not repo_id:
        repo_id = repo_url.split("/")[-2]
    
    repo_path = clone_repo(repo_url, repo_id)
    
    files = scan_repo(repo_path)
    for f in files:
        if f["language"] in {"python", "javascript", "typescript"} and f["num_lines"] < 800:
            maybe_embed(f, repo_path, repo_id)
    
    session_id = chat_service.create_session(repo_id=repo_id)
    
    return {"message": "cloned and indexed", "path": str(repo_path), "total_files": len(files), "session_id": session_id, "repo_id": repo_id}

@router.post("/ask")
def ask(request: AskRequest):
    session = chat_service.get_session(request.session_id)
    if not session:
        return {"error": "Invalid session_id"}
    
    repo_id = session["repo_id"]
    repo_path = Path(f"../.repos/{repo_id}").resolve()
    
    if not repo_path.exists():
        return {"error": f"Repository does not exist at {repo_path}. Please clone a repository first."}
    
    from app.agents.graph import app as graph_app
    
    chat_service.add_message_to_session(
        request.session_id,
        "user",
        request.q
    )
    
    initial_state = {
        "query": request.q,
        "contexts": [],
        "answer": "",
        "verified": False,
        "repo_id": repo_id
    }
    
    result = graph_app.invoke(initial_state)
    
    chat_service.add_message_to_session(
        request.session_id,
        "assistant",
        result["answer"]
    )
    
    return {"answer": result["answer"], "verified": result["verified"],
            "history": chat_service.get_chat_history(request.session_id)}

@router.get("/session/{session_id}")
def get_session_info(session_id: str):
    session = chat_service.get_session(session_id)
    if not session:
        return {"error": "Session not found"}
    
    return {
        "session_id": session_id,
        "repo_id": session["repo_id"],
        "created_at": session["created_at"].isoformat(),
        "message_count": len(session["messages"])
    }

@router.post("/ask/stream")
async def ask_stream(request: AskRequest):
    generator = chat_service.stream_chat_response(
        session_id=request.session_id,
        user_message=request.q
    )
    
    return StreamingResponse(generator, media_type="application/json")