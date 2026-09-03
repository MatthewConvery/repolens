from pathlib import Path
from typing import TypedDict

class ProjectFileDiscoveryResult(TypedDict):
    manifests: list[str]
    lock_files: list[str]
    infrastructure_files: list[str]
    ci_files: list[str]

MANIFEST_FILENAMES = {
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "pipfile",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "settings.gradle.kts",
    "go.mod",
    "cargo.toml",
    "composer.json",
    "gemfile",
    "go.mod"
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

LOCK_FILENAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "pipfile.lock",
    "cargo.lock",
    "composer.lock",
    "gemfile.lock",
    "go.sum"
}

def discover_project_files(
        repository_path: Path,
) -> ProjectFileDiscoveryResult:
    manifests: list[str] = []
    lock_files: list[str] = []
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

        if filename in LOCK_FILENAMES:
            lock_files.append(relative_path_text)

        if filename in INFRASTRUCTURE_FILENAMES:
            infrastructure_files.append(relative_path_text)

        if _is_github_workflow(relative_path):
            ci_files.append(relative_path_text)

        if filename == ".gitlab-ci.yml":
            ci_files.append(relative_path_text)

    return {
        "manifests": sorted(set(manifests)),
        "lock_files": sorted(set(lock_files)),
        "infrastructure_files": sorted(set(infrastructure_files)),
        "ci_files": sorted(set(ci_files))
    }

def _is_github_workflow(relative_path: Path) -> bool:
    parts = relative_path.parts

    for index, part in enumerate(parts):
        if part != ".github":
            continue

        if (
            len(parts) > index + 2
            and parts[index + 1] == "workflows"
            and relative_path.suffix.lower() in {".yml", ".yaml"}
        ):
            return True

    return False