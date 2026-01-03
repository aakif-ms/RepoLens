from git import Repo
from pathlib import Path
import shutil
import time

BASE_REPO_DIR = Path("../.repos").resolve()

def clone_repo(repo_url: str, repo_id: str) -> Path:
    BASE_REPO_DIR.mkdir(exist_ok=True)

    repo_path = BASE_REPO_DIR / repo_id

    if repo_path.exists():
        shutil.rmtree(repo_path, ignore_errors=True)
        time.sleep(0.5)

    Repo.clone_from(
        repo_url,
        repo_path,
        depth=1
    )

    return repo_path
