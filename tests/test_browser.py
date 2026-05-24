import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from opensword.utils import normalize_url, is_valid_hostname

def test_normalize_url_search():
    assert "duckduckgo.com" in normalize_url("hello world")

def test_normalize_url_direct():
    assert normalize_url("example.com").startswith("https://")

def test_normalize_url_with_scheme():
    assert normalize_url("https://github.com") == "https://github.com"

def test_is_valid_hostname():
    assert is_valid_hostname("example.com") is True
    assert is_valid_hostname("-invalid.com") is False
