from typing import Optional, Type, Dict
from app.parsers.base import BaseLogParser
from app.parsers.ssh_auth import SSHAuthLogParser
from app.parsers.syslog import SyslogParser
from app.parsers.json_log import JSONLogParser
from app.parsers.csv_log import CSVLogParser
from app.parsers.windows_event import WindowsEventLogParser
from app.parsers.apache_access import ApacheAccessLogParser
from app.parsers.nginx_access import NginxAccessLogParser

PARSER_REGISTRY: Dict[str, Type[BaseLogParser]] = {
    "SSH_AUTH": SSHAuthLogParser,
    "SYSLOG": SyslogParser,
    "JSON_LOG": JSONLogParser,
    "CSV_LOG": CSVLogParser,
    "WINDOWS_SECURITY": WindowsEventLogParser,
    "APACHE_ACCESS": ApacheAccessLogParser,
    "NGINX_ACCESS": NginxAccessLogParser,
}

def get_parser(parser_type: str) -> BaseLogParser:
    parser_cls = PARSER_REGISTRY.get(parser_type.upper(), SSHAuthLogParser)
    return parser_cls()

def detect_parser_from_filename_or_content(filename: str, sample_content: str) -> BaseLogParser:
    fn = filename.lower()
    if fn.endswith(".json"):
        return JSONLogParser()
    if fn.endswith(".csv"):
        return CSVLogParser()
    if "auth" in fn or "secure" in fn or "ssh" in fn:
        return SSHAuthLogParser()
    if "syslog" in fn or "messages" in fn:
        return SyslogParser()
    if "nginx" in fn:
        return NginxAccessLogParser()
    if "apache" in fn or "access" in fn:
        return ApacheAccessLogParser()
    if "win" in fn or "event" in fn:
        return WindowsEventLogParser()

    # Inspect sample content
    sample_strip = sample_content.strip()
    if sample_strip.startswith("{") or sample_strip.startswith("["):
        return JSONLogParser()
    if "sshd[" in sample_content or "Failed password" in sample_content or "Accepted password" in sample_content:
        return SSHAuthLogParser()
    if "EventID" in sample_content or "Logon" in sample_content:
        return WindowsEventLogParser()
    if "," in sample_content and ("timestamp" in sample_content.lower() or "source_ip" in sample_content.lower()):
        return CSVLogParser()

    return SSHAuthLogParser()
