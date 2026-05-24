# SPDX-License-Identifier: Apache-2.0
"""Klavye kisayol yonetimi."""
from PySide6.QtGui import QKeySequence

SHORTCUTS = {
    "new_tab": "Ctrl+T",
    "close_tab": "Ctrl+W",
    "restore_tab": "Ctrl+Shift+T",
    "next_tab": "Ctrl+Tab",
    "prev_tab": "Ctrl+Shift+Tab",
    "reload": "Ctrl+R",
    "ai_panel": "Ctrl+Shift+A",
    "command_palette": "Ctrl+K",
    "add_bookmark": "Ctrl+D",
    "focus_url": "Ctrl+L",
    "find": "Ctrl+F",
    "fullscreen": "F11",
    "dev_tools": "F12",
    "zoom_in": "Ctrl++",
    "zoom_out": "Ctrl+-",
}

def get_sequence(name: str) -> QKeySequence:
    return QKeySequence(SHORTCUTS.get(name, ""))
