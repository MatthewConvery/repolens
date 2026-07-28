from __future__ import annotations
import json
from pathlib import Path
from typing import TypedDict
from app.services.project_file_detector import ProjectFileDiscoveryResult

class FrameworkDetectionResult(TypedDict):
    frameworks: list[str]
    build_tools: list[str]
    infrastructure: list[str]

def detect_frameworks(
        repository_path: Path,
        project_files: ProjectFileDiscoveryResult,
) -> FrameworkDetectionResult:
    frameworks: set[str] = set()
    build_tools: set[str] = set()
    infrastructure: set[str] = set()

    for relative_path_text in project_files["manifests"]:
        manifest_path = repository_path / relative_path_text
        filename = manifest_path.name.lower()

        if filename == "package.json":
            _inspect_package_json(
                manifest_path=manifest_path,
                frameworks=frameworks,
                build_tools=build_tools
            )

        elif filename == "requirements.txt":
            _inspect_requirements_txt(
                manifest_path=manifest_path,
                frameworks=frameworks,
                build_tools=build_tools
            )

        elif filename == "pyproject.toml":
            _inspect_pyproject_toml(
                manifest_path=manifest_path,
                frameworks=frameworks,
                build_tools=build_tools
            )

        elif filename == "pom.xml":
            build_tools.add("Maven")

        elif filename in {
            "build.gradle",
            "build.gradle.kts",
            "settings.gradle",
            "settings.gradle.kts"
        }:
            build_tools.add("Gradle")

        elif filename == "go.mod":
            build_tools.add("Go Modules")

        elif filename == "cargo.toml":
            build_tools.add("Cargo")

        elif filename == "composer.json":
            build_tools.add("Composer")

        elif filename == "gemfile":
            build_tools.add("Bundler")

    _detect_infrastructure(
        project_files=project_files,
        infrastructure=infrastructure
    )

    return {
        "frameworks": sorted(frameworks),
        "build_tools": sorted(build_tools),
        "infrastructure": sorted(infrastructure)
    }

def _inspect_package_json(
        manifest_path: Path,
        frameworks: set[str],
        build_tools: set[str],
) -> None:
    try:
        package_data = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return

    dependencies = package_data.get("dependencies", {})
    dev_dependencies = package_data.get("devDependencies", {})

    all_dependencies = {
        **dependencies,
        **dev_dependencies
    }

    dependency_names = {
        dependency.lower()
        for dependency in all_dependencies
    }

    if "react" in dependency_names:
        frameworks.add("React")

    if "next" in dependency_names:
        frameworks.add("Next.js")

    if "vue" in dependency_names:
        frameworks.add("Vue")

    if "@angular/core" in dependency_names:
        frameworks.add("Angular")
    
    if "nestjs" in dependency_names or "@nestjs/core" in dependency_names:
        frameworks.add("NestJS")
    
    if "vite" in dependency_names:
        build_tools.add("Vite")

    if "webpack" in dependency_names:
        build_tools.add("Webpack")

    build_tools.add("npm")

def _inspect_requirements_txt(
        manifest_path: Path,
        frameworks: set[str],
        build_tools: set[str],
) -> None:
    try:
        contents = manifest_path.read_text(
            encoding="utf-8"
        ).lower()
    except (OSError, UnicodeDecodeError):
        return

    package_names = _parse_requirements(contents)

    if "fastapi" in package_names:
        frameworks.add("FastAPI")

    if "django" in package_names:
        frameworks.add("Django")

    if "flask" in package_names:
        frameworks.add("Flask")

    if "starlette" in package_names:
        frameworks.add("Starlette")

    build_tools.add("pip")

def _inspect_pyproject_toml(
        manifest_path: Path,
        frameworks: set[str],
        build_tools: set[str],
) -> None:
    try:
        contents = manifest_path.read_text(
            encoding="utf-8"
        ).lower()
    except (OSError, UnicodeDecodeError):
        return
    
    if "fastapi" in contents:
        frameworks.add("FastAPI")
    
    if "django" in contents:
        frameworks.add("Django")
    
    if "flask" in contents:
        frameworks.add("Flask")

    if "[tool.poetry]" in contents:
        build_tools.add("Poetry")
    else:
        build_tools.add("pip")

def _parse_requirements(contents: str) -> set[str]:
    package_names: set[str] = set()

    for line in contents.splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith(("-", "git+", "http://", "https://")):
            continue

        package_name = line

        for separator in (
            "==",
            ">=",
            "<=",
            "~=",
            "!=",
            ">",
            "<",
            "[",
            ";",
        ):
            package_name = package_name.split(
                separator,
                maxsplit=1
            )[0]

        package_name = package_name.strip().lower()

        if package_name:
            package_names.add(package_name)

    return package_names

def _detect_infrastructure(
        project_files: ProjectFileDiscoveryResult,
        infrastructure: set[str],
) -> None:
    for relative_path_text in project_files[
        "infrastructure_files"
    ]:
        filename = Path(relative_path_text).name.lower()

        if filename == "dockerfile":
            infrastructure.add("Docker")

        elif filename in {
            "docker-compose.yml",
            "docker-compose.yaml",
            "compose.yml",
            "compose.yaml"
        }:
            infrastructure.add("Docker Compose")

        elif filename == "nginx.conf":
            infrastructure.add("Nginx")