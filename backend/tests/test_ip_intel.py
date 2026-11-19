from datetime import datetime
from app.models.event import SecurityEvent
from app.services.ip_service import IPIntelligenceService

def test_ip_intel_private_ip(db):
    res = IPIntelligenceService.inspect_ip(db, "192.168.1.1")
    assert res["is_valid"] is True
    assert res["is_private"] is True
    assert res["classification"] == "LOCAL_INTERNAL"

def test_ip_intel_external_with_history(db):
    now = datetime.utcnow()
    # Add some failed events
    for i in range(12):
        ev = SecurityEvent(
            event_uuid=f"e-intel-{i}",
            timestamp=now,
            source_ip="142.250.190.46",
            status="FAILURE",
            username="admin",
            event_type="SSH_AUTH",
            raw_log="fail",
            parser_type="SSH_AUTH"
        )
        db.add(ev)
    db.commit()

    res = IPIntelligenceService.inspect_ip(db, "142.250.190.46")
    assert res["is_valid"] is True
    assert res["is_private"] is False
    assert res["reputation_history"]["failed_attempts"] == 12
    assert res["threat_score"] > 0
