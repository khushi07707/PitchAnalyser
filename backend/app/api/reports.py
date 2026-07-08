import uuid
import os
import logging
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.report import Report
from app.models.upload import Upload
from app.core.exceptions import NotFoundException
from app.utils.pdf import generate_pdf_report

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Report History"])

@router.get("")
def get_reports(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve user's paginated list of reports.
    Supports optional keyword search on filenames.
    """
    query = db.query(Report).join(Upload, Report.upload_id == Upload.id).filter(Report.user_id == current_user.id)
    
    if search:
        query = query.filter(Upload.filename.ilike(f"%{search}%"))
        
    total_count = query.count()
    
    offset = (page - 1) * limit
    reports = query.order_by(Report.created_at.desc()).offset(offset).limit(limit).all()
    
    items = []
    for r in reports:
        items.append({
            "report_id": r.id,
            "upload_id": r.upload_id,
            "filename": r.upload.filename,
            "overall_score": float(r.overall_score),
            "duration": float(r.upload.duration or 0.0),
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
        
    return {
        "items": items,
        "total": int(total_count),
        "page": int(page),
        "limit": int(limit),
        "pages": int((total_count + limit - 1) // limit)
    }

@router.get("/{report_id}")
def get_report_detail(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get full analysis report results for a given report ID.
    Includes scores, audio metrics, transcribed segments, and recommendations.
    """
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == current_user.id).first()
    if not report:
        raise NotFoundException("Analysis report not found or access denied.")
        
    upload = report.upload
    transcript = upload.transcript
    analysis = upload.analysis_result
    feedback = upload.feedback
    
    return {
        "report_id": report.id,
        "upload_id": report.upload_id,
        "filename": upload.filename,
        "duration": float(upload.duration or 0.0),
        "file_size": int(upload.file_size),
        "mime_type": upload.mime_type,
        "status": upload.status,
        "created_at": report.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        
        "scores": {
            "clarity_score": float(report.clarity_score),
            "confidence_score": float(report.confidence_score),
            "engagement_score": float(report.engagement_score),
            "communication_score": float(report.communication_score),
            "voice_quality_score": float(report.voice_quality_score),
            "overall_score": float(report.overall_score)
        },
        
        "transcript": {
            "full_text": transcript.full_text,
            "language": transcript.language,
            "words": transcript.words_json,
            "sentences": transcript.sentences_json
        } if transcript else None,
        
        "analysis": {
            "speaking_rate": float(analysis.speaking_rate),
            "pitch_mean": float(analysis.pitch_mean),
            "pitch_stability": float(analysis.pitch_stability),
            "energy": float(analysis.energy),
            "pauses_count": int(analysis.pauses_count),
            "silence_duration": float(analysis.silence_duration),
            "voice_modulation": float(analysis.voice_modulation),
            "speaking_style": analysis.speaking_style,
            "filler_words": analysis.filler_words,
            "repeated_words": analysis.repeated_words,
            "grammar_issues": analysis.grammar_issues,
            "sentiment_polarity": float(analysis.sentiment_polarity),
            "sentiment_subjectivity": float(analysis.sentiment_subjectivity),
            "keywords": analysis.keywords,
            "confidence_indicators": analysis.confidence_indicators
        } if analysis else None,
        
        "feedback": {
            "strengths": feedback.strengths,
            "weaknesses": feedback.weaknesses,
            "suggestions": feedback.suggestions,
            "overall_review": feedback.overall_review,
            "presentation_tips": feedback.presentation_tips,
            "communication_tips": feedback.communication_tips,
            "confidence_tips": feedback.confidence_tips
        } if feedback else None
    }

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permanently deletes a report.
    Deletes the local media file from disk, and cascades DB deletion.
    """
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == current_user.id).first()
    if not report:
        raise NotFoundException("Analysis report not found or access denied.")
        
    upload = report.upload
    
    # 1. Delete file from local uploads folder
    if upload and os.path.exists(upload.filepath):
        try:
            logger.info(f"Removing media file from disk: {upload.filepath}")
            os.remove(upload.filepath)
        except Exception as e:
            logger.warning(f"Could not delete media file at {upload.filepath}: {str(e)}")
            
    # 2. Deleting the upload cascade deletes child records
    db.delete(upload)
    db.commit()
    logger.info(f"Cascade deletion of report {report_id} completed successfully.")
    return

@router.get("/{report_id}/download")
def download_pdf(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generates and returns the PDF pitch evaluation report file as a streaming download."""
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == current_user.id).first()
    if not report:
        raise NotFoundException("Analysis report not found or access denied.")
        
    upload = report.upload
    transcript = upload.transcript
    feedback = upload.feedback
    
    report_data = {
        "filename": upload.filename,
        "created_at": report.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "clarity_score": float(report.clarity_score),
        "confidence_score": float(report.confidence_score),
        "engagement_score": float(report.engagement_score),
        "communication_score": float(report.communication_score),
        "voice_quality_score": float(report.voice_quality_score),
        "overall_score": float(report.overall_score),
        "transcript": transcript.full_text if transcript else "",
        "overall_review": feedback.overall_review if feedback else "",
        "strengths": feedback.strengths if feedback else [],
        "weaknesses": feedback.weaknesses if feedback else [],
        "suggestions": feedback.suggestions if feedback else []
    }
    
    # Generate the streaming buffer
    pdf_buffer = generate_pdf_report(report_data)
    
    filename = f"PitchPilot_Report_{report_id}.pdf"
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
