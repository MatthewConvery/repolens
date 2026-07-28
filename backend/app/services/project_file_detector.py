from pathlib import Path
from typing import TypedDict

class ProjectFileDiscoveryResult(TypedDict):
    manifests: list[str]
    infrastructure_files: list[str]
    ci_files: list[str]

MANIFEST_FILENAMES = {
    "package.json",
    "package-lock.json",
    "requirements.txt",
    "pyproject.toml",
    "poetry.lock",
    "pipfile",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "settings.gradle.kts",
    "go.mod",
    "cargo.toml",
    "composer.json",
    "gemfile"
}

INFRASTRUCTURE_FILENAMES = {
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "nginx.conf"
}

CI_DIRECTORIES = {
    ".github/workflows",
    ".gitlab-ci"
}

def discover_project_files(
        repository_path: Path,
) -> ProjectFileDiscoveryResult:
    manifests: list[str] = []
    infrastructure_files: list[str] = []
    ci_files: list[str] = []

    for path in repository_path.rglob("*"):
        if not path.is_file():
            continue

        relative_path = path.relative_to(repository_path)
        relative_path_text = relative_path.as_posix()
        filename = path.name.lower()

        if filename in MANIFEST_FILENAMES:
            manifests.append(relative_path_text)

        if filename in INFRASTRUCTURE_FILENAMES:
            infrastructure_files.append(relative_path_text)

        if (relative_path_text.startswith(".github/workflows/") and path.suffix.lower() in {".yml", ".yaml"}):
            ci_files.append(relative_path_text)

        if filename == ".gitlab-ci.yml":
            ci_files.append(relative_path_text)

    return {
        "manifests": sorted(manifests),
        "infrastructure_files": sorted(infrastructure_files),
        "ci_files": sorted(ci_files)
    }