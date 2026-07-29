from __future__ import annotations
import json
from pathlib import Path
from typing import Literal, TypedDict
from app.services.project_file_detector import ProjectFileDiscoveryResult
from app.services.lock_file_detector import LockFileDetectionResult

DependencyScope = Literal[
    "runtime",
    "development",
    "optional",
    "peer",
    "unknown"
]

class DependencyPackage(TypedDict):
    name: str
    requested_version: str | None
    resolved_version: str | None
    scope: DependencyScope
    source_file: str

class DependencyEcosystem(TypedDict):
    package_manager: str
    packages: list[DependencyPackage]

class DependencyDetectionResult(TypedDict):
    Python: DependencyEcosystem | None
    JavaScript: DependencyEcosystem | None

def detect_dependencies(
        repository_path: Path,
        project_files: ProjectFileDiscoveryResult,
) -> DependencyDetectionResult:
    python_packages: list[DependencyPackage] = []
    javascript_packages: list[DependencyPackage] = []

    for relative_path_text in project_files["manifests"]:
        manifest_path = repository_path / relative_path_text
        filename = manifest_path.name.lower()

        if filename == "requirements.txt":
            python_packages.extend(
                _parse_requirements_txt(
                    manifest_path=manifest_path,
                    source_file=relative_path_text
                )
            )

        elif filename == "package.json":
            javascript_packages.extend(
                _parse_package_json(
                    manifest_path=manifest_path,
                    source_file=relative_path_text
                )
            )

    python_packages = _deduplicate_packages(python_packages)
    javascript_packages = _deduplicate_packages(javascript_packages)

    return {
        "Python": (
            {
                "package_manager": "pip",
                "packages": python_packages
            }
            if python_packages
            else None
        ),
        "JavaScript": (
            {
                "package_manager": "npm",
                "packages": javascript_packages
            }
            if javascript_packages
            else None
        )
    }

def _parse_package_json(
        manifest_path: Path,
        source_file: str,
) -> list[DependencyPackage]:
    try:
        package_data = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []

    packages: list[DependencyPackage] = []

    dependency_sections: dict[str, DependencyScope] = {
        "dependencies": "runtime",
        "devDependencies": "development",
        "optionalDependencies": "optional",
        "peerDependencies": "peer"
    }

    for section_name, scope in dependency_sections.items():
        section = package_data.get(section_name, {})

        if not isinstance(section, dict):
            continue

        for package_name, requested_version in section.items():
            packages.append(
                {
                    "name": str(package_name),
                    "requested_version": (
                        str(requested_version)
                        if requested_version is not None
                        else None
                    ),
                    "resolved_version": None,
                    "scope": scope,
                    "source_file": source_file
                }
            )

    return packages

def _parse_requirements_txt(
        manifest_path: Path,
        source_file: str,
) -> list[DependencyPackage]:
    try:
        contents = manifest_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    packages: list[DependencyPackage] = []

    for raw_line in contents.splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith(("-r", "--requirement")):
            continue

        if line.startswith(("-e", "--editable")):
            continue

        if line.startswith(("git+", "http://", "https://")):
            continue

        parsed_dependency = _parse_python_dependency_line(line)

        if parsed_dependency is None:
            continue

        package_name, requested_version = parsed_dependency

        packages.append(
            {
                "name": package_name,
                "requested_version": requested_version,
                "resolved_version": None,
                "scope": "runtime",
                "source_file": source_file
            }
        )

    return packages

def _parse_python_dependency_line(
        line: str,
) -> tuple[str, str | None] | None:
    line_without_comment = line.split("#", maxsplit=1)[0].strip()

    if not line_without_comment:
        return None

    requirement_part = line_without_comment.split(
        ";",
        maxsplit=1
    )[0].strip()

    if not requirement_part:
        return None

    separators = (
        "===",
        "==",
        ">=",
        "<=",
        "~=",
        "!=",
        ">",
        "<",
    )

    separator_position: int | None = None

    for separator in separators:
        position = requirement_part.find(separator)

        if position == -1:
            continue

        if separator_position is None or position < separator_position:
            separator_position = position

    if separator_position is None:
        package_name = requirement_part
        requested_version = None
    else:
        package_name = requirement_part[:separator_position].strip()
        requested_version = requirement_part[separator_position:].strip()

    if "[" in package_name:
        package_name = package_name.split("[", maxsplit=1)[0]

    package_name = package_name.strip()

    if not package_name:
        return None

    return package_name, requested_version

def _deduplicate_packages(
        packages: list[DependencyPackage],
) -> list[DependencyPackage]:
    unique_packages: dict[
        tuple[str, str, str],
        DependencyPackage
    ] = {}

    for package in packages:
        key = (
            package["name"].lower(),
            package["scope"],
            package["source_file"]
        )

        unique_packages[key] = package

    return sorted(
        unique_packages.values(),
        key=lambda package: (
            package["name"].lower(),
            package["scope"]
        )
    )

def attach_resolved_versions(
        dependencies: DependencyDetectionResult,
        resolved_packages: LockFileDetectionResult,
) -> DependencyDetectionResult:
    resolved_versions: dict[
        tuple[str, str],
        set[str]
    ] = {}

    for resolved_package in resolved_packages["packages"]:
        ecosystem = resolved_package["ecosystem"].lower()
        package_name = resolved_package["name"].lower()

        key = (ecosystem, package_name)

        resolved_versions.setdefault(
            key,
            set()
        ).add(resolved_package["version"])

    ecosystem_dependencies = (
        ("JavaScript", "npm"),
        ("Python", "python")
    )

    for dependency_key, ecosystem in ecosystem_dependencies:
        dependency_group = dependencies.get(dependency_key)

        if dependency_group is None:
            continue

        for package in dependency_group["packages"]:
            key = (
                ecosystem,
                package["name"].lower()
            )

            versions = sorted(
                resolved_versions.get(key, set())
            )

            requested_version = package["requested_version"]

            if requested_version in versions:
                package["resolved_version"] = requested_version
            elif len(versions) == 1:
                package["resolved_version"] = versions[0]
            else:
                package["resolved_version"] = None

    return dependencies