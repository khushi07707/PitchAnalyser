import os
import uuid
import shutil
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.config.config import settings
from app.models.upload import Upload
from app.core.exceptions import FileTooLargeException, InvalidFileFormatException

# Allowed audio/video extensions
ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a", "mp4", "mov"}

class FileService:
    @staticmethod
    def validate_file(file: UploadFile):
        """Validate that the file format is allowed and file size doesn't exceed limit."""
        filename = file.filename or ""
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise InvalidFileFormatException(
                f"Unsupported file format: .{ext}. Supported formats are: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
        
        # Find file size by reading/seeking
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)  # Reset pointer to start of file
        
        max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if size > max_size:
            raise FileTooLargeException(f"File size exceeds the maximum limit of {settings.MAX_FILE_SIZE_MB}MB.")
        
        return size, ext

    @staticmethod
    def save_upload(db: Session, file: UploadFile, user_id: uuid.UUID) -> Upload:
        """Validate, save file to local disk, and register upload metadata in database."""
        size, ext = FileService.validate_file(file)
        
        # Ensure target folder exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Generate unique local filename
        unique_name = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(settings.UPLOAD_DIR, unique_name)
        
        # Copy file content to disk
        try:
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise Exception(f"Failed to write file to local disk: {str(e)}")
            
        # Register upload in DB
        db_upload = Upload(
            user_id=user_id,
            filename=file.filename or unique_name,
            filepath=filepath,
            file_size=size,
            mime_type=file.content_type or f"audio/{ext}",
            status="pending"
        )
        db.add(db_upload)
        db.commit()
        db.refresh(db_upload)
        
        return db_upload
