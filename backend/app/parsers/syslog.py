import re
import uuid
from typing import Optional, Dict, Any
from app.parsers.base import BaseLogParser

class SyslogParser(BaseLogParser):
    parser_name: str = "SYSLOG"

    # RFC 3164: <PRI>TIMESTAMP HOSTNAME TAG: MESSAGE
    # RFC 5424: <PRI>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID STRUCTURED-DATA MSG
    RFC3164_PATTERN = re.compile(
        r'^(?:<(?P<pri>\d+)>)?(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+\d+:\d+:\d+)\s+(?P<hostname>\S+)\s+(?P<service>[a-zA-Z0-9_\-\.\/]+)(?:\[(?P<pid>\d+)\])?:\s+(?P<message>.*)$'
    )
    RFC5424_PATTERN = re.compile(
        r'^<(?P<pri>\d+)>(?P<version>\d+)\s+(?P<timestamp>\S+)\s+(?P<hostname>\S+)\s+(?P<service>\S+)\s+(?P<pid>\S+)\s+(?P<msgid>\S+)\s+(?P<message>.*)$'
    )

    def parse_line(self, line: str, line_number: int = 0) -> Optional[Dict[str, Any]]:
        data = None
        match = self.RFC5424_PATTERN.match(line)
        if match:
            data = match.groupdict()
        else:
            match = self.RFC3164_PATTERN.match(line)
            if match:
                data = match.groupdict()

        if not data:
            return None

        message = data.get("message", "")
        timestamp = self.normalize_timestamp(data.get("timestamp"))
        hostname = data.get("hostname", "unknown")
        service = data.get("service", "syslog")

        # Extract possible IP from message
        ip_match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', message)
        source_ip = self.normalize_ip(ip_match.group(0)) if ip_match else None

        # Extract possible user from message
        user_match = re.search(r'\b(?:user|for|account)\s+([a-zA-Z0-9_\-\.]+)', message, re.IGNORECASE)
        username = user_match.group(1) if user_match else None

        status = "UNKNOWN"
        msg_lower = message.lower()
        if any(w in msg_lower for w in ["fail", "error", "denied", "invalid", "refused", "rejected"]):
            status = "FAILURE"
        elif any(w in msg_lower for w in ["success", "accepted", "established", "authenticated", "ok"]):
            status = "SUCCESS"

        return {
            "event_uuid": f"evt-{uuid.uuid4().hex[:16]}",
            "timestamp": timestamp,
            "source_ip": source_ip,
            "source_port": None,
            "destination_ip": None,
            "destination_port": None,
            "event_type": "SYSLOG",
            "action": "SYSTEM_EVENT",
            "status": status,
            "username": username,
            "hostname": hostname,
            "service": service,
            "raw_log": line,
            "parser_type": self.parser_name,
            "metadata_json": {
                "pri": data.get("pri"),
                "pid": data.get("pid"),
                "line_number": line_number
            }
        }
