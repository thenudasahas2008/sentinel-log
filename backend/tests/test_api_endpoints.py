import os

def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"

def test_auth_login_success(client):
    res = client.post("/api/v1/auth/login", json={"username": "testadmin", "password": "TestSecret123!"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "ADMIN"

def test_auth_login_invalid_password(client):
    res = client.post("/api/v1/auth/login", json={"username": "testadmin", "password": "WrongPassword!"})
    assert res.status_code == 401

def test_dashboard_stats_endpoint(client):
    res = client.get("/api/v1/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_events" in data
    assert "critical_alerts" in data
    assert "timeline" in data

def test_demo_generate_and_reset(client):
    gen_res = client.post("/api/v1/demo/generate")
    assert gen_res.status_code == 200
    assert gen_res.json()["is_synthetic"] is True

    # Check alerts were populated
    alerts_res = client.get("/api/v1/alerts")
    assert alerts_res.status_code == 200
    assert len(alerts_res.json()) > 0

    # Reset demo
    reset_res = client.post("/api/v1/demo/reset")
    assert reset_res.status_code == 200
    assert reset_res.json()["status"] == "SUCCESS"

def test_file_ingestion_upload(client):
    sample_content = b"Nov 20 02:10:01 bastion sshd[10201]: Failed password for invalid user admin from 198.51.100.42 port 49152 ssh2\n"
    files = {"file": ("test_auth.log", sample_content, "text/plain")}
    res = client.post("/api/v1/ingestion/upload", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["successful_records"] == 1
