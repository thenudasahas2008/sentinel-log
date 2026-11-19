import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.report import Report
from app.schemas.report import ReportGenerateRequest, ReportResponse
from app.services.report_service import ReportService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["Reporting Engine"])

@router.get("", response_model=List[ReportResponse])
def list_reports(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    return db.query(Report).order_by(Report.created_at.desc()).offset(offset).limit(limit).all()

@router.post("/generate", response_model=ReportResponse)
def generate_report(
    payload: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    report = ReportService.generate_report(
        db=db,
        title=payload.title,
        report_type=payload.report_type,
        format_type=payload.format,
        user_id=current_user.id if current_user else None,
        filters=payload.filters
    )
    return report

@router.get("/{report_uuid}/download")
def download_report(report_uuid: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.report_uuid == report_uuid).first()
    if not report or not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Report file not found")

    media_types = {
        "PDF": "application/pdf",
        "HTML": "text/html",
        "JSON": "application/json",
        "CSV": "text/csv"
    }
    media_type = media_types.get(report.format.upper(), "application/octet-stream")
    filename = os.path.basename(report.file_path)

    return FileResponse(
        path=report.file_path,
        media_type=media_type,
        filename=filename
    )
