import os
import shutil
import hashlib
from pathlib import Path
from fastapi import UploadFile, HTTPException
from config import settings
from loguru import logger


ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # bytes


def validate_file(file: UploadFile) -> None:
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Supported: PDF, DOCX"
        )


async def save_upload_file(file: UploadFile, subfolder: str = "") -> tuple[str, float]:
    upload_dir = Path(settings.UPLOAD_DIR) / subfolder
    upload_dir.mkdir(parents=True, exist_ok=True)

    contents = await file.read()
    file_size = len(contents)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB"
        )

    # Generate unique filename
    file_hash = hashlib.md5(contents).hexdigest()[:8]
    ext = Path(file.filename).suffix.lower()
    safe_name = Path(file.filename).stem.replace(" ", "_")[:50]
    unique_filename = f"{safe_name}_{file_hash}{ext}"
    file_path = upload_dir / unique_filename

    with open(file_path, "wb") as f:
        f.write(contents)

    size_kb = file_size / 1024
    logger.info(f"Saved file: {file_path} ({size_kb:.1f} KB)")
    return str(file_path), size_kb


def delete_file(file_path: str) -> bool:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to delete {file_path}: {e}")
        return False
