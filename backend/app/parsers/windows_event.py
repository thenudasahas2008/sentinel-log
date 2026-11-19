import re
import json
import uuid
from typing import Optional, Dict, Any
from app.parsers.base import BaseLogParser

class WindowsEventLogParser(BaseLogParser):
    parser_name: str = "WINDOWS_SECURITY"

    # Known security event IDs
    EVENT_DESCRIPTIONS = {
        4624: ("An account was successfully logged on", "SUCCESS", "LOGIN"),
        4625: ("An account failed to log on", "FAILURE", "LOGIN"),
        4634: ("An account was logged off", "SUCCESS", "LOGOUT"),
        4648: ("A logon was attempted using explicit credentials", "INFO", "EXPLICIT_CREDENTIALS"),
        4672: ("Special privileges assigned to new logon", "SUCCESS", "PRIVILEGE_ESCALATION"),
        4720: ("A user account was created", "SUCCESS", "ACCOUNT_CREATION"),
        4726: ("A user account was deleted", "SUCCESS", "ACCOUNT_DELETION"),
        4740: ("A user account was locked out", "FAILURE", "ACCOUNT_LOCKOUT")
    }

    def parse_line(self, line: str, line_number: int = 0) -> Optional[Dict[str, Any]]:
        # Handle JSON exported windows events
        if line.strip().startswith("{") and line.strip().endswith("}"):
            try:
                data = json.loads(line)
                event_id = int(data.get("EventID") or data.get("event_id") or 0)
                timestamp = self.normalize_timestamp(data.get("TimeCreated") or data.get("timestamp"))
                
                # Extract event info
                info = self.EVENT_DESCRIPTIONS.get(event_id, ("Windows Security Event", "UNKNOWN", "WINDOWS_EVENT"))
                
                source_ip = self.normalize_ip(data.get("IpAddress") or data.get("SourceNetworkAddress") or data.get("source_ip"))
                username = data.get("TargetUserName") or data.get("SubjectUserName") or data.get("username")
                hostname = data.get("Computer") or data.get("hostname") or "WINDOWS-HOST"

                return {
                    "event_uuid": f"evt-{uuid.uuid4().hex[:16]}",
                    "timestamp": timestamp,
                    "source_ip": source_ip,
                    "source_port": int(data.get("IpPort")) if data.get("IpPort") and str(data["IpPort"]).isdigit() else None,
                    "destination_ip": None,
                    "destination_port": None,
                    "event_type": f"WIN_EVENT_{event_id}",
                    "action": info[2],
                    "status": info[1],
                    "username": username,
                    "hostname": hostname,
                    "service": "Security",
                    "raw_log": line,
                    "parser_type": self.parser_name,
                    "metadata_json": {
                        "event_id": event_id,
                        "description": info[0],
                        "logon_type": data.get("LogonType"),
                        "workstation": data.get("WorkstationName")
                    }
                }
            except Exception:
                pass

        # Text format: e.g. "Event 4625, Security: An account failed to log on. Account: Administrator, IP: 192.168.1.50"
        m_id = re.search(r'\b(?:Event\s*(?:ID)?\s*[:=]?\s*|462[45]|4672|4720)(\d{4})\b', line, re.IGNORECASE)
        event_id = int(m_id.group(1)) if m_id else (4625 if "fail" in line.lower() else (4624 if "success" in line.lower() else 0))
        
        info = self.EVENT_DESCRIPTIONS.get(event_id, ("Windows Security Event", "UNKNOWN", "WINDOWS_EVENT"))
        
        ip_match = re.search(r'(?:IP|Address|SourceNetworkAddress)[:=\s]+([0-9\.:a-fA-F]+)', line, re.IGNORECASE)
        source_ip = self.normalize_ip(ip_match.group(1)) if ip_match else None

        user_match = re.search(r'(?:Account|User|TargetUserName)[:=\s]+([a-zA-Z0-9_\-\.\$\\]+)', line, re.IGNORECASE)
        username = user_match.group(1).split("\\")[-1] if user_match else None

        ts_match = re.search(r'\b\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}', line)
        timestamp = self.normalize_timestamp(ts_match.group(0)) if ts_match else self.normalize_timestamp(line[:25])

        return {
            "event_uuid": f"evt-{uuid.uuid4().hex[:16]}",
            "timestamp": timestamp,
            "source_ip": source_ip,
            "source_port": None,
            "destination_ip": None,
            "destination_port": None,
            "event_type": f"WIN_EVENT_{event_id}",
            "action": info[2],
            "status": info[1],
            "username": username,
            "hostname": "WINDOWS-SERVER",
            "service": "Security",
            "raw_log": line,
            "parser_type": self.parser_name,
            "metadata_json": {
                "event_id": event_id,
                "description": info[0],
                "line_number": line_number
            }
        }
