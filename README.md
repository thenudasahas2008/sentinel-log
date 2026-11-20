# SentinelLog — Advanced Security Log Intelligence Platform

SentinelLog is a production-grade Security Information and Event Management (SIEM) and log intelligence platform engineered for modern Security Operations Centers (SOC). It provides real-time detection rule evaluation, multi-format log ingestion, WebSocket telemetry streaming, and forensic investigation workflows.

---

## Key Features

- **10 Core Threat Detection Rules**:
  - SSH Brute-Force attack detection
  - Password Spraying across corporate identities
  - Credential Stuffing indicators
  - Repeated authentication failures with severity escalation
  - Successful authentication immediately following repeated failures
  - Off-hours / anomalous login time detection
  - Multi-source IP account access
  - Impossible Travel velocity analysis
  - Privileged root/admin account anomalies
  - Suspicious authentication patterns
- **Multi-Format Log Parser**: Supports Linux `auth.log`, RFC 5424 Syslog, Nginx/Apache access logs, Windows Security Event CSVs, and structured JSON logs.
- **SOC Investigation Engine**: Incident triage, evidence inspection, analyst note taking, and alert status transitions.
- **Reporting System**: Generates executive forensic summaries and data export in JSON, HTML, and CSV formats.
- **Modern Full-Stack Architecture**: Python FastAPI backend with SQLAlchemy 2 + React 18, TypeScript, Tailwind CSS, Lucide icons, and Recharts.

---

## Quick Start

### 1. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Linux: source venv/bin/activate
pip install -r ../requirements.txt

# Seed demonstration data
python seed.py

# Launch API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be available at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Dashboard will be accessible at `http://localhost:5173`.

---

## Automated Testing

```bash
# Run backend test suite (21 unit and integration tests)
pytest -v tests
```

---

## Architecture

```
sentinel-log/
├── backend/
│   ├── app/
│   │   ├── api/v1/         # REST API endpoints (Auth, Ingestion, Alerts, Reports)
│   │   ├── core/           # Security configuration, JWT, Argon2 hashing
│   │   ├── detection/      # 10 Real-time threat detection rule engines
│   │   ├── models/         # SQLAlchemy database models
│   │   ├── parsers/        # Linux, Syslog, Apache/Nginx, Windows event parsers
│   │   └── services/       # Reporting, investigation, and IP intelligence services
├── frontend/
│   ├── src/
│   │   ├── components/     # SOC Dashboard, Alert cards, Timeline charts
│   │   ├── contexts/       # WebSocket live telemetry provider
│   │   └── pages/          # Dashboard, Explorer, Investigations, Reports
└── tests/                  # Automated pytest test cases
```
