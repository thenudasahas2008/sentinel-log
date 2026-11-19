import json
import uuid
from typing import Optional, Dict, Any
from app.parsers.base import BaseLogParser

class JSONLogParser(BaseLogParser):
    parser_name: str = "JSON_LOG"

    def parse_line(self, line: str, line_number: int = 0) -> Optional[Dict[str, Any]]:
        try:
            doc = json.loads(line)
        except Exception:
            return None

        if not isinstance(doc, dict):
            return None

        # Auto-detect timestamp keys
        raw_ts = (
            doc.get("timestamp") or doc.get("@timestamp") or doc.get("time") or
            doc.get("date") or doc.get("event_time") or doc.get("created_at")
        )
        timestamp = self.normalize_timestamp(raw_ts)

        # Auto-detect IP keys
        raw_ip = (
            doc.get("source_ip") or doc.get("src_ip") or doc.get("ip") or
            doc.get("client_ip") or doc.get("remote_addr") or doc.get("sourceIp")
        )
        source_ip = self.normalize_ip(str(raw_ip)) if raw_ip else None

        # Auto-detect user keys
        username = (
            doc.get("username") or doc.get("user") or doc.get("account") or
            doc.get("target_user") or doc.get("user_id") or doc.get("userName")
        )
        if username is not None:
            username = str(username)

        # Status
        raw_status = str(doc.get("status") or doc.get("result") or doc.get("outcome") or "").upper()
        if "FAIL" in raw_status or "ERR" in raw_status or "DENI" in raw_status:
            status = "FAILURE"
        elif "SUCC" in raw_status or "OK" in raw_status or "ALLOW" in raw_status:
            status = "SUCCESS"
        else:
            status = "UNKNOWN"

        action = str(doc.get("action") or doc.get("event_type") or doc.get("event") or "SECURITY_EVENT").upper()
        event_type = str(doc.get("type") or doc.get("log_type") or "JSON_EVENT")
        hostname = str(doc.get("hostname") or doc.get("host") or doc.get("node") or "unknown")

        return {
            "event_uuid": f"evt-{uuid.uuid4().hex[:16]}",
            "timestamp": timestamp,
            "source_ip": source_ip,
            "source_port": doc.get("source_port") or doc.get("src_port"),
            "destination_ip": self.normalize_ip(doc.get("destination_ip") or doc.get("dst_ip")),
            "destination_port": doc.get("destination_port") or doc.get("dst_port"),
            "event_type": event_type,
            "action": action,
            "status": status,
            "username": username,
            "hostname": hostname,
            "service": doc.get("service") or doc.get("app"),
            "raw_log": line,
            "parser_type": self.parser_name,
            "metadata_json": {k: v for k, v in doc.items() if k not in ["raw_log", "line"]}
        }
