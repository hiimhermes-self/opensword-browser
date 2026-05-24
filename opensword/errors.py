# SPDX-License-Identifier: Apache-2.0
"""Hata yonetimi ve guvenli loglama."""
import logging
from pathlib import Path
from opensword.constants import CONFIG_DIR

LOG_FILE = CONFIG_DIR / "opensword.log"

handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

logger = logging.getLogger("opensword")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

class BrowserError(Exception):
    pass

class NavigationError(BrowserError):
    pass
