from __future__ import annotations
import json
from pathlib import Path
from typing import TypedDict
import tomllib

from app.services.project_file_detector import ProjectFileDiscoveryResult

class ResolvedPackage(TypedDict):
    name: str
    version: str
    ecosystem: str
    source_file: str

class LockFileDetectionResult(TypedDict):
    packages: list[ResolvedPackage]

def detect_resolved_packages(
        repository_path: Path,
        project_files: ProjectFileDiscoveryResult,
) -> LockFileDetectionResult:
    resolved_packages: list[ResolvedPackage] =[]

    for relative_path_text in project_files["lock_files"]:
        lock_file_path = repository_path / relative_path_text
        filename = lock_file_path.name.lower()

        if filename == "package-lock.json":
            resolved_packages.extend(
                _parse_package_lock_json(
                    lock_file_path=lock_file_path,
                    source_file=relative_path_text
                )
            )

        elif filename == "yarn.lock":
            resolved_packages.extend(
                _parse_yarn_lock(
                    lock_file_path=lock_file_path,
                    source_file=relative_path_text
                )
            )

        elif filename == "poetry.lock":
            resolved_packages.extend(
                _parse_poetry_lock(
                    lock_file_path=lock_file_path,
                    source_file=relative_path_text
                )
            )

    return {
        "packages": _deduplicate_resolved_packages(
            resolved_packages
        )
    }

def _parse_yarn_lock(
        lock_file_path: Path,
        source_file: str,
) -> list[ResolvedPackage]:
    try:
        contents = lock_file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    resolved_packages: list[ResolvedPackage] = []

    current_selectors: list[str] = []
    current_version: str | None = None

    for raw_line in contents.splitlines():
        line = raw_line.rstrip()

        if not line.startswith(" ") and line.endswith(":"):
            current_selectors = _parse_yarn_selectors(
                line[:-1]
            )
            current_version = None
            continue

        stripped_line = line.strip()

        if stripped_line.startswith("version "):
            current_version = _parse_yarn_version(
                stripped_line
            )

            if current_version is None:
                continue

            for selector in current_selectors:
                package_name = _package_name_for_yarn_selector(
                    selector
                )

                if package_name is None:
                    continue

                resolved_packages.append(
                    {
                        "name": package_name,
                        "version": current_version,
                        "ecosystem": "npm",
                        "source_file": source_file
                    }
                )

    return resolved_packages

def _parse_package_lock_json(
        lock_file_path: Path,
        source_file: str,
) -> list[ResolvedPackage]:
    try:
        lock_data = json.loads(
            lock_file_path.read_text(encoding="utf-8")
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []

    packages = lock_data.get("packages")

    if isinstance(packages, dict):
        return _parse_modern_package_lock(
            packages=packages,
            source_file=source_file
        )

    dependencies = lock_data.get("dependencies")

    if isinstance(dependencies, dict):
        return _parse_legacy_package_lock(
            dependencies=dependencies,
            source_file=source_file
        )

    return []

def _parse_modern_package_lock(
        packages: dict,
        source_file: str,
) -> list[ResolvedPackage]:
    resolved_packages: list[ResolvedPackage] = []

    for package_path, package_data in packages.items():
        if not package_path:
            continue

        if not isinstance(package_data, dict):
            continue

        version = package_data.get("version")

        if not isinstance(version, str):
            continue

        package_name = _package_name_from_node_modules_path(
            package_path
        )

        if package_name is None:
            continue

        resolved_packages.append(
            {
                "name": package_name,
                "version": version,
                "ecosystem": "npm",
                "source_file": source_file
            }
        )

    return resolved_packages

def _package_name_from_node_modules_path(
        package_path: str,
) -> str | None:
    marker = "node_modules/"

    if marker not in package_path:
        return None

    package_name = package_path.rsplit(
        marker,
        maxsplit=1
    )[1]

    if not package_name:
        return None

    return package_name

def _parse_legacy_package_lock(
        dependencies: dict,
        source_file: str,
) -> list[ResolvedPackage]:
    resolved_packages: list[ResolvedPackage] = []

    def visit_dependencies(
            dependency_map: dict,
    ) -> None:
        for package_name, package_data in dependency_map.items():
            if not isinstance(package_data, dict):
                continue

            version = package_data.get("version")

            if isinstance(version, str):
                resolved_packages.append(
                    {
                        "name": str(package_name),
                        "version": version,
                        "ecosystem": "npm",
                        "source_file": source_file
                    }
                )

            nested_dependencies = package_data.get(
                "dependencies"
            )

            if isinstance(nested_dependencies, dict):
                visit_dependencies(nested_dependencies)

    visit_dependencies(dependencies)

    return resolved_packages

def _deduplicate_resolved_packages(
        packages: list[ResolvedPackage],
) -> list[ResolvedPackage]:
    unique_packages: dict[
        tuple[str, str, str],
        ResolvedPackage
    ] = {}

    for package in packages:
        key = (
            package["ecosystem"],
            package["name"].lower(),
            package["version"]
        )

        unique_packages[key] = package

    return sorted(
        unique_packages.values(),
        key=lambda package: (
            package["name"].lower(),
            package["version"]
        )
    )

def _parse_yarn_selectors(
        selector_line: str
) -> list[str]:
    selectors: list[str] = []

    for selector in selector_line.split(","):
        cleaned_selector = selector.strip().strip('"')

        if cleaned_selector:
            selectors.append(cleaned_selector)

    return selectors

def _parse_yarn_version(
        version_line: str,
) -> str | None:
    _, _, version_text = version_line.partition(" ")

    version = version_text.strip().strip('"')

    return version or None

def _package_name_for_yarn_selector(
        selector: str,
) -> str | None:
    selector = selector.strip().strip('"')

    if selector.startswith("@"):
        slash_position = selector.find("/")

        if slash_position == -1:
            return None

        version_separator = selector.find(
            "@",
            slash_position
        )

        if version_separator == -1:
            return selector

        return selector[:version_separator]

    version_separator = selector.find("@")

    if version_separator == -1:
        return selector or None

    return selector[:version_separator] or None

def _parse_poetry_lock(
        lock_file_path: Path,
        source_file: str,
) -> list[ResolvedPackage]:
    try:
        with lock_file_path.open("rb") as file:
            lock_data = tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError):
        return []

    resolved_packages: list[ResolvedPackage] = []

    for package in lock_data.get("package", []):
        name = package.get("name")
        version = package.get("version")

        if not isinstance(name, str) or not isinstance(version, str):
            continue

        resolved_packages.append(
            {
                "name": name,
                "version": version,
                "ecosystem": "python",
                "source_file": source_file
            }
        )

    return resolved_packages