from pydantic import BaseModel

class LanguageStatistics(BaseModel):
    files: int
    bytes: int
    percentage: float

class ProjectFiles(BaseModel):
    manifests: list[str]
    infrastructure_files: list[str]
    ci_files: list[str]

class TechnologyDetection(BaseModel):
    frameworks: list[str]
    build_tools: list[str]
    infrastructure: list[str]

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