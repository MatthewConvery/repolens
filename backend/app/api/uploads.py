from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZipFile
from fastapi import APIRouter, File, HTTPException, UploadFile
from app.services.repository_scanner import scan_repository
from app.models.repository import RepositoryScanResponse

MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024
router = APIRouter(prefix="/upload", tags=["uploads"])

@router.post("", response_model=RepositoryScanResponse)
async def upload_repository(file: UploadFile = File(...)) -> dict:
    filename = file.filename or "repository.zip"

    if Path(filename).suffix.lower() != ".zip":
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are supported."
        )

    try:
        contents = await file.read()

        if len(contents) > MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="ZIP file exceeds the 50 MB upload limit."
            )
        
        with TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            zip_path = temporary_path / "repository.zip"

            zip_path.write_bytes(contents)

            extraction_path = temporary_path / "extracted"
            extraction_path.mkdir()

            with ZipFile(zip_path) as archive:
                extract_zip_safely(archive, extraction_path)

            statistics = scan_repository(extraction_path)

            return {
                "filename": filename,
                **statistics
            }

    except BadZipFile as error:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid ZIP archive."
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error
    
    finally:
        await file.close()
    
def extract_zip_safely(archive: ZipFile, destination: Path) -> None:
    destination = destination.resolve()

    for member in archive.infolist():
        member_path = (destination / member.filename).resolve()

        if destination not in member_path.parents and member_path != destination:
            raise ValueError("ZIP archive contains an unsafe file path.")

    archive.extractall(destination)