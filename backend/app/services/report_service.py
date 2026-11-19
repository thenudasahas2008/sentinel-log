import os
import json
import csv
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.models.event import SecurityEvent
from app.models.report import Report
from app.config import settings

# PDF generation using ReportLab
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class ReportService:
    @staticmethod
    def generate_report(
        db: Session,
        title: str,
        report_type: str = "INCIDENT",
        format_type: str = "PDF",
        user_id: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Report:
        format_clean = format_type.upper()
        report_uuid = f"rep-{uuid.uuid4().hex[:16]}"
        os.makedirs(settings.REPORTS_DIR, exist_ok=True)

        # Pull actual database results
        query = db.query(Alert)
        if filters:
            if filters.get("severity"):
                query = query.filter(Alert.severity == filters["severity"])
            if filters.get("category"):
                query = query.filter(Alert.category == filters["category"])
        
        alerts = query.order_by(Alert.timestamp.desc()).limit(100).all()
        events = db.query(SecurityEvent).order_by(SecurityEvent.timestamp.desc()).limit(200).all()

        file_extension = format_clean.lower()
        filename = f"{report_uuid}_{report_type.lower()}.{file_extension}"
        file_path = os.path.join(settings.REPORTS_DIR, filename)

        if format_clean == "JSON":
            ReportService._generate_json(file_path, title, report_type, alerts, events)
        elif format_clean == "CSV":
            ReportService._generate_csv(file_path, alerts)
        elif format_clean == "HTML":
            ReportService._generate_html(file_path, title, report_type, alerts, events)
        else:  # PDF
            ReportService._generate_pdf(file_path, title, report_type, alerts, events)

        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

        report_obj = Report(
            report_uuid=report_uuid,
            title=title,
            report_type=report_type,
            format=format_clean,
            file_path=file_path,
            file_size_bytes=file_size,
            parameters=filters,
            generated_by_id=user_id,
            created_at=datetime.utcnow()
        )
        db.add(report_obj)
        db.commit()
        db.refresh(report_obj)
        return report_obj

    @staticmethod
    def _generate_json(path: str, title: str, report_type: str, alerts: List[Alert], events: List[SecurityEvent]):
        data = {
            "metadata": {
                "title": title,
                "report_type": report_type,
                "generated_at": datetime.utcnow().isoformat(),
                "total_alerts": len(alerts),
                "total_events_sample": len(events)
            },
            "alerts": [
                {
                    "alert_uuid": a.alert_uuid,
                    "rule_id": a.rule_id,
                    "title": a.title,
                    "severity": a.severity,
                    "category": a.category,
                    "source_ip": a.source_ip,
                    "target_username": a.target_username,
                    "timestamp": a.timestamp.isoformat(),
                    "confidence_score": a.confidence_score,
                    "recommended_action": a.recommended_action,
                    "evidence": a.evidence
                }
                for a in alerts
            ]
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def _generate_csv(path: str, alerts: List[Alert]):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Alert ID", "Rule ID", "Title", "Severity", "Category",
                "Source IP", "Target User", "Timestamp", "Confidence", "Status"
            ])
            for a in alerts:
                writer.writerow([
                    a.alert_uuid, a.rule_id, a.title, a.severity, a.category,
                    a.source_ip or "", a.target_username or "",
                    a.timestamp.isoformat(), a.confidence_score, a.status
                ])

    @staticmethod
    def _generate_html(path: str, title: str, report_type: str, alerts: List[Alert], events: List[SecurityEvent]):
        critical_count = sum(1 for a in alerts if a.severity == "CRITICAL")
        high_count = sum(1 for a in alerts if a.severity == "HIGH")
        medium_count = sum(1 for a in alerts if a.severity == "MEDIUM")
        
        rows = "".join(f"""
        <tr>
            <td><strong>{a.alert_uuid[:12]}</strong></td>
            <td><span class="badge {a.severity.lower()}">{a.severity}</span></td>
            <td>{a.title}</td>
            <td><code>{a.source_ip or 'N/A'}</code></td>
            <td>{a.target_username or 'N/A'}</td>
            <td>{a.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</td>
            <td>{int(a.confidence_score * 100)}%</td>
        </tr>
        """ for a in alerts[:50])

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title} — SentinelLog Intelligence Dossier</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0b0f19; color: #e2e8f0; margin: 0; padding: 40px; }}
        .header {{ border-bottom: 2px solid #06b6d4; padding-bottom: 20px; margin-bottom: 30px; }}
        h1 {{ color: #06b6d4; margin: 0 0 10px 0; font-size: 28px; }}
        .meta {{ color: #94a3b8; font-size: 14px; }}
        .kpi-container {{ display: flex; gap: 20px; margin-bottom: 30px; }}
        .kpi-card {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 20px; flex: 1; }}
        .kpi-val {{ font-size: 32px; font-weight: bold; margin-top: 5px; }}
        .kpi-val.crit {{ color: #ef4444; }}
        .kpi-val.high {{ color: #f97316; }}
        .kpi-val.med {{ color: #eab308; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: #1e293b; border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #334155; font-size: 14px; }}
        th {{ background: #0f172a; color: #38bdf8; text-transform: uppercase; font-size: 12px; letter-spacing: 0.05em; }}
        .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase; }}
        .badge.critical {{ background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid #ef4444; }}
        .badge.high {{ background: rgba(249, 115, 22, 0.2); color: #fdba74; border: 1px solid #f97316; }}
        .badge.medium {{ background: rgba(234, 179, 8, 0.2); color: #fde047; border: 1px solid #eab308; }}
        .badge.low {{ background: rgba(59, 130, 246, 0.2); color: #93c5fd; border: 1px solid #3b82f6; }}
        code {{ background: #0f172a; padding: 2px 6px; border-radius: 4px; color: #22d3ee; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SENTINELLOG // SECURITY INTELLIGENCE DOSSIER</h1>
        <div class="meta">{title} &bull; Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} &bull; Classification: RESTRICTED SOC REPORT</div>
    </div>

    <div class="kpi-container">
        <div class="kpi-card">
            <div class="meta">CRITICAL ALERTS</div>
            <div class="kpi-val crit">{critical_count}</div>
        </div>
        <div class="kpi-card">
            <div class="meta">HIGH SEVERITY</div>
            <div class="kpi-val high">{high_count}</div>
        </div>
        <div class="kpi-card">
            <div class="meta">MEDIUM SEVERITY</div>
            <div class="kpi-val med">{medium_count}</div>
        </div>
        <div class="kpi-card">
            <div class="meta">TOTAL ANALYZED</div>
            <div class="kpi-val">{len(alerts)}</div>
        </div>
    </div>

    <h2>Verified Threat Detections</h2>
    <table>
        <thead>
            <tr>
                <th>Alert ID</th>
                <th>Severity</th>
                <th>Title</th>
                <th>Source IP</th>
                <th>Target Account</th>
                <th>Timestamp</th>
                <th>Confidence</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
</body>
</html>"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)

    @staticmethod
    def _generate_pdf(path: str, title: str, report_type: str, alerts: List[Alert], events: List[SecurityEvent]):
        doc = SimpleDocTemplate(path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#0f172a')
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor('#64748b'),
            leading=14
        )
        h2_style = ParagraphStyle(
            'H2',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#1e293b')
        )
        cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10
        )

        elements = []
        elements.append(Paragraph("SENTINELLOG // SECURITY INTELLIGENCE DOSSIER", title_style))
        elements.append(Paragraph(f"{title} | Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", subtitle_style))
        elements.append(Spacer(1, 15))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#06b6d4'), spaceAfter=15))

        # Executive Summary Table
        crit = sum(1 for a in alerts if a.severity == "CRITICAL")
        high = sum(1 for a in alerts if a.severity == "HIGH")
        med = sum(1 for a in alerts if a.severity == "MEDIUM")
        
        kpi_data = [
            ["Metric", "Count", "Severity Assessment"],
            ["Critical Threats Detected", str(crit), "Immediate Remediation Required" if crit > 0 else "Nominal"],
            ["High Severity Detections", str(high), "Active Investigation Underway" if high > 0 else "Nominal"],
            ["Medium Severity Anomalies", str(med), "Routine SOC Review"],
            ["Total Correlated Incidents", str(len(alerts)), "Security Monitoring Active"]
        ]
        kpi_table = Table(kpi_data, colWidths=[180, 80, 280])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 20))

        # Incident Detections Table
        elements.append(Paragraph("Key Incident Detections & Evidence", h2_style))
        elements.append(Spacer(1, 10))

        table_data = [
            ["Alert ID", "Severity", "Threat Title", "Source IP", "Target", "Confidence"]
        ]
        for a in alerts[:25]:
            table_data.append([
                Paragraph(a.alert_uuid[:12], cell_style),
                Paragraph(a.severity, cell_style),
                Paragraph(a.title[:45], cell_style),
                Paragraph(a.source_ip or "N/A", cell_style),
                Paragraph(a.target_username or "N/A", cell_style),
                Paragraph(f"{int(a.confidence_score * 100)}%", cell_style)
            ])

        table = Table(table_data, colWidths=[70, 60, 200, 85, 75, 50])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')])
        ]))
        elements.append(table)

        doc.build(elements)
