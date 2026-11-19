import abc
import ipaddress
import hashlib
from datetime import datetime
from typing import Generator, Dict, Any, Optional, Tuple
from dateutil import parser as dt_parser

class BaseLogParser(abc.ABC):
    """
    Abstract base class for all SentinelLog format parsers.
    Handles encoding detection, streaming, timestamp normalization, and IP validation.
    """
    parser_name: str = "BASE"

    @classmethod
    def detect_encoding(cls, file_bytes_sample: bytes) -> str:
        """Detect file encoding safely."""
        for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252", "utf-16"]:
            try:
                file_bytes_sample.decode(enc)
                return enc
            except UnicodeDecodeError:
                continue
        return "utf-8"

    @classmethod
    def compute_hash(cls, file_path: str) -> str:
        """Compute SHA-256 hash of file for duplicate prevention."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        return sha256.hexdigest()

    @classmethod
    def normalize_ip(cls, ip_str: Optional[str]) -> Optional[str]:
        """Validates and normalizes IPv4 and IPv6 addresses."""
        if not ip_str:
            return None
        ip_clean = ip_str.strip().strip("[]").split(":")[0] if "." in ip_str and ":" in ip_str and ip_str.count(":") == 1 else ip_str.strip().strip("[]")
        try:
            ip_obj = ipaddress.ip_address(ip_clean)
            return str(ip_obj)
        except ValueError:
            return None

    @classmethod
    def normalize_timestamp(cls, ts_input: Any, default_year: Optional[int] = None) -> datetime:
        """Robust timestamp parser supporting ISO, Syslog, epoch, and Windows formats."""
        if isinstance(ts_input, datetime):
            return ts_input
        if isinstance(ts_input, (int, float)):
            try:
                # Handle millisecond vs second timestamps
                if ts_input > 1e11:
                    ts_input = ts_input / 1000.0
                return datetime.utcfromtimestamp(ts_input)
            except Exception:
                return datetime.utcnow()
        if not ts_input or not isinstance(ts_input, str):
            return datetime.utcnow()

        ts_str = ts_input.strip()
        try:
            parsed = dt_parser.parse(ts_str, fuzzy=True)
            # Handle syslog without year: e.g. "Nov 19 02:45:00"
            if parsed.year == 1900 or (default_year and parsed.year == 1900):
                year = default_year or datetime.utcnow().year
                parsed = parsed.replace(year=year)
            return parsed
        except Exception:
            return datetime.utcnow()

    @abc.abstractmethod
    def parse_line(self, line: str, line_number: int = 0) -> Optional[Dict[str, Any]]:
        """Parses a single raw line into standardized security event dictionary."""
        pass

    def parse_file(self, file_path: str) -> Generator[Dict[str, Any], None, None]:
        """Streams through the log file yielding normalized events."""
        with open(file_path, "rb") as bf:
            sample = bf.read(4096)
        encoding = self.detect_encoding(sample)

        with open(file_path, "r", encoding=encoding, errors="replace") as f:
            for line_idx, line in enumerate(f, start=1):
                clean_line = line.strip()
                if not clean_line:
                    continue
                parsed = self.parse_line(clean_line, line_idx)
                if parsed:
                    yield parsed
