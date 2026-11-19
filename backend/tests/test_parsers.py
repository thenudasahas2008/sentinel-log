import pytest
from app.parsers import get_parser, detect_parser_from_filename_or_content

def test_ssh_auth_parser():
    parser = get_parser("SSH_AUTH")
    line = "Nov 20 02:15:01 bastion sshd[24512]: Failed password for invalid user admin from 198.51.100.42 port 49152 ssh2"
    res = parser.parse_line(line)
    assert res is not None
    assert res["username"] == "admin"
    assert res["source_ip"] == "198.51.100.42"
    assert res["status"] == "FAILURE"
    assert res["action"] == "LOGIN"
    assert res["service"] == "sshd"

def test_ssh_accepted_publickey():
    parser = get_parser("SSH_AUTH")
    line = "Nov 20 02:16:10 bastion sshd[24515]: Accepted publickey for root from 10.0.0.50 port 51221 ssh2: RSA SHA256:abc"
    res = parser.parse_line(line)
    assert res is not None
    assert res["username"] == "root"
    assert res["status"] == "SUCCESS"

def test_windows_event_json_parser():
    parser = get_parser("WINDOWS_SECURITY")
    line = '{"EventID": 4625, "TimeCreated": "2026-11-20T02:00:00Z", "TargetUserName": "Administrator", "IpAddress": "192.168.1.150"}'
    res = parser.parse_line(line)
    assert res is not None
    assert res["status"] == "FAILURE"
    assert res["username"] == "Administrator"
    assert res["source_ip"] == "192.168.1.150"

def test_syslog_rfc5424():
    parser = get_parser("SYSLOG")
    line = "<34>1 2026-11-20T02:30:00Z firewall.corp.local sudo 14502 ID47 - user secops : COMMAND=/bin/bash"
    res = parser.parse_line(line)
    assert res is not None
    assert res["service"] == "sudo"
    assert res["hostname"] == "firewall.corp.local"

def test_nginx_access_parser():
    parser = get_parser("NGINX_ACCESS")
    line = '198.51.100.99 - admin [20/Nov/2026:02:40:01 +0000] "POST /api/v1/auth/login HTTP/1.1" 401 84 "-" "curl/7.68.0"'
    res = parser.parse_line(line)
    assert res is not None
    assert res["source_ip"] == "198.51.100.99"
    assert res["status"] == "FAILURE"
    assert res["metadata_json"]["http_status"] == 401
