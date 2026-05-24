# SPDX-License-Identifier: Apache-2.0
"""Site izin yonetimi."""
from pathlib import Path
import json
from opensword.constants import CONFIG_DIR

PERMS_FILE = CONFIG_DIR / "permissions.json"

class PermissionManager:
    def __init__(self):
        self.rules = self._load()

    def _load(self):
        if PERMS_FILE.exists():
            try:
                with open(PERMS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def allow(self, site: str, permission: str):
        self.rules.setdefault(site, {})[permission] = "allow"
        self._save()

    def deny(self, site: str, permission: str):
        self.rules.setdefault(site, {})[permission] = "deny"
        self._save()

    def _save(self):
        with open(PERMS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.rules, f, ensure_ascii=False, indent=2)
