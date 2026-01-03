from pathlib import Path
import re

PY_IMPORT_RE = re.compile(r'^\s*(?:from|import)\s+([a-zA-Z0-9_\.]+)', re.MULTILINE)
JS_IMPORT_RE = re.compile(r'import\s+.*?from\s+[\'"](.+?)[\'"]')
JS_REQUIRE_RE = re.compile(r'require\([\'"](.+?)[\'"]\)')

def extract_dependencies(path: Path, content: str):
    deps = set()
    
    if path.suffix == ".py":
        for match in PY_IMPORT_RE.findall(content):
            deps.add(match.split(".")[0])
    elif path.suffix in {".js", ".ts", ".jsx", ".tsx"}:
        for match in JS_IMPORT_RE.findall(content):
            deps.add(match)
        for match in JS_REQUIRE_RE.findall(content):
            deps.add(match)
    
    return list(deps)