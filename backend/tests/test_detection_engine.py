from datetime import datetime, timedelta
from app.models.event import SecurityEvent
from app.engine.detector import DetectionEngine
from app.engine.rules.brute_force import SSHBruteForceRule
from app.engine.rules.password_spray import PasswordSprayingRule
from app.engine.rules.login_after_failures import LoginAfterFailuresRule
from app.engine.scoring import ConfidenceScorer

def test_confidence_scorer_deterministic():
    score = ConfidenceScorer.calculate_confidence(
        base_rule_confidence=0.85,
        failure_count=15,
        distinct_users=1,
        is_critical_account=True,
        is_external_ip=True,
        velocity_per_minute=5.0
    )
    assert 0.85 <= score <= 0.99

def test_ssh_brute_force_rule():
    rule = SSHBruteForceRule()
    now = datetime.utcnow()
    events = [
        SecurityEvent(
            event_uuid=f"e-{i}",
            timestamp=now + timedelta(seconds=i * 10),
            source_ip="198.51.100.77",
            status="FAILURE",
            username="admin",
            raw_log="fail",
            parser_type="SSH_AUTH"
        )
        for i in range(8)
    ]
    alerts = rule.evaluate(events)
    assert len(alerts) >= 1
    assert alerts[0]["rule_id"] == "RULE-001"
    assert alerts[0]["source_ip"] == "198.51.100.77"
    assert alerts[0]["confidence_score"] > 0.80

def test_password_spraying_rule():
    rule = PasswordSprayingRule()
    now = datetime.utcnow()
    users = ["alice", "bob", "charlie", "david"]
    events = [
        SecurityEvent(
            event_uuid=f"e-spray-{i}",
            timestamp=now + timedelta(seconds=i * 20),
            source_ip="203.0.113.99",
            status="FAILURE",
            username=u,
            raw_log="fail",
            parser_type="SSH_AUTH"
        )
        for i, u in enumerate(users)
    ]
    alerts = rule.evaluate(events)
    assert len(alerts) >= 1
    assert alerts[0]["rule_id"] == "RULE-002"
    assert "distinct_user_count" in alerts[0]["evidence"]

def test_login_after_failures_rule():
    rule = LoginAfterFailuresRule()
    now = datetime.utcnow()
    events = [
        SecurityEvent(
            event_uuid=f"e-fail-{i}",
            timestamp=now + timedelta(seconds=i * 15),
            source_ip="45.142.195.22",
            status="FAILURE",
            username="finance_lead",
            raw_log="fail",
            parser_type="SSH_AUTH"
        )
        for i in range(4)
    ]
    # Followed by success
    events.append(
        SecurityEvent(
            event_uuid="e-succ-1",
            timestamp=now + timedelta(seconds=70),
            source_ip="45.142.195.22",
            status="SUCCESS",
            username="finance_lead",
            raw_log="accepted",
            parser_type="SSH_AUTH"
        )
    )
    alerts = rule.evaluate(events)
    assert len(alerts) >= 1
    assert alerts[0]["rule_id"] == "RULE-005"
    assert alerts[0]["severity"] == "CRITICAL"
