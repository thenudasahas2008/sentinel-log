import os
import uuid
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.event import SecurityEvent
from app.models.import_history import ImportHistory
from app.parsers import detect_parser_from_filename_or_content, get_parser
from app.engine.detector import DetectionEngine
from app.services.audit_service import AuditService
from app.config import settings
from app.utils.logging import logger

router = APIRouter(prefix="/ingestion", tags=["Log Ingestion"])

@router.post("/upload")
async def upload_log_file(
    file: UploadFile = File(...),
    parser_type: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    batch_id = f"batch-{uuid.uuid4().hex[:12]}"
    temp_path = os.path.join(settings.UPLOAD_DIR, f"{batch_id}_{file.filename}")

    try:
        # Stream file to disk to handle large uploads safely
        file_size = 0
        with open(temp_path, "wb") as buffer:
            while chunk := await file.read(65536):
                file_size += len(chunk)
                if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
                    buffer.close()
                    os.remove(temp_path)
                    raise HTTPException(status_code=400, detail="File exceeds maximum allowed size (50MB)")
                buffer.write(chunk)

        # Check duplicate hash
        from app.parsers.base import BaseLogParser
        file_hash = BaseLogParser.compute_hash(temp_path)
        existing = db.query(ImportHistory).filter(ImportHistory.file_hash == file_hash).first()
        if existing:
            # File already ingested
            os.remove(temp_path)
            return {
                "status": "DUPLICATE_SKIPPED",
                "message": f"File previously processed in batch {existing.batch_id} on {existing.created_at}",
                "batch_id": existing.batch_id,
                "total_records": existing.total_records
            }

        # Select parser
        if parser_type and parser_type.upper() in ["SSH_AUTH", "SYSLOG", "JSON_LOG", "CSV_LOG", "WINDOWS_SECURITY", "APACHE_ACCESS", "NGINX_ACCESS"]:
            parser = get_parser(parser_type)
        else:
            with open(temp_path, "r", encoding="utf-8", errors="ignore") as f:
                sample_text = f.read(2048)
            parser = detect_parser_from_filename_or_content(file.filename, sample_text)

        # Stream parse events
        events_to_create = []
        successful_records = 0
        failed_records = 0
        error_details = []

        for record in parser.parse_file(temp_path):
            try:
                ev = SecurityEvent(
                    event_uuid=record["event_uuid"],
                    timestamp=record["timestamp"],
                    source_ip=record["source_ip"],
                    source_port=record["source_port"],
                    destination_ip=record["destination_ip"],
                    destination_port=record["destination_port"],
                    event_type=record["event_type"],
                    action=record["action"],
                    status=record["status"],
                    username=record["username"],
                    hostname=record["hostname"],
                    service=record["service"],
                    raw_log=record["raw_log"],
                    parser_type=parser.parser_name,
                    import_batch_id=batch_id,
                    is_synthetic=False,
                    metadata_json=record["metadata_json"]
                )
                events_to_create.append(ev)
                successful_records += 1
            except Exception as ex:
                failed_records += 1
                if len(error_details) < 10:
                    error_details.append(str(ex))

        # Batch insert events
        if events_to_create:
            db.add_all(events_to_create)
            db.commit()

        # Run real-time detection engine over the newly ingested events!
        detector = DetectionEngine()
        created_alerts = detector.process_and_persist(db, events_to_create, is_synthetic=False)

        # Record import history
        history = ImportHistory(
            batch_id=batch_id,
            filename=file.filename,
            file_hash=file_hash,
            file_size_bytes=file_size,
            parser_used=parser.parser_name,
            total_records=successful_records + failed_records,
            successful_records=successful_records,
            failed_records=failed_records,
            error_summary={"samples": error_details} if error_details else None,
            status="COMPLETED"
        )
        db.add(history)
        db.commit()

        return {
            "status": "SUCCESS",
            "batch_id": batch_id,
            "filename": file.filename,
            "parser_used": parser.parser_name,
            "successful_records": successful_records,
            "failed_records": failed_records,
            "alerts_generated": len(created_alerts)
        }

    except Exception as e:
        logger.error(f"Ingestion failure: {str(e)}", exc_info=True)
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.get("/history")
def get_import_history(db: Session = Depends(get_db)):
    return db.query(ImportHistory).order_by(ImportHistory.created_at.desc()).limit(50).all()
