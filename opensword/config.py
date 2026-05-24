# SPDX-License-Identifier: Apache-2.0
"""Merkezi yapilandirma yoneticisi."""
import json
from pathlib import Path
from opensword.constants import SETTINGS_FILE

class ConfigManager:
    def __init__(self, path: Path = SETTINGS_FILE):
        self.path = path
        self._data = self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"home": "https://duckduckgo.com", "search": "https://duckduckgo.com/?q={}"}

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value):
        self._data[key] = value
        self.save()

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
