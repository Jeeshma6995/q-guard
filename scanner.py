"""Simple static scanner for Python, Java, and C-family source files."""
from pathlib import Path
import re
from rules import RULES

SUPPORTED_EXTENSIONS = {".py": "Python", ".java": "Java", ".c": "C", ".h": "C"}

_COMPILED_RULES = [
    (rule, [re.compile(pattern, re.IGNORECASE) for pattern in rule["patterns"]])
    for rule in RULES
]

def scan_file(path):
    """Return potential cryptographic findings for one source file."""
    path = Path(path)
    language = SUPPORTED_EXTENSIONS.get(path.suffix.lower())
    if language is None or not path.is_file():
        return []

    findings = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []

    for line_number, line in enumerate(lines, start=1):
        for rule, patterns in _COMPILED_RULES:
            matched = next((p.search(line) for p in patterns if p.search(line)), None)
            if not matched:
                continue

            # A lightweight confidence heuristic: comments are less reliable evidence.
            stripped = line.strip()
            is_comment = (
                stripped.startswith("#")
                or stripped.startswith("//")
                or stripped.startswith("/*")
                or stripped.startswith("*")
            )
            findings.append({
                "file": str(path),
                "line": line_number,
                "language": language,
                "algorithm": rule["algorithm"],
                "family": rule["family"],
                "purpose": rule["default_purpose"],
                "quantum_risk": rule["quantum_risk"],
                "confidence": "Low — comment or documentation" if is_comment else "Medium — pattern match",
                "evidence": stripped[:300],
                "recommendation": rule["recommendation"],
            })
    return findings

def scan_path(path, max_files=5000):
    """Scan a file or recursively scan supported source files in a directory."""
    root = Path(path)
    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")

    if root.is_file():
        candidates = [root]
    else:
        ignored_dirs = {".git", ".venv", "venv", "node_modules", "__pycache__", "build", "dist"}
        candidates = []
        for candidate in root.rglob("*"):
            if any(part in ignored_dirs for part in candidate.parts):
                continue
            if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_EXTENSIONS:
                candidates.append(candidate)
                if len(candidates) >= max_files:
                    break

    results = []
    scanned_files = 0
    for candidate in candidates:
        if candidate.suffix.lower() in SUPPORTED_EXTENSIONS:
            scanned_files += 1
            results.extend(scan_file(candidate))
    return scanned_files, results