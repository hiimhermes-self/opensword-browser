# Copyright 2025 hiimhermes-self
# SPDX-License-Identifier: Apache-2.0
"""OpenSword Browser — Modern, AI-native, open-source web browser."""
import json
import sys
from pathlib import Path
import importlib.util
from urllib.parse import urlparse

from PySide6.QtCore import QUrl, Qt, Slot, QTimer
from PySide6.QtGui import QKeySequence, QShortcut, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTabWidget, QToolBar, QStatusBar,
    QSplitter, QTextEdit, QComboBox, QLabel, QMenu, QDialog,
    QDialogButtonBox, QPlainTextEdit, QFileDialog, QMessageBox
)
from PySide6.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineDownloadRequest


CONFIG_DIR = Path.home() / ".config" / "opensword"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
BOOKMARKS_FILE = CONFIG_DIR / "bookmarks.json"
SETTINGS_FILE = CONFIG_DIR / "settings.json"


def load_json(path: Path, default=None) -> dict:
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default if default is not None else {}


def save_json(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class WebTab(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPage(QWebEnginePage(self))
        self.page().profile().downloadRequested.connect(self.on_download)
        self.loadFinished.connect(self.on_load_finished)
        self.urlChanged.connect(self.on_url_changed)
        self.titleChanged.connect(self.on_title_changed)
        self._title = "Yeni Sekme"
        self._icon = None

    def on_load_finished(self, ok):
        pass

    def on_url_changed(self, url):
        pass

    def on_title_changed(self, title):
        self._title = title or "Yeni Sekme"
        win = self.window()
        if isinstance(win, BrowserWindow):
            win.update_tab_title(self)

    def on_download(self, download: QWebEngineDownloadRequest):
        path, _ = QFileDialog.getSaveFileName(self, "Dosya Kaydet", download.suggestedFileName())
        if path:
            download.setDownloadDirectory(str(Path(path).parent))
            download.setDownloadFileName(Path(path).name)
            download.accept()

    def createWindow(self, window_type):
        win = self.window()
        if isinstance(win, BrowserWindow):
            return win.add_tab("about:blank", activate=False)
        return None


class CommandPalette(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.Dialog)
        self.setWindowTitle("Komut Paleti")
        self.setFixedSize(600, 400)
        self.setStyleSheet("background:#1a1a1a;color:#eee;border:1px solid #333;")
        layout = QVBoxLayout(self)
        self.search = QLineEdit(self)
        self.search.setPlaceholderText("Komut ara...")
        self.search.setStyleSheet("padding:10px;font-size:16px;background:#222;color:#eee;border:none;")
        layout.addWidget(self.search)
        self.results = QPlainTextEdit(self)
        self.results.setReadOnly(True)
        self.results.setStyleSheet("background:#1a1a1a;color:#aaa;border:none;font-size:14px;")
        layout.addWidget(self.results)
        self.commands = [
            ("Yeni sekme", "Ctrl+T"),
            ("Sekmeyi kapat", "Ctrl+W"),
            ("Sonraki sekme", "Ctrl+Tab"),
            ("Önceki sekme", "Ctrl+Shift+Tab"),
            ("Yenile", "Ctrl+R"),
            ("AI paneli aç/kapat", "Ctrl+Shift+A"),
            ("Komut paleti", "Ctrl+K"),
            ("Yer imi ekle", "Ctrl+D"),
            ("Gizli modda yeni pencere", "Ctrl+Shift+N"),
            ("Geliştirici araçları", "F12"),
        ]
        self.update_results("")
        self.search.textChanged.connect(self.update_results)
        self.search.returnPressed.connect(self.run_selected)

    def update_results(self, text):
        lines = []
        for cmd, key in self.commands:
            if text.lower() in cmd.lower() or text.lower() in key.lower():
                lines.append(f"{cmd}  <span style='color:#666'>{key}</span>")
        self.results.setPlainText("\n".join(lines) if lines else "Sonuç yok")

    def run_selected(self):
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)


class AIPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(320)
        self.setStyleSheet("background:#111;color:#eee;border-left:1px solid #333;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        header = QLabel("🚀 AI Yardımcı")
        header.setStyleSheet("font-size:16px;font-weight:bold;color:#0f0;padding-bottom:6px;")
        layout.addWidget(header)

        self.provider = QComboBox(self)
        self.provider.addItems(["OpenAI", "Groq", "Anthropic", "Ollama (Yerel)"])
        self.provider.setStyleSheet("background:#222;color:#eee;padding:4px;")
        layout.addWidget(self.provider)

        self.api_key = QLineEdit(self)
        self.api_key.setPlaceholderText("API Key (opsiyonel)")
        self.api_key.setEchoMode(QLineEdit.Password)
        self.api_key.setStyleSheet("background:#222;color:#eee;padding:6px;")
        layout.addWidget(self.api_key)

        self.chat = QTextEdit(self)
        self.chat.setReadOnly(True)
        self.chat.setStyleSheet("background:#0a0a0a;color:#0f0;border:1px solid #222;padding:6px;")
        layout.addWidget(self.chat)

        input_row = QHBoxLayout()
        self.prompt = QLineEdit(self)
        self.prompt.setPlaceholderText("Sorunuzu yazın...")
        self.prompt.setStyleSheet("background:#222;color:#eee;padding:6px;")
        self.prompt.returnPressed.connect(self.send)
        input_row.addWidget(self.prompt)

        send_btn = QPushButton("Gönder")
        send_btn.setStyleSheet("background:#0f0;color:#000;padding:6px 12px;")
        send_btn.clicked.connect(self.send)
        input_row.addWidget(send_btn)
        layout.addLayout(input_row)

        summarize_btn = QPushButton("📋 Sayfayı Özetle")
        summarize_btn.setStyleSheet("background:#222;color:#eee;padding:6px;")
        summarize_btn.clicked.connect(self.summarize_page)
        layout.addWidget(summarize_btn)

        self.setVisible(False)

    def log(self, msg):
        self.chat.append(f"<span style='color:#0f0'>> {msg}</span>")

    @Slot()
    def send(self):
        text = self.prompt.text().strip()
        if not text:
            return
        self.chat.append(f"<b style='color:#fff'>Siz:</b> {text}")
        self.prompt.clear()
        # Placeholder cevap - ileride API entegrasyonu eklenecek
        self.chat.append(f"<b style='color:#0f0'>AI:</b> API entegrasyonu için ayarları yapılandırın. Seçili sağlayıcı: {self.provider.currentText()}")

    @Slot()
    def summarize_page(self):
        win = self.window()
        if isinstance(win, BrowserWindow):
            url = win.current_url()
            self.chat.append(f"<b style='color:#ffa500'>Özet:</b> {url} sayfası için özet istendi. (API entegrasyonu bekleniyor)")


class BrowserWindow(QMainWindow):
    def __init__(self, private=False):
        super().__init__()
        self.private = private
        self.setWindowTitle("OpenSword Browser")
        self.setGeometry(100, 100, 1400, 900)
        self.settings_data = load_json(SETTINGS_FILE, {"home": "https://duckduckgo.com", "search": "https://duckduckgo.com/?q={}"})
        self.bookmarks = load_json(BOOKMARKS_FILE, [])

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)

        self.browser_container = QWidget()
        browser_layout = QVBoxLayout(self.browser_container)
        browser_layout.setContentsMargins(0, 0, 0, 0)
        browser_layout.setSpacing(0)
        self.splitter.addWidget(self.browser_container)

        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet("background:#0d0d0d;border:none;padding:4px;")
        self.addToolBar(self.toolbar)

        self.btn_back = QPushButton("◀")
        self.btn_back.setStyleSheet(self._btn_style())
        self.btn_back.setToolTip("Geri (Alt+Left)")
        self.btn_back.clicked.connect(self.go_back)
        self.toolbar.addWidget(self.btn_back)

        self.btn_forward = QPushButton("▶")
        self.btn_forward.setStyleSheet(self._btn_style())
        self.btn_forward.setToolTip("İleri (Alt+Right)")
        self.btn_forward.clicked.connect(self.go_forward)
        self.toolbar.addWidget(self.btn_forward)

        self.btn_reload = QPushButton("🔄")
        self.btn_reload.setStyleSheet(self._btn_style())
        self.btn_reload.setToolTip("Yenile (Ctrl+R)")
        self.btn_reload.clicked.connect(self.reload_page)
        self.toolbar.addWidget(self.btn_reload)

        self.btn_home = QPushButton("🏠")
        self.btn_home.setStyleSheet(self._btn_style())
        self.btn_home.setToolTip("Ana Sayfa")
        self.btn_home.clicked.connect(self.go_home)
        self.toolbar.addWidget(self.btn_home)

        self.address_bar = QLineEdit()
        self.address_bar.setStyleSheet(
            "background:#1a1a1a;color:#eee;padding:6px;border:1px solid #333;border-radius:4px;font-size:14px;"
        )
        self.address_bar.returnPressed.connect(self.load_url)
        self.toolbar.addWidget(self.address_bar)

        self.btn_ai = QPushButton("🤖 AI")
        self.btn_ai.setStyleSheet(self._btn_style("#0f0", "#000"))
        self.btn_ai.setToolTip("AI Paneli (Ctrl+Shift+A)")
        self.btn_ai.clicked.connect(self.toggle_ai)
        self.toolbar.addWidget(self.btn_ai)

        self.btn_bookmark = QPushButton("⭐")
        self.btn_bookmark.setStyleSheet(self._btn_style())
        self.btn_bookmark.setToolTip("Yer imi ekle (Ctrl+D)")
        self.btn_bookmark.clicked.connect(self.add_bookmark)
        self.toolbar.addWidget(self.btn_bookmark)

        self.btn_menu = QPushButton("⋮")
        self.btn_menu.setStyleSheet(self._btn_style())
        self.btn_menu.setToolTip("Menü")
        self.btn_menu.clicked.connect(self.show_menu)

        self.btn_zoom_in = QPushButton("+")
        self.btn_zoom_in.setStyleSheet(self._btn_style())
        self.btn_zoom_in.setToolTip("Yakinlastir (Ctrl++)")
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        self.toolbar.addWidget(self.btn_zoom_in)

        self.btn_zoom_out = QPushButton("-")
        self.btn_zoom_out.setStyleSheet(self._btn_style())
        self.btn_zoom_out.setToolTip("Uzaklastir (Ctrl+-)")
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        self.toolbar.addWidget(self.btn_zoom_out)
        self.toolbar.addWidget(self.btn_menu)

        # Bookmarks bar
        self.bookmarks_bar = QHBoxLayout()
        self.bookmarks_bar.setSpacing(4)
        self.bookmarks_bar.setContentsMargins(6, 2, 6, 2)
        self.bookmarks_widget = QWidget()
        self.bookmarks_widget.setStyleSheet("background:#0d0d0d;border-bottom:1px solid #222;")
        self.bookmarks_widget.setLayout(self.bookmarks_bar)
        browser_layout.addWidget(self.bookmarks_widget)
        self.refresh_bookmarks_bar()

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setStyleSheet(self._tab_style())
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        browser_layout.addWidget(self.tabs)

        self.status = QStatusBar()
        self.status.setStyleSheet("background:#0d0d0d;color:#888;font-size:11px;")
        self.setStatusBar(self.status)

        # AI Panel
        self.ai_panel = AIPanel(self)
        self.splitter.addWidget(self.ai_panel)
        self.splitter.setSizes([1080, 0])

        # Shortcuts
        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(lambda: self.add_tab())
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(lambda: BrowserWindow().show())
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence("Ctrl+Shift+T"), self).activated.connect(self.restore_last_tab)
        QShortcut(QKeySequence("Ctrl+Tab"), self).activated.connect(self.next_tab)
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self).activated.connect(self.prev_tab)
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.reload_page)
        QShortcut(QKeySequence("Ctrl+Shift+A"), self).activated.connect(self.toggle_ai)
        QShortcut(QKeySequence("Ctrl+K"), self).activated.connect(self.show_palette)
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self.add_bookmark)
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.address_bar.setFocus)
        QShortcut(QKeySequence("F12"), self).activated.connect(self.dev_tools)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)
        QShortcut(QKeySequence("F11"), self).activated.connect(self.toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_bar)

        self.closed_tabs = []
        self.add_tab(self.settings_data.get("home", "https://duckduckgo.com"))

        self.apply_dark_theme()
        self.load_features()

    def load_features(self):
        features_dir = Path(__file__).parent / "features"
        if not features_dir.exists():
            return
        for f in sorted(features_dir.glob("feature_*.py")):
            try:
                spec = importlib.util.spec_from_file_location(f.stem, f)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "register"):
                    mod.register(self)
            except Exception as e:
                print(f"[OpenSword Feature Error] {f.name}: {e}")

    def _btn_style(self, bg="#222", fg="#eee"):
        return f"background:{bg};color:{fg};padding:6px 10px;border:none;border-radius:4px;font-size:14px;"

    def _tab_style(self):
        return """
            QTabWidget::pane { border: none; background: #0d0d0d; }
            QTabBar::tab {
                background: #1a1a1a; color: #aaa; padding: 8px 16px;
                border-top-left-radius: 6px; border-top-right-radius: 6px;
                margin-right: 2px; font-size: 13px;
            }
            QTabBar::tab:selected { background: #0d0d0d; color: #0f0; border-bottom: 2px solid #0f0; }
            QTabBar::tab:hover { background: #222; color: #fff; }
            QTabBar::close-button { image: none; }
            QTabBar::close-button:hover { background: #f00; }
        """

    def apply_dark_theme(self):
        self.setStyleSheet("background:#0d0d0d;color:#eee;")

    def add_tab(self, url="about:blank", activate=True):
        tab = WebTab(self)
        tab.load(QUrl(url))
        idx = self.tabs.addTab(tab, "Yeni Sekme")
        if activate:
            self.tabs.setCurrentIndex(idx)
        return tab

    def close_tab(self, idx):
        if self.tabs.count() > 1:
            tab = self.tabs.widget(idx)
            self.closed_tabs.append((tab.url().toString(), tab._title))
            self.tabs.removeTab(idx)
            tab.deleteLater()

    def restore_last_tab(self):
        if self.closed_tabs:
            url, title = self.closed_tabs.pop()
            self.add_tab(url)

    def next_tab(self):
        idx = (self.tabs.currentIndex() + 1) % self.tabs.count()
        self.tabs.setCurrentIndex(idx)

    def prev_tab(self):
        idx = (self.tabs.currentIndex() - 1) % self.tabs.count()
        self.tabs.setCurrentIndex(idx)

    def current_tab(self) -> 'WebTab':
        return self.tabs.currentWidget()

    def current_url(self) -> str:
        tab = self.current_tab()
        return tab.url().toString() if tab else ""

    def load_url(self):
        text = self.address_bar.text().strip()
        if not text:
            return
        if "." in text and " " not in text and not text.startswith(("http://", "https://")):
            text = "https://" + text
        elif not text.startswith(("http://", "https://", "file://")):
            template = self.settings_data.get("search", "https://duckduckgo.com/?q={}")
            text = template.format(text.replace(" ", "+"))
        tab = self.current_tab()
        if tab:
            tab.load(QUrl(text))

    def go_back(self):
        """Onceki sayfaya doner."""
        tab = self.current_tab()
        if tab:
            tab.back()

    def go_forward(self):
        """Sonraki sayfaya gider."""
        tab = self.current_tab()
        if tab:
            tab.forward()

    def reload_page(self):
        """Sayfayi yeniler."""
        tab = self.current_tab()
        if tab:
            tab.reload()

    def go_home(self):
        """Ana sayfaya gider."""
        self.add_tab(self.settings_data.get("home", "https://duckduckgo.com"))

    def tab_changed(self, idx):
        tab = self.tabs.widget(idx)
        if tab:
            self.address_bar.setText(tab.url().toString())
            self.setWindowTitle(f"{tab._title} — OpenSword Browser")

    def update_tab_title(self, tab):
        idx = self.tabs.indexOf(tab)
        if idx >= 0:
            title = tab._title[:20] + "..." if len(tab._title) > 20 else tab._title
            self.tabs.setTabText(idx, title)
            if self.tabs.currentIndex() == idx:
                self.setWindowTitle(f"{tab._title} — OpenSword Browser")
                self.address_bar.setText(tab.url().toString())

    def toggle_ai(self):
        visible = not self.ai_panel.isVisible()
        self.ai_panel.setVisible(visible)
        sizes = self.splitter.sizes()
        if visible:
            self.splitter.setSizes([sizes[0] - 320, 320])
        else:
            self.splitter.setSizes([sizes[0] + sizes[1], 0])

    def add_bookmark(self):
        url = self.current_url()
        title = self.current_tab()._title if self.current_tab() else url
        self.bookmarks.append({"title": title, "url": url})
        save_json(BOOKMARKS_FILE, self.bookmarks)
        self.refresh_bookmarks_bar()
        self.status.showMessage(f"Yer imi eklendi: {title}", 3000)

    def refresh_bookmarks_bar(self):
        while self.bookmarks_bar.count():
            item = self.bookmarks_bar.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for bm in self.bookmarks:
            btn = QPushButton(bm["title"][:20])
            btn.setStyleSheet("background:#1a1a1a;color:#0f0;border:none;padding:4px 8px;font-size:12px;")
            btn.setToolTip(bm["url"])
            btn.clicked.connect(lambda checked, u=bm["url"]: self.add_tab(u))
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda pos, b=btn, u=bm["url"]: self.bookmark_context(pos, b, u))
            self.bookmarks_bar.addWidget(btn)
        self.bookmarks_bar.addStretch()

    def bookmark_context(self, pos, btn, url):
        menu = QMenu(self)
        del_action = menu.addAction("🗑 Sil")
        action = menu.exec(btn.mapToGlobal(pos))
        if action == del_action:
            self.bookmarks = [b for b in self.bookmarks if b["url"] != url]
            save_json(BOOKMARKS_FILE, self.bookmarks)
            self.refresh_bookmarks_bar()

    def show_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("background:#1a1a1a;color:#eee;border:1px solid #333;")
        menu.addAction("Yeni Pencere", lambda: BrowserWindow().show())
        menu.addAction("Gizli Mod", lambda: BrowserWindow(private=True).show())
        menu.addSeparator()
        menu.addAction("Komut Paleti (Ctrl+K)", self.show_palette)
        menu.addAction("Yer imlerini yönet", self.manage_bookmarks)
        menu.addSeparator()
        menu.addAction("Ayarlar", self.open_settings)
        menu.addAction("Hakkında", self.about)
        menu.exec(self.btn_menu.mapToGlobal(self.btn_menu.rect().bottomLeft()))

    def show_palette(self):
        palette = CommandPalette(self)
        palette.exec()

    def manage_bookmarks(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Yer İmleri")
        dlg.setFixedSize(500, 400)
        dlg.setStyleSheet("background:#111;color:#eee;")
        layout = QVBoxLayout(dlg)
        txt = QPlainTextEdit(dlg)
        txt.setPlainText(json.dumps(self.bookmarks, ensure_ascii=False, indent=2))
        txt.setStyleSheet("background:#0a0a0a;color:#0f0;font-family:monospace;")
        layout.addWidget(txt)
        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(lambda: (save_json(BOOKMARKS_FILE, json.loads(txt.toPlainText())), self.refresh_bookmarks_bar(), dlg.accept()))
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)
        dlg.exec()

    def open_settings(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Ayarlar")
        dlg.setFixedSize(400, 250)
        dlg.setStyleSheet("background:#111;color:#eee;")
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel("Ana Sayfa:"))
        home = QLineEdit(self.settings_data.get("home", "https://duckduckgo.com"))
        home.setStyleSheet("background:#222;color:#eee;padding:6px;")
        layout.addWidget(home)
        layout.addWidget(QLabel("Arama Motoru ({} için placeholder):"))
        search = QLineEdit(self.settings_data.get("search", "https://duckduckgo.com/?q={}"))
        search.setStyleSheet("background:#222;color:#eee;padding:6px;")
        layout.addWidget(search)
        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(lambda: (self.settings_data.update({"home": home.text(), "search": search.text()}), save_json(SETTINGS_FILE, self.settings_data), dlg.accept()))
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)
        dlg.exec()

    def about(self):
        QMessageBox.information(self, "Hakkında",
            "<b>OpenSword Browser</b><br>"
            "Versiyon 0.1.0<br>"
            "Lisans: Apache-2.0<br>"
            "Geliştirici: hiimhermes-self<br><br>"
            "Açık kaynak, AI-native, hızlı ve modüler web tarayıcısı.<br>"
            "Rakipler: Dia Browser, Perplexity Comet<br>"
            "Fark: %100 açık kaynak, yerel AI entegrasyonu, topluluk gücü.")

    def zoom_in(self):
        tab = self.current_tab()
        if tab:
            tab.setZoomFactor(tab.zoomFactor() + 0.1)

    def zoom_out(self):
        tab = self.current_tab()
        if tab:
            tab.setZoomFactor(max(0.25, tab.zoomFactor() - 0.1))

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def print_page(self):
        tab = self.current_tab()
        if tab:
            from PySide6.QtWebEngineWidgets import QWebEngineView
            tab.page().printToPdf("/tmp/opensword_page.pdf")
            self.status.showMessage("PDF yazdirildi: /tmp/opensword_page.pdf", 4000)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.statusBar().show()
            self.toolbar.show()
        else:
            self.showFullScreen()
            self.statusBar().hide()
            self.toolbar.hide()

    def save_page(self):
        tab = self.current_tab()
        if tab:
            path, _ = QFileDialog.getSaveFileName(self, "Sayfayi Kaydet", "page.mhtml")
            if path:
                tab.page().save(path, format=QWebEngineDownloadRequest.MimeHtmlSaveFormat)
                self.status.showMessage(f"Sayfa kaydedildi: {path}", 3000)

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def show_find_bar(self):
        from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
        if not hasattr(self, "_find_bar"):
            self._find_bar = QWidget(self)
            layout = QHBoxLayout(self._find_bar)
            layout.setContentsMargins(4, 2, 4, 2)
            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Sayfada ara...")
            self._find_input.setStyleSheet("background:#222;color:#eee;padding:4px;")
            self._find_input.returnPressed.connect(lambda: self.current_tab().page().findText(self._find_input.text()))
            layout.addWidget(self._find_input)
            self.browser_container.layout().addWidget(self._find_bar)
        self._find_bar.setVisible(not self._find_bar.isVisible())
        if self._find_bar.isVisible():
            self._find_input.setFocus()

    def dev_tools(self):
        tab = self.current_tab()
        if tab:
            tab.page().setDevToolsPage(QWebEnginePage(self))
            self.status.showMessage("Geliştirici araçları etkinleştirildi (DevTools penceresi ayrılacak)", 3000)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("OpenSword")
    app.setApplicationDisplayName("OpenSword Browser")
    app.setOrganizationName("hiimhermes-self")
    font = QFont("Inter", 10)
    if not QFont(font).exactMatch():
        font = QFont("Noto Sans", 10)
    app.setFont(font)
    win = BrowserWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
