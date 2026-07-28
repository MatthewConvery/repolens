from collections import Counter
from pathlib import Path
from typing import Any
from app.services.language_detector import detect_languages
from app.services.project_file_detector import discover_project_files

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "target",
    "__pycache__"
}

def scan_repository(repository_path: Path) -> dict[str, Any]:
    file_count = 0
    folder_count = 0
    total_size_bytes = 0
    extension_counts: Counter[str] = Counter()
    scanned_files: list[Path] = []

    for path in repository_path.rglob("*"):
        relative_parts = path.relative_to(repository_path).parts

        if any(part in IGNORED_DIRECTORIES for part in relative_parts):
            continue

        if path.is_dir():
            folder_count += 1
            continue

        if path.is_file():
            file_count += 1
            file_size = path.stat().st_size
            total_size_bytes += file_size

            scanned_files.append(path)

            extension = path.suffix.lower() or "[no extension]"
            extension_counts[extension] += 1

    languages, primary_language = detect_languages(scanned_files)
    project_files = discover_project_files(repository_path)

    return {
        "files": file_count,
        "folders": folder_count,
        "total_size_bytes": total_size_bytes,
        "extensions": dict(extension_counts),
        "languages": languages,
        "primary_language": primary_language,
        "project_files": project_files
    }