"""Module bao mat duoc tiep thu tu Hermes Agent:
1. Threat Patterns: quet prompt injection, lech chi thi he thong (forget instructions), ro ri token bi mat.
2. URL Safety: ngan chan tan cong SSRF vao IP noi bo (127.0.0.1, 10.x, 192.168.x, Cloud metadata 169.254.169.254).
"""
import ipaddress
import logging
import re
import socket
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# --- 1. THREAT PATTERNS SCANNER (Prompt Injection & Instruction Overrides) ---
_NEGATOR = (r"(?:(?:do|does|did|ca|could|would|should|wo|must|need|is|are|was|were|ai|has|have|had)n[’']?t"
            r"|cannot|not|never)")

_FORGET_RULES_RE = re.compile(
    rf"(?:^|[^\w’' \t]|_)[ \t]*"
    rf"forget\s+(?:about\s+)?(your|all|any|previous|prior|above|earlier)"
    rf"\s+(?:\w+\s+){{0,3}}(instructions|rules|guidelines)",
    re.IGNORECASE,
)

_SYSTEM_OVERRIDE_RE = re.compile(
    r"(?:you are now|pretend you are|disregard previous|ignore all previous|new system prompt|override system prompt)",
    re.IGNORECASE,
)

_SECRET_LEAK_RE = re.compile(
    r"\$\{?\w{0,64}(?:KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)S?\}?",
    re.IGNORECASE,
)


def scan_for_threats(text: str) -> list[str]:
    """Quét văn bản đầu vào để tìm các dấu hiệu tấn công prompt injection hoặc ghi đè luật hệ thống."""
    if not text or not isinstance(text, str):
        return []
    threats = []
    if _FORGET_RULES_RE.search(text):
        threats.append("forget_instructions_override")
    if _SYSTEM_OVERRIDE_RE.search(text):
        threats.append("system_override_attempt")
    if _SECRET_LEAK_RE.search(text):
        threats.append("secret_credential_reference")
    return threats


# --- 2. URL SAFETY & SSRF PROTECTION ---
# Các dải IP riêng tư và IP Cloud Metadata (AWS/GCP/Azure)
BLOCKED_IPS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),  # Cloud metadata IP (169.254.169.254)
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


def is_safe_url(url: str, allow_private: bool = False) -> tuple[bool, str]:
    """Kiểm tra URL có an toàn để truy cập không (ngăn chặn SSRF).
    Trả về (is_safe, reason).
    """
    if not url or not isinstance(url, str):
        return False, "URL rỗng"

    parsed = urlparse(url.strip())
    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Giao thức '{parsed.scheme}' không được hỗ trợ (chỉ nhận http/https)"

    hostname = parsed.hostname
    if not hostname:
        return False, "Không tìm thấy hostname trong URL"

    if hostname.lower() in ("localhost", "metadata.google.internal", "instance-data"):
        if not allow_private:
            return False, f"Hostname nội bộ bị chặn ({hostname})"

    # Giải quyết DNS để kiểm tra IP thực tế (chống DNS rebinding / IP loopback dạng thập phân)
    try:
        resolved_ips = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        # Không phân giải được DNS: có thể là URL không tồn tại
        return True, ""

    for item in resolved_ips:
        ip_str = item[4][0]
        try:
            ip = ipaddress.ip_address(ip_str)
            for blocked_net in BLOCKED_IPS:
                if ip in blocked_net:
                    if not allow_private:
                        return False, f"URL trỏ tới địa chỉ mạng nội bộ/metadata ({ip_str}) bị chặn nhằm đảm bảo an toàn"
        except ValueError:
            continue

    return True, ""
