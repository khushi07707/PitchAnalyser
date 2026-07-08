import uuid
from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user
from app.services.report_service import ReportService
from app.models.user import User
from app.models.upload import Upload
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter(prefix="/analysis", tags=["AI Speech Analysis"])

@router.post("/process/{upload_id}", status_code=status.HTTP_202_ACCEPTED)
def process_pitch(
    upload_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Triggers AI and DSP analysis of the uploaded audio/video recording.
    Runs asynchronously in the background. Returns immediately.
    """
    upload = db.query(Upload).filter(Upload.id == upload_id, Upload.user_id == current_user.id).first()
    if not upload:
        raise NotFoundException("Recording upload not found or access denied.")
    
    if upload.status in ["processing", "completed"]:
        raise BadRequestException(f"Analysis pipeline is already {upload.status} for this recording.")
    
    # Delegate to FastAPI background task processor
    background_tasks.add_task(ReportService.process_and_generate_report, db, upload.id)
    
    return {
        "message": "AI analysis pipeline started successfully.",
        "upload_id": upload.id,
        "status": "processing"
    }

@router.get("/status/{upload_id}")
def check_status(
    upload_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check the current processing status of an upload.
    Returns: 'pending', 'processing', 'completed', or 'failed'.
    """
    upload = db.query(Upload).filter(Upload.id == upload_id, Upload.user_id == current_user.id).first()
    if not upload:
        raise NotFoundException("Recording upload not found or access denied.")
    
    return {
        "upload_id": upload.id,
        "status": upload.status
    }
