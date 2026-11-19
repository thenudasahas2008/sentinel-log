import re
import uuid
from typing import Optional, Dict, Any
from app.parsers.base import BaseLogParser

class ApacheAccessLogParser(BaseLogParser):
    parser_name: str = "APACHE_ACCESS"

    # Apache Combined Log Format:
    # 127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326 "http://www.example.com/start.html" "Mozilla/4.08 [en] (Win98; I ;Nav)"
    APACHE_PATTERN = re.compile(
        r'^(?P<ip>\S+)\s+(?P<ident>\S+)\s+(?P<user>\S+)\s+\[(?P<timestamp>[^\]]+)\]\s+"(?P<request>[^"]+)"\s+(?P<status>\d{3})\s+(?P<size>\S+)(?:\s+"(?P<referrer>[^"]*)"\s+"(?P<agent>[^"]*)")?'
    )

    def parse_line(self, line: str, line_number: int = 0) -> Optional[Dict[str, Any]]:
        match = self.APACHE_PATTERN.match(line)
        if not match:
            return None

        data = match.groupdict()
        source_ip = self.normalize_ip(data.get("ip"))
        # Parse timestamp: e.g. 10/Oct/2000:13:55:36 -0700
        raw_ts = data.get("timestamp", "").replace(":", " ", 1)
        timestamp = self.normalize_timestamp(raw_ts)

        username = data.get("user") if data.get("user") != "-" else None
        status_code = int(data.get("status", 0))

        # Classify status
        if status_code in [401, 403]:
            event_status = "FAILURE"
            action = "UNAUTHORIZED_ACCESS"
        elif 200 <= status_code < 400:
            event_status = "SUCCESS"
            action = "HTTP_REQUEST"
        else:
            event_status = "FAILURE" if status_code >= 400 else "UNKNOWN"
            action = "HTTP_REQUEST"

        req_parts = data.get("request", "").split()
        method = req_parts[0] if req_parts else "GET"
        endpoint = req_parts[1] if len(req_parts) > 1 else "/"

        return {
            "event_uuid": f"evt-{uuid.uuid4().hex[:16]}",
            "timestamp": timestamp,
            "source_ip": source_ip,
            "source_port": None,
            "destination_ip": None,
            "destination_port": 80,
            "event_type": "APACHE_ACCESS",
            "action": action,
            "status": event_status,
            "username": username,
            "hostname": "web-server",
            "service": "apache",
            "raw_log": line,
            "parser_type": self.parser_name,
            "metadata_json": {
                "http_status": status_code,
                "method": method,
                "endpoint": endpoint,
                "user_agent": data.get("agent"),
                "referrer": data.get("referrer")
            }
        }
