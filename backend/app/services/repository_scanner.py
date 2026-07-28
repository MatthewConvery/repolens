from collections import Counter
from pathlib import Path
from typing import Any

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__"
}

def scan_repository(repository_path: Path) -> dict[str, Any]:
    file_count = 0
    folder_count = 0
    total_size_bytes = 0
    extension_counts: Counter[str] = Counter()

    for path in repository_path.rglob("*"):
        relative_parts = path.relative_to(repository_path).parts

        if any(part in IGNORED_DIRECTORIES for part in relative_parts):
            continue

        if path.is_dir():
            folder_count += 1
            continue

        if path.is_file():
            file_count += 1
            total_size_bytes += path.stat().st_size

            extension = path.suffix.lower() or "[no extension]"
            extension_counts[extension] += 1

    return {
        "files": file_count,
        "folders": folder_count,
        "total_size_bytes": total_size_bytes,
        "extensions": dict(extension_counts)
    }