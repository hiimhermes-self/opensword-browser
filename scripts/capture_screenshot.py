#!/usr/bin/env python3
"""Headless screenshot capture for OpenSword Browser."""
import sys
from pathlib import Path
from PySide6.QtCore import QUrl, QTimer, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTabWidget, QToolBar, QStatusBar, QSplitter
from PySide6.QtWebEngineWidgets import QWebEngineView

REPO_ROOT = Path(__file__).parent.parent
OUT = REPO_ROOT / "docs" / "screenshot.png"
OUT.parent.mkdir(exist_ok=True)

class MiniBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenSword Browser")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet("background:#0d0d0d;color:#eee;")

        # Toolbar
        tb = QToolBar()
        tb.setStyleSheet("background:#0d0d0d;border:none;padding:4px;")
        for sym in ["\u25c0", "\u25b6", "\ud83d\udd04", "\ud83c\udfe0"]:
            b = QPushButton(sym)
            b.setStyleSheet("background:#222;color:#eee;padding:6px 10px;border:none;border-radius:4px;font-size:14px;")
            tb.addWidget(b)
        addr = QLineEdit("https://duckduckgo.com")
        addr.setStyleSheet("background:#1a1a1a;color:#eee;padding:6px;border:1px solid #333;border-radius:4px;font-size:14px;")
        tb.addWidget(addr)
        ai = QPushButton("\ud83e\udd16 AI")
        ai.setStyleSheet("background:#222;color:#0f0;padding:6px 10px;border:none;border-radius:4px;")
        tb.addWidget(ai)
        self.addToolBar(tb)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: #0d0d0d; }
            QTabBar::tab { background: #1a1a1a; color: #aaa; padding: 8px 16px;
                border-top-left-radius: 6px; border-top-right-radius: 6px;
                margin-right: 2px; font-size: 13px; }
            QTabBar::tab:selected { background: #0d0d0d; color: #0f0; border-bottom: 2px solid #0f0; }
        """)
        self.setCentralWidget(self.tabs)

        tab = QWebEngineView()
        html = """<html><head><style>
body{background:#0d0d0d;color:#0f0;font-family:sans-serif;display:flex;flex-wrap:wrap;
justify-content:center;align-items:center;height:100vh;margin:0;}
a{display:flex;width:160px;height:110px;margin:14px;background:#1a1a1a;border:1px solid #333;
border-radius:10px;text-decoration:none;color:#0f0;align-items:center;justify-content:center;
font-size:16px;transition:.2s;}a:hover{background:#252525;transform:translateY(-2px);}
h1{width:100%;text-align:center;margin-bottom:20px;color:#fff;font-weight:300;}
</style></head><body>
<h1>OpenSword Hızlı Erişim</h1>
<a href='https://duckduckgo.com'>DuckDuckGo</a>
<a href='https://github.com'>GitHub</a>
<a href='https://news.ycombinator.com'>Hacker News</a>
<a href='https://wikipedia.org'>Wikipedia</a>
<a href='https://arxiv.org'>ArXiv</a>
<a href='https://reddit.com'>Reddit</a>
<a href='https://youtube.com'>YouTube</a>
<a href='https://perplexity.ai'>Perplexity</a>
</body></html>"""
        tab.setHtml(html)
        self.tabs.addTab(tab, "Yeni Sekme")

        self.statusBar().setStyleSheet("background:#0d0d0d;color:#888;font-size:11px;")
        self.statusBar().showMessage("OpenSword Browser v0.1.0 — Ready")

        QTimer.singleShot(2500, self.capture)

    def capture(self):
        pixmap = self.grab()
        pixmap.save(str(OUT))
        print(f"Screenshot saved: {OUT}")
        QApplication.instance().quit()

app = QApplication(sys.argv)
win = MiniBrowser()
win.show()
app.exec()
