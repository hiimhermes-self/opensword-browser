# SPDX-License-Identifier: Apache-2.0
"""Tema yonetimi."""
DARK_THEME = """
QMainWindow { background: #0d0d0d; color: #eee; }
QToolBar { background: #0d0d0d; border: none; }
QLineEdit { background: #1a1a1a; color: #eee; border: 1px solid #333; }
QTabBar::tab { background: #1a1a1a; color: #aaa; }
QTabBar::tab:selected { background: #0d0d0d; color: #0f0; border-bottom: 2px solid #0f0; }
QStatusBar { background: #0d0d0d; color: #888; }
QPlainTextEdit { background: #0a0a0a; color: #0f0; }
"""

LIGHT_THEME = """
QMainWindow { background: #f5f5f5; color: #222; }
QToolBar { background: #e0e0e0; border: none; }
QLineEdit { background: #fff; color: #222; border: 1px solid #ccc; }
QTabBar::tab { background: #ddd; color: #333; }
QTabBar::tab:selected { background: #fff; color: #000; border-bottom: 2px solid #0078d7; }
"""

def apply_theme(widget, theme_css: str):
    widget.setStyleSheet(theme_css)
