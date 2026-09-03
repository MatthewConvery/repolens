from __future__ import annotations
import json
from pathlib import Path
from typing import Literal, TypedDict, Any
from collections.abc import Callable
import tomllib
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
    Go: DependencyEcosystem | None

def detect_dependencies(
        repository_path: Path,
        project_files: ProjectFileDiscoveryResult,
) -> DependencyDetectionResult:
    python_packages: list[DependencyPackage] = []
    javascript_packages: list[DependencyPackage] = []
    go_packages: list[DependencyPackage] = []

    python_package_managers: set[str] = set()
    javascript_package_managers: set[str] = set()
    go_package_managers: set[str] = set()

    for relative_path_text in project_files["manifests"]:
        manifest_path = repository_path / relative_path_text
        filename = manifest_path.name.lower()

        if filename == "requirements.txt":
            parsed_packages = _parse_requirements_txt(
                manifest_path=manifest_path,
                source_file=relative_path_text
            )

            if parsed_packages:
                python_packages.extend(parsed_packages)
                python_package_managers.add("pip")


        elif filename == "pyproject.toml":
            parsed_packages = _parse_poetry_dependencies(
                manifest_path=manifest_path,
                source_file=relative_path_text
            )

            if parsed_packages:
                python_packages.extend(parsed_packages)
                python_package_managers.add("poetry")

        elif filename == "package.json":
            parsed_packages = _parse_package_json(
                manifest_path=manifest_path,
                source_file=relative_path_text
            )

            if parsed_packages:
                javascript_packages.extend(parsed_packages)
                javascript_package_managers.add("npm")

        elif filename == "go.mod":
            parsed_packages = _parse_go_mod_dependencies(
                manifest_path=manifest_path,
                source_file=relative_path_text
            )

            if parsed_packages:
                go_packages.extend(parsed_packages)
                go_package_managers.add("go")

    python_packages = _deduplicate_packages(python_packages, _normalise_python_package_name)
    javascript_packages = _deduplicate_packages(javascript_packages, _normalise_npm_package_name)
    go_packages = _deduplicate_packages(go_packages, _normalise_go_module_name)

    return {
        "Python": (
            {
                "package_manager": _resolve_package_manager(
                    python_package_managers
                ),
                "packages": python_packages
            }
            if python_packages
            else None
        ),
        "JavaScript": (
            {
                "package_manager": _resolve_package_manager(
                    javascript_package_managers
                ),
                "packages": javascript_packages
            }
            if javascript_packages
            else None
        ),
        "Go": (
            {
                "package_manager": _resolve_package_manager(
                    go_package_managers
                ),
                "packages": go_packages
            }
            if go_packages
            else None
        ),
    }

def _resolve_package_manager(
        package_managers: set[str],
) -> str:
    if not package_managers:
        return "unknown"

    if len(package_managers) == 1:
        return next(iter(package_managers))

    return "mixed"

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
        normalise_name: Callable[[str], str]
) -> list[DependencyPackage]:
    unique_packages: dict[
        tuple[str, str | None, DependencyScope, str],
        DependencyPackage
    ] = {}

    for package in packages:
        key = (
            normalise_name(package["name"]),
            package["requested_version"],
            package["scope"],
            package["source_file"]
        )

        unique_packages[key] = package

    return sorted(
        unique_packages.values(),
        key=lambda package: (
            normalise_name(package["name"]),
            package["scope"],
            package["source_file"]
        )
    )

def _normalise_python_package_name(
        package_name: str,
) -> str:
    return package_name.strip().lower().replace("_", "-").replace(".", "-")

def _normalise_npm_package_name(
        package_name: str,
) -> str: return package_name.strip().lower()

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

        if ecosystem == "python":
            package_name = _normalise_python_package_name(
                resolved_package["name"]
            )
        elif ecosystem == "go":
            package_name = _normalise_go_module_name(
                resolved_package["name"]
            )
        else:
            package_name = _normalise_npm_package_name(
                resolved_package["name"]
            )

        key = (ecosystem, package_name)

        resolved_versions.setdefault(
            key,
            set()
        ).add(resolved_package["version"])

    ecosystem_dependencies = (
        ("JavaScript", "npm"),
        ("Python", "python"),
        ("Go", "go")
    )

    for dependency_key, ecosystem in ecosystem_dependencies:
        dependency_group = dependencies.get(dependency_key)

        if dependency_group is None:
            continue

        for package in dependency_group["packages"]:
            if ecosystem == "python":
                package_name = _normalise_python_package_name(
                    package["name"]
                )
            elif ecosystem == "go":
                package_name = _normalise_go_module_name(
                    package["name"]
                )
            else:
                package_name = _normalise_npm_package_name(
                    package["name"]
                )

            versions = sorted(
                resolved_versions.get((ecosystem, package_name), set())
            )

            requested_version = package["requested_version"]

            if ecosystem == "go":
                if (
                    requested_version is not None and requested_version in versions
                ):
                    package["resolved_version"] = requested_version
                else:
                    package["resolved_version"] = None

            else:
                if requested_version is not None and requested_version in versions:
                    package["resolved_version"] = requested_version
                elif len(versions) == 1:
                    package["resolved_version"] = versions[0]
                else:
                    package["resolved_version"] = None

    return dependencies


