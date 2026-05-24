# SPDX-License-Identifier: Apache-2.0
"""Cerez yonetimi."""
from pathlib import Path
from opensword.constants import CONFIG_DIR

COOKIE_DIR = CONFIG_DIR / "cookies"
COOKIE_DIR.mkdir(parents=True, exist_ok=True)

def clear_all_cookies():
    for f in COOKIE_DIR.iterdir():
        if f.is_file():
            f.unlink()

def get_cookie_path(profile: str = "default") -> Path:
    return COOKIE_DIR / f"{profile}.sqlite"
