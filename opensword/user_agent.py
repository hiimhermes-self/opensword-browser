# SPDX-License-Identifier: Apache-2.0
"""User-Agent yonetimi."""
DEFAULT_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OpenSword/0.1.0"
)

class UserAgentManager:
    def __init__(self, ua: str = DEFAULT_UA):
        self.ua = ua

    def set(self, ua: str):
        self.ua = ua

    def get(self) -> str:
        return self.ua
