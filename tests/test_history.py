import pytest
from pathlib import Path
import tempfile
from opensword.history import HistoryManager

def test_history_add_and_search():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tf:
        mgr = HistoryManager(Path(tf.name))
        mgr.add("https://example.com", "Example")
        results = mgr.search("example")
        assert len(results) == 1
        assert results[0]["url"] == "https://example.com"
