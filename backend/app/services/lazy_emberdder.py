from pathlib import Path
from app.services.vector_store import upsert

MAX_LINES = 400

def maybe_embed(file_obj: dict, repo_path: Path, repo_id: str = None):
    file_path = repo_path / file_obj["path"]

    content = file_path.read_text(encoding="utf-8", errors="ignore")
    content = "\n".join(content.splitlines()[:MAX_LINES])
    
    if repo_id is None:
        repo_id = repo_path.name

    upsert(
        doc_id=f"{repo_id}:{file_obj['path']}",
        text=content,
        metadata={
            "path": file_obj["path"],
            "language": file_obj["language"],
            "repo_id": repo_id
        }
    )