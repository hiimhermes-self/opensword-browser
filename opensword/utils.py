# SPDX-License-Identifier: Apache-2.0
"""Yardimci fonksiyonlar."""
import re
from urllib.parse import urlparse

def normalize_url(text: str, search_template: str = "https://duckduckgo.com/?q={}") -> str:
    """Kullanici girdisini normalize eder."""
    text = text.strip()
    if not text:
        return "about:blank"
    if "." in text and " " not in text and not text.startswith(("http://", "https://")):
        return "https://" + text
    if not text.startswith(("http://", "https://", "file://")):
        return search_template.format(text.replace(" ", "+"))
    return text

def is_valid_hostname(hostname: str) -> bool:
    if len(hostname) > 253:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1]
    allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))
