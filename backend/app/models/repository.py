from pydantic import BaseModel
from typing import Literal

class LanguageStatistics(BaseModel):
    files: int
    bytes: int
    percentage: float

class ProjectFiles(BaseModel):
    manifests: list[str]
    lock_files: list[str]
    infrastructure_files: list[str]
    ci_files: list[str]

class TechnologyDetection(BaseModel):
    frameworks: list[str]
    build_tools: list[str]
    infrastructure: list[str]

class DependencyPackageModel(BaseModel):
    name: str
    requested_version: str | None
    resolved_version: str | None = None
    scope: Literal[
        "runtime",
        "development",
        "optional",
        "peer",
        "unknown"
    ]
    source_file: str

class DependencyEcosystemModel(BaseModel):
    package_manager: str
    packages: list[DependencyPackageModel]

class DependencyDetectionModel(BaseModel):
    Python: DependencyEcosystemModel | None = None
    JavaScript: DependencyEcosystemModel | None = None
    Go: DependencyEcosystemModel | None = None

class ResolvedPackageModel(BaseModel):
    name: str
    version: str
    ecosystem: str
    source_file: str

class ResolvedPackagesModel(BaseModel):
    packages: list[ResolvedPackageModel]

class RepositoryScanResponse(BaseModel):
    filename: str
    files: int
    folders: int
    total_size_bytes: int
    extensions: dict[str, int]
    languages: dict[str, LanguageStatistics]
    primary_language: str | None
    project_files: ProjectFiles
    technologies: TechnologyDetection
    dependencies: DependencyDetectionModel
    resolved_packages: ResolvedPackagesModel