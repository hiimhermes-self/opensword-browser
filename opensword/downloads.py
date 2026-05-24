# SPDX-License-Identifier: Apache-2.0
"""Indirme yoneticisi."""
import json
from pathlib import Path
from datetime import datetime
from opensword.constants import CONFIG_DIR

class DownloadManager:
    def __init__(self, path: Path = CONFIG_DIR / "downloads.json"):
        self.path = path
        self.items = self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def add(self, filename: str, url: str, directory: str):
        self.items.append({
            "filename": filename,
            "url": url,
            "directory": directory,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        })
        self.save()

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)

    def list(self):
        return self.items
