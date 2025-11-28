import os
import uuid
import aiofiles
from pathlib import Path
from typing import AsyncIterator

from fastapi import UploadFile, HTTPException, status

from app.core.config import settings


class LocalStorage:
    """Local file storage backend."""

    def __init__(self):
        self.base_path = Path(settings.UPLOAD_DIR)
        self._ensure_directories()

    def _ensure_directories(self):
        """Create upload directories if they don't exist."""
        (self.base_path / "lessons").mkdir(parents=True, exist_ok=True)
        (self.base_path / "submissions").mkdir(parents=True, exist_ok=True)

    def _get_allowed_extensions(self, file_type: str) -> set[str]:
        """Get allowed extensions for file type."""
        if file_type == "lessons":
            return set(settings.ALLOWED_LESSON_EXTENSIONS.split(","))
        elif file_type == "submissions":
            return set(settings.ALLOWED_SUBMISSION_EXTENSIONS.split(","))
        return set()

    def _validate_file(self, file: UploadFile, file_type: str) -> str:
        """Validate file and return extension."""
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required",
            )

        ext = Path(file.filename).suffix.lower()
        allowed = self._get_allowed_extensions(file_type)

        if ext not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {ext} not allowed. Allowed: {', '.join(allowed)}",
            )

        return ext

    def _generate_filename(self, original_filename: str) -> str:
        """Generate unique filename preserving extension."""
        ext = Path(original_filename).suffix.lower()
        return f"{uuid.uuid4()}{ext}"

    async def upload(
        self, file: UploadFile, file_type: str, entity_id: int
    ) -> str:
        """
        Upload file to local storage.

        Args:
            file: FastAPI UploadFile
            file_type: 'lessons' or 'submissions'
            entity_id: ID of lesson or submission

        Returns:
            Relative path to uploaded file
        """
        ext = self._validate_file(file, file_type)

        # Check file size by reading in chunks
        total_size = 0
        chunks = []

        while chunk := await file.read(1024 * 1024):  # 1 MB chunks
            total_size += len(chunk)
            if total_size > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE // (1024*1024)} MB",
                )
            chunks.append(chunk)

        # Generate unique filename
        filename = self._generate_filename(file.filename)
        relative_path = f"{file_type}/{entity_id}/{filename}"
        full_path = self.base_path / file_type / str(entity_id) / filename

        # Create entity directory
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        async with aiofiles.open(full_path, "wb") as f:
            for chunk in chunks:
                await f.write(chunk)

        return relative_path

    async def download(self, path: str) -> AsyncIterator[bytes]:
        """
        Stream file from local storage.

        Args:
            path: Relative path to file

        Yields:
            File chunks
        """
        full_path = self.base_path / path

        if not full_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )

        async with aiofiles.open(full_path, "rb") as f:
            while chunk := await f.read(1024 * 1024):  # 1 MB chunks
                yield chunk

    async def delete(self, path: str) -> None:
        """
        Delete file from local storage.

        Args:
            path: Relative path to file
        """
        full_path = self.base_path / path

        if full_path.exists():
            os.remove(full_path)

            # Remove parent directory if empty
            parent = full_path.parent
            if parent.exists() and not any(parent.iterdir()):
                parent.rmdir()

    def get_file_url(self, path: str) -> str:
        """Get URL for file download."""
        return f"/api/v1/files/{path}"

    def get_filename(self, path: str) -> str:
        """Extract original-style filename from path."""
        return Path(path).name


storage = LocalStorage()
