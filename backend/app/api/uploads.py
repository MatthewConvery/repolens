from pathlib import Path
from tempfile import NamedTemporaryFile
from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(prefix="/upload", tags=["uploads"])

@router.post("")
async def upload_repository(
    file: UploadFile = File(...),
) -> dict[str, str | int]:
    filename = file.filename or "repository.zip"

    if Path(filename).suffix.lower() != ".zip":
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are supported.",
        )

    try:
        with NamedTemporaryFile(delete=False, suffix=".zip") as temporary_file:
            contents = await file.read()
            temporary_file.write(contents)
            temporary_path = Path(temporary_file.name)

        return {
            "filename": filename,
            "content_type": file.content_type or "unknown",
            "size_bytes": len(contents),
            "status": "uploaded"
        }
    finally:
        await file.close()

        if "temporary_path" in locals() and temporary_path.exists():
            temporary_path.unlink()