# SPDX-License-Identifier: Apache-2.0
"""Arama motoru sablonlari."""
ENGINES = {
    "duckduckgo": "https://duckduckgo.com/?q={}",
    "google": "https://www.google.com/search?q={}",
    "bing": "https://www.bing.com/search?q={}",
    "brave": "https://search.brave.com/search?q={}",
    "searxng": "https://search.example.com/search?q={}",
}

def get_engine(name: str) -> str:
    return ENGINES.get(name, ENGINES["duckduckgo"])
