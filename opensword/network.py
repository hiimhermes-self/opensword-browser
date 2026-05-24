# SPDX-License-Identifier: Apache-2.0
"""Ag istatistikleri ve monitor."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class RequestStats:
    url: str
    method: str = "GET"
    status: Optional[int] = None
    duration_ms: Optional[float] = None

class NetworkMonitor:
    def __init__(self):
        self.requests = []

    def log(self, stats: RequestStats):
        self.requests.append(stats)

    def summary(self) -> dict:
        total = len(self.requests)
        return {"total_requests": total, "last_url": self.requests[-1].url if self.requests else None}
