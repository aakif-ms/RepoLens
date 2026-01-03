from pathlib import Path
from app.core.ignore import IGNORE_DIRS, IGNORE_EXTENSIONS
from app.services.dependency_extractor import extract_dependencies

LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".md": "markdown",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml"
}

def scan_repository(repo_path: Path):
    files = []

    for path in repo_path.rglob("*"):
        if path.is_dir():
            if path.name in IGNORE_DIRS:
                continue
            continue

        if any(part in IGNORE_DIRS for part in path.parts):
            continue

        if path.suffix in IGNORE_EXTENSIONS:
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        
        language = LANGUAGE_MAP.get(path.suffix, "unknown")
        dependencies = extract_dependencies(path, content)

        files.append({
            "path": str(path.relative_to(repo_path)),
            "extension": path.suffix,
            "language": language,
            "size": path.stat().st_size,
            "num_lines": content.count("\n") + 1,
            "dependencies": dependencies
        })

    return files
