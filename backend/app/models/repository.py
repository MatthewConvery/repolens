from pydantic import BaseModel

class RepositoryScanResponse(BaseModel):
    filename: str
    files: int
    folders: int
    total_size_bytes: int
    extensions: dict[str, int]