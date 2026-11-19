import os
from datetime import datetime
from app.models.alert import Alert
from app.services.report_service import ReportService

def test_report_generation_all_formats(db):
    # Add an alert
    alert = Alert(
        alert_uuid="alt-rep-test-01",
        rule_id="RULE-001",
        title="Test Incident Alert",
        category="BRUTE_FORCE",
        severity="HIGH",
        source_ip="198.51.100.1",
        target_username="root",
        timestamp=datetime.utcnow(),
        evidence={"failure_count": 10},
        detection_rule_name="SSH Brute Force",
        recommended_action="Block IP",
        confidence_score=0.91,
        status="NEW"
    )
    db.add(alert)
    db.commit()

    for fmt in ["JSON", "CSV", "HTML", "PDF"]:
        rep = ReportService.generate_report(
            db=db,
            title=f"Test {fmt} Report",
            report_type="INCIDENT",
            format_type=fmt
        )
        assert rep is not None
        assert os.path.exists(rep.file_path)
        assert rep.file_size_bytes > 0
        assert rep.format == fmt
