# SPDX-License-Identifier: Apache-2.0
"""Sabitler ve varsayilan degerler."""
from pathlib import Path

APP_NAME = "OpenSword"
APP_VERSION = "0.1.0"
APP_ORG = "hiimhermes-self"

CONFIG_DIR = Path.home() / ".config" / "opensword"
BOOKMARKS_FILE = CONFIG_DIR / "bookmarks.json"
SETTINGS_FILE = CONFIG_DIR / "settings.json"
HISTORY_FILE = CONFIG_DIR / "history.json"

DEFAULT_HOME = "https://duckduckgo.com"
DEFAULT_SEARCH = "https://duckduckgo.com/?q={}"

MAX_RECENT_CLOSED = 10
TAB_SLEEP_MINUTES = 5
