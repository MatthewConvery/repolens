from collections import defaultdict
from pathlib import Path
from typing import TypedDict

class MutableLanguageStatistics(TypedDict):
    files: int
    bytes: int

LANGUAGE_BY_EXTENSION = {
    ".c": "C",
    ".cpp": "C++",
    ".cs": "C#",
    ".css": "CSS",
    ".go": "Go",
    ".html": "HTML",
    ".java": "Java",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".kt": "Kotlin",
    ".php": "PHP",
    ".py": "Python",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".scss": "SCSS",
    ".swift": "Swift",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".vue": "Vue",
}

def detect_languages(
        file_paths: list[Path],
) -> tuple[dict[str, dict[str, int | float]], str | None]:
    language_totals: dict[str, MutableLanguageStatistics] = defaultdict(
        lambda: {
            "files": 0,
            "bytes": 0
        }
    )

    for file_path in file_paths:
        language = LANGUAGE_BY_EXTENSION.get(file_path.suffix.lower())

        if language is None:
            continue

        file_size = file_path.stat().st_size

        language_totals[language]["files"] += 1
        language_totals[language]["bytes"] += file_size

    recognised_bytes = sum(
        statistics["bytes"]
        for statistics in language_totals.values()
    )

    languages: dict[str, dict[str, int | float]] = {}

    for language, statistics in language_totals.items():
        percentage = (
            statistics["bytes"] / recognised_bytes * 100
            if recognised_bytes > 0
            else 0
        )

        languages[language] = {
            "files": statistics["files"],
            "bytes": statistics["bytes"],
            "percentage": round(percentage, 2)
        }

    languages = dict(
        sorted(
            languages.items(),
            key=lambda item: item[1]["bytes"],
            reverse=True
        )
    )

    primary_language = next(iter(languages), None)

    return languages, primary_language