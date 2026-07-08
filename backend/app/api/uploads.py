from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user
from app.schemas.upload import UploadResponse
from app.services.file_service import FileService
from app.models.user import User

router = APIRouter(prefix="/uploads", tags=["File Upload"])

@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload an audio or video file (MP3, WAV, M4A, MP4, MOV) up to 100MB.
    Registers metadata in the database and stores the file locally.
    """
    return FileService.save_upload(db, file, current_user.id)
