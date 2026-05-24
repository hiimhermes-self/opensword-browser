# SPDX-License-Identifier: Apache-2.0
"""Oturum yonetimi: acik sekmeleri kaydet ve geri yukle."""
import json
from pathlib import Path
from opensword.constants import CONFIG_DIR

SESSION_FILE = CONFIG_DIR / "session.json"

class SessionManager:
    def save(self, urls: list):
        SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({"urls": urls}, f, ensure_ascii=False, indent=2)

    def load(self) -> list:
        if SESSION_FILE.exists():
            try:
                with open(SESSION_FILE, "r", encoding="utf-8") as f:
                    return json.load(f).get("urls", [])
            except Exception:
                pass
        return []
