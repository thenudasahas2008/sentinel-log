import csv
import io
import uuid
from typing import Optional, Dict, Any, List
from app.parsers.base import BaseLogParser

class CSVLogParser(BaseLogParser):
    parser_name: str = "CSV_LOG"

    def __init__(self):
        self.headers: Optional[List[str]] = None

    def parse_line(self, line: str, line_number: int = 0) -> Optional[Dict[str, Any]]:
        reader = csv.reader(io.StringIO(line))
        try:
            row = next(reader)
        except StopIteration:
            return None

        # First line is usually header if line_number == 1
        if line_number == 1 and not self.headers:
            # Check if looks like header
            if any(h.lower() in ["timestamp", "time", "date", "source_ip", "ip", "username", "user", "status"] for h in row):
                self.headers = [h.strip().lower() for h in row]
                return None
            else:
                self.headers = [f"col_{i}" for i in range(len(row))]

        if not self.headers or len(row) != len(self.headers):
            # Fallback headers
            self.headers = [f"col_{i}" for i in range(len(row))]

        row_dict = dict(zip(self.headers, row))

        # Extract values
        raw_ts = next((row_dict[k] for k in row_dict if any(t in k for t in ["time", "date", "ts"])), None)
        timestamp = self.normalize_timestamp(raw_ts)

        raw_ip = next((row_dict[k] for k in row_dict if any(i in k for i in ["ip", "src", "client", "host"])), None)
        source_ip = self.normalize_ip(raw_ip)

        username = next((row_dict[k] for k in row_dict if any(u in k for u in ["user", "account", "login"])), None)
        raw_status = next((row_dict[k] for k in row_dict if "status" in k or "result" in k or "outcome" in k), "UNKNOWN").upper()
        
        status = "UNKNOWN"
        if any(s in raw_status for s in ["FAIL", "ERR", "DENI", "0"]):
            status = "FAILURE"
        elif any(s in raw_status for s in ["SUCC", "OK", "PASS", "1"]):
            status = "SUCCESS"

        return {
            "event_uuid": f"evt-{uuid.uuid4().hex[:16]}",
            "timestamp": timestamp,
            "source_ip": source_ip,
            "source_port": None,
            "destination_ip": None,
            "destination_port": None,
            "event_type": "CSV_AUTH",
            "action": "AUTH_EVENT",
            "status": status,
            "username": username,
            "hostname": "csv-source",
            "service": "csv_import",
            "raw_log": line,
            "parser_type": self.parser_name,
            "metadata_json": row_dict
        }
