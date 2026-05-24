# SPDX-License-Identifier: Apache-2.0
"""Gecmis yonetimi."""
import json
from pathlib import Path
from datetime import datetime
from opensword.constants import HISTORY_FILE

class HistoryManager:
    def __init__(self, path: Path = HISTORY_FILE):
        self.path = path
        self.entries = self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def add(self, url: str, title: str = ""):
        self.entries.append({
            "url": url,
            "title": title,
            "timestamp": datetime.now().isoformat()
        })
        self.save()

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.entries[-500:], f, ensure_ascii=False, indent=2)

    def search(self, query: str):
        q = query.lower()
        return [e for e in self.entries if q in e.get("url", "").lower() or q in e.get("title", "").lower()]