def _parse_poetry_dependency_version(value: object) -> str | None:
    if isinstance(value, str):
        return value

    if not isinstance(value, dict):
        return None

    version = value.get("version")

    if isinstance(version, str):
        return version

    path = value.get("path")

    if isinstance(path, str):
        return f"path:{path}"

    git = value.get("git")

    if isinstance(git, str):
        reference = _poetry_git_reference(value)

        if reference is not None:
            return f"git:{git}@{reference}"

        return f"git:{git}"

    url = value.get("url")

    if isinstance(url, str):
        return url

    return None

def _poetry_git_reference(
        value: dict[Any, Any],
) -> str | None:
    for key in ("rev", "tag", "branch"):
        reference = value.get(key)

        if isinstance(reference, str):
            return reference
        
    return None

def _parse_poetry_dependencies(
        manifest_path: Path,
        source_file: str,
) -> list[DependencyPackage]:
    try:
        with manifest_path.open("rb") as file:
            manifest_data = tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError):
        return []

    tool = manifest_data.get("tool")

    if not isinstance(tool, dict):
        return []

    poetry = tool.get("poetry")

    if not isinstance(poetry, dict):
        return []

    dependencies: list[DependencyPackage] = []

    runtime_dependencies = poetry.get("dependencies", {})

    if isinstance(runtime_dependencies, dict):
        dependencies.extend(
            _poetry_dependency_section_to_packages(
                dependency_section=runtime_dependencies,
                scope="runtime",
                source_file=source_file
            )
        )

    legacy_dev_dependencies = poetry.get("dev-dependencies", {})

    if isinstance(legacy_dev_dependencies, dict):
        dependencies.extend(
            _poetry_dependency_section_to_packages(
                dependency_section=legacy_dev_dependencies,
                scope="development",
                source_file=source_file
            )
        )

    groups = poetry.get("group", {})

    if isinstance(groups, dict):
        for group_name, group_data in groups.items():
            if not isinstance(group_name, str):
                continue

            if not isinstance(group_data, dict):
                continue

            group_dependencies = group_data.get("dependencies", {})

            if not isinstance(group_dependencies, dict):
                continue

            scope = _poetry_group_scope(group_name)

            dependencies.extend(
                _poetry_dependency_section_to_packages(
                    dependency_section=group_dependencies,
                    scope=scope,
                    source_file=source_file
                )
            )

    return _deduplicate_packages(dependencies, _normalise_python_package_name)

def _poetry_group_scope(
      group_name: str,  
) -> DependencyScope:
        normalised_group_name = group_name.strip().lower()

        development_groups = {
            "dev",
            "development",
            "test",
            "tests",
            "testing",
            "lint",
            "linting",
            "format",
            "formatting",
            "docs",
            "documentation",
            "typing",
            "typecheck",
            "type-checking",
            "quality",
        }

        if normalised_group_name in development_groups:
            return "development"

        return "optional"


def _poetry_dependency_section_to_packages(
        dependency_section: dict[str, Any],
        scope: DependencyScope,
        source_file: str,
) -> list[DependencyPackage]:
    packages: list[DependencyPackage] = []

    for name, value in dependency_section.items():
        if not isinstance(name, str):
            continue

        if name.lower() == "python":
            continue

        requested_version = _parse_poetry_dependency_version(value)

        if requested_version is None:
            continue

        packages.append(
            {
                "name": name,
                "requested_version": requested_version,
                "resolved_version": None,
                "scope": scope,
                "source_file": source_file
            }
        )

    return packages


def _parse_go_mod_dependencies(
        manifest_path: Path,
        source_file: str,
) -> list[DependencyPackage]:
    try:
        content = manifest_path.read_text(
            encoding="utf-8"
        )

    except(OSError, UnicodeDecodeError):
        return []

    packages: list[DependencyPackage] = []

    in_require_block = False

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("//"):
            continue

        if line == "require (":
            in_require_block = True
            continue

        if in_require_block and line == ")":
            in_require_block = False
            continue

        if in_require_block:
            package = _parse_go_requirement_line(
                line=line,
                source_file=source_file
            )

            if package is not None:
                packages.append(package)

            continue

        if line.startswith("require "):
            requirement = line.removeprefix("require ").strip()

            package = _parse_go_requirement_line(
                line=requirement,
                source_file=source_file
            )

            if package is not None:
                packages.append(package)

    return _deduplicate_packages(
        packages,
        _normalise_go_module_name
    )

def _parse_go_requirement_line(
        line: str,
        source_file: str,
) -> DependencyPackage | None:

    if "//" in line:
        dependency_text, _ = line.split(
            "//",
            maxsplit=1
        )
    else:
        dependency_text = line

    parts = dependency_text.split()

    if len(parts) < 2:
        return None

    module_name = parts[0].strip()
    version = parts[1].strip()

    if not module_name or not version:
        return None

    return {
        "name": module_name,
        "requested_version": version,
        "resolved_version": None,
        "scope": "runtime",
        "source_file": source_file
    }

def _normalise_go_module_name(
        package_name: str,
) -> str:
    return package_name.strip()