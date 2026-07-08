from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.report import Report
from app.models.upload import Upload

router = APIRouter(prefix="/dashboard", tags=["Dashboard Metrics"])

@router.get("/stats")
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get general user statistics for the dashboard cards:
    - Total Uploads count
    - Total reports count
    - Average overall score
    - Highest overall score
    """
    total_uploads = db.query(func.count(Upload.id)).filter(Upload.user_id == current_user.id).scalar() or 0
    reports_count = db.query(func.count(Report.id)).filter(Report.user_id == current_user.id).scalar() or 0
    avg_score = db.query(func.avg(Report.overall_score)).filter(Report.user_id == current_user.id).scalar() or 0.0
    max_score = db.query(func.max(Report.overall_score)).filter(Report.user_id == current_user.id).scalar() or 0.0

    return {
        "total_uploads": int(total_uploads),
        "total_reports": int(reports_count),
        "average_score": round(float(avg_score), 1),
        "highest_score": round(float(max_score), 1)
    }

@router.get("/performance")
def get_performance_trend(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve performance trend (overall scores over time)
    ordered ascendingly by creation date.
    """
    reports = db.query(Report.created_at, Report.overall_score)\
                .filter(Report.user_id == current_user.id)\
                .order_by(Report.created_at.asc())\
                .all()
                
    return [
        {
            "date": r.created_at.strftime("%Y-%m-%d"), 
            "score": float(r.overall_score)
        } for r in reports
    ]

@router.get("/recent")
def get_recent_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the 5 most recent completed reports for user quick links."""
    reports = db.query(Report)\
                .join(Upload, Report.upload_id == Upload.id)\
                .filter(Report.user_id == current_user.id)\
                .order_by(Report.created_at.desc())\
                .limit(5)\
                .all()
                
    recent = []
    for r in reports:
        recent.append({
            "report_id": r.id,
            "filename": r.upload.filename,
            "overall_score": float(r.overall_score),
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "duration": float(r.upload.duration or 0.0)
        })
    return recent

@router.get("/user-stats")
def get_user_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get aggregated averages for all 5 individual scoring dimensions."""
    dims = db.query(
        func.avg(Report.clarity_score).label("clarity"),
        func.avg(Report.confidence_score).label("confidence"),
        func.avg(Report.engagement_score).label("engagement"),
        func.avg(Report.communication_score).label("communication"),
        func.avg(Report.voice_quality_score).label("voice_quality")
    ).filter(Report.user_id == current_user.id).first()
    
    return {
        "clarity": round(float(dims.clarity or 0.0), 1),
        "confidence": round(float(dims.confidence or 0.0), 1),
        "engagement": round(float(dims.engagement or 0.0), 1),
        "communication": round(float(dims.communication or 0.0), 1),
        "voice_quality": round(float(dims.voice_quality or 0.0), 1)
    }
