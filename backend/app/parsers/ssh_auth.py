import re
import uuid
from typing import Optional, Dict, Any
from app.parsers.base import BaseLogParser

class SSHAuthLogParser(BaseLogParser):
    parser_name: str = "SSH_AUTH"

    # Regex patterns for standard Linux /var/log/auth.log and secure
    # Example: Nov 20 02:15:01 bastion sshd[24512]: Failed password for invalid user admin from 192.168.1.105 port 49152 ssh2
    # Example: Nov 20 02:16:10 bastion sshd[24515]: Accepted publickey for root from 10.0.0.50 port 51221 ssh2: RSA SHA256:...
    SSH_PATTERNS = [
        # Failed password for invalid user
        re.compile(
            r'^(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+\d+:\d+:\d+)\s+(?P<hostname>\S+)\s+sshd(?:\[\d+\])?:\s+Failed password for invalid user (?P<username>\S+)\s+from\s+(?P<source_ip>\S+)\s+port\s+(?P<source_port>\d+)',
            re.IGNORECASE
        ),
        # Failed password for valid user
        re.compile(
            r'^(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+\d+:\d+:\d+)\s+(?P<hostname>\S+)\s+sshd(?:\[\d+\])?:\s+Failed password for (?P<username>\S+)\s+from\s+(?P<source_ip>\S+)\s+port\s+(?P<source_port>\d+)',
            re.IGNORECASE
        ),
        # Accepted password / publickey
        re.compile(
            r'^(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+\d+:\d+:\d+)\s+(?P<hostname>\S+)\s+sshd(?:\[\d+\])?:\s+Accepted (?:password|publickey) for (?P<username>\S+)\s+from\s+(?P<source_ip>\S+)\s+port\s+(?P<source_port>\d+)',
            re.IGNORECASE
        ),
        # Invalid user announcement
        re.compile(
            r'^(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+\d+:\d+:\d+)\s+(?P<hostname>\S+)\s+sshd(?:\[\d+\])?:\s+Invalid user (?P<username>\S+)\s+from\s+(?P<source_ip>\S+)',
            re.IGNORECASE
        ),
        # Connection closed / reset during auth
        re.compile(
            r'^(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+\d+:\d+:\d+)\s+(?P<hostname>\S+)\s+sshd(?:\[\d+\])?:\s+Connection closed by (?:authenticating user )?(?P<username>\S+)?\s*(?P<source_ip>\S+)\s+port\s+(?P<source_port>\d+)',
            re.IGNORECASE
        )
    ]

    def parse_line(self, line: str, line_number: int = 0) -> Optional[Dict[str, Any]]:
        for pattern in self.SSH_PATTERNS:
            match = pattern.search(line)
            if match:
                data = match.groupdict()
                timestamp = self.normalize_timestamp(data.get("timestamp"))
                source_ip = self.normalize_ip(data.get("source_ip"))
                source_port = int(data.get("source_port")) if data.get("source_port") and data["source_port"].isdigit() else None
                username = data.get("username", "unknown")
                hostname = data.get("hostname", "localhost")

                # Determine action & status
                line_lower = line.lower()
                if "accepted" in line_lower:
                    status = "SUCCESS"
                    action = "LOGIN"
                elif "failed password" in line_lower or "invalid user" in line_lower:
                    status = "FAILURE"
                    action = "LOGIN"
                elif "connection closed" in line_lower:
                    status = "FAILURE"
                    action = "CONNECTION_ABORT"
                else:
                    status = "UNKNOWN"
                    action = "COMMAND"

                return {
                    "event_uuid": f"evt-{uuid.uuid4().hex[:16]}",
                    "timestamp": timestamp,
                    "source_ip": source_ip,
                    "source_port": source_port,
                    "destination_ip": None,
                    "destination_port": 22,
                    "event_type": "SSH_AUTH",
                    "action": action,
                    "status": status,
                    "username": username,
                    "hostname": hostname,
                    "service": "sshd",
                    "raw_log": line,
                    "parser_type": self.parser_name,
                    "metadata_json": {
                        "is_invalid_user": "invalid user" in line_lower,
                        "auth_method": "publickey" if "publickey" in line_lower else "password",
                        "line_number": line_number
                    }
                }
        return None
