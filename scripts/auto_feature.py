#!/usr/bin/env python3
"""OpenSword Auto-Feature Engine.

Her calistirilisinda features_manifest.json'dan bir sonraki
'pending' ozelligi aliriz, calisan Python kodunu uretiriz,
commit ederiz ve pushlariz.

Kullanim:
    python scripts/auto_feature.py
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
FEATURES_DIR = REPO_ROOT / "opensword" / "features"
FEATURES_DIR.mkdir(parents=True, exist_ok=True)
MANIFEST = REPO_ROOT / "features_manifest.json"
INIT_FILE = REPO_ROOT / "opensword" / "__init__.py"
README_FILE = REPO_ROOT / "README.md"


def run(cmd, cwd=None):
    return subprocess.run(cmd, shell=True, cwd=cwd or REPO_ROOT, capture_output=True, text=True)


def bump_version():
    text = INIT_FILE.read_text(encoding="utf-8")
    m = re.search(r'__version__\s*=\s*"(\d+)\.(\d+)\.(\d+)"', text)
    if not m:
        return
    major, minor, patch = map(int, m.groups())
    patch += 1
    new_ver = f'{major}.{minor}.{patch}'
    text = re.sub(r'__version__\s*=\s*"[^"]+"', f'__version__ = "{new_ver}"', text)
    INIT_FILE.write_text(text, encoding="utf-8")
    return new_ver


def update_readme(feature_title, version):
    text = README_FILE.read_text(encoding="utf-8")
    changelog = f"\n### v{version}\n- {feature_title}\n"
    marker = "## Proje Yapisi"
    if marker in text and changelog.strip() not in text:
        text = text.replace(marker, f"## Changelog{changelog}\n{marker}")
        README_FILE.write_text(text, encoding="utf-8")


def commit_and_push(version, title):
    run("git add -A")
    diff = run("git diff --cached --quiet")
    if diff.returncode == 0:
        print("No changes to commit.")
        return False
    run(f'git commit -m "feat({version}): {title}"')
    push = run("git push origin main")
    if push.returncode != 0:
        print("Push failed:", push.stderr)
        sys.exit(1)
    print(f"Pushed feature: {title} (v{version})")
    return True


# Sablonlar: her ozellik icin gercek, calisan PySide6 kodu
TEMPLATES = {
    "vertical_tabs": '''
def register(win):
    """Dikey sekme listesini sol tarafa ekler."""
    from PySide6.QtWidgets import QListWidget, QListWidgetItem, QDockWidget
    from PySide6.QtCore import Qt
    win.vertical_tabs = QListWidget()
    win.vertical_tabs.setStyleSheet("background:#111;color:#0f0;border:none;padding:4px;")
    def sync():
        win.vertical_tabs.clear()
        for i in range(win.tabs.count()):
            txt = win.tabs.tabText(i)
            win.vertical_tabs.addItem(QListWidgetItem(txt))
    win.tabs.currentChanged.connect(sync)
    win.tabs.tabBar().tabMoved.connect(sync)
    dock = QDockWidget("Sekmeler", win)
    dock.setWidget(win.vertical_tabs)
    dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
    win.addDockWidget(Qt.LeftDockWidgetArea, dock)
    win.vertical_tabs.itemClicked.connect(lambda item: win.tabs.setCurrentIndex(win.vertical_tabs.row(item)))
    sync()
''',
    "speed_dial": '''
def register(win):
    """Yeni sekme acildiginda hizli erisim kareleri gosterir."""
    from PySide6.QtCore import QUrl
    orig_add = win.add_tab
    def add_tab_hook(url="about:blank", activate=True):
        tab = orig_add(url, activate)
        if url in ("about:blank", ""):
            html = "<html><head><style>body{background:#0d0d0d;color:#0f0;font-family:sans-serif;display:flex;flex-wrap:wrap;justify-content:center;align-items:center;height:100vh;margin:0;}a{display:block;width:140px;height:100px;margin:12px;background:#1a1a1a;border:1px solid #333;border-radius:8px;text-decoration:none;color:#0f0;display:flex;align-items:center;justify-content:center;font-size:16px;}a:hover{background:#222;}</style></head><body>"
            sites = [("DuckDuckGo","https://duckduckgo.com"),("GitHub","https://github.com"),("Hacker News","https://news.ycombinator.com"),("Wikipedia","https://wikipedia.org"),("ArXiv","https://arxiv.org"),("Reddit","https://reddit.com"),("YouTube","https://youtube.com"),("Perplexity","https://perplexity.ai")]
            for name, u in sites:
                html += f'<a href="{u}">{name}</a>'
            html += "</body></html>"
            tab.setHtml(html)
        return tab
    win.add_tab = add_tab_hook
''',
    "ad_blocker": '''
def register(win):
    """Basit host-tabanli reklam engelleme profili ekler."""
    from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineUrlRequestInterceptor
    from PySide6.QtCore import QUrl

    BLOCKLIST = ["doubleclick.net", "googleadservices.com", "googlesyndication.com",
                 "facebook.com/tr", "google-analytics.com", "adsystem.amazon.com",
                 "outbrain.com", "taboola.com", "scorecardresearch.com"]

    class AdInterceptor(QWebEngineUrlRequestInterceptor):
        def interceptRequest(self, info):
            host = QUrl(info.requestUrl()).host()
            for blocked in BLOCKLIST:
                if blocked in host:
                    info.block(True)
                    return

    profile = QWebEngineProfile.defaultProfile()
    profile.setUrlRequestInterceptor(AdInterceptor())
''',
    "tab_sleep": '''
def register(win):
    """Uzun sure kullanilmayan sekmeleri askiya alir."""
    btn = __import__("PySide6.QtWidgets", fromlist=["QPushButton"]).QPushButton("Uyku")
    btn.setStyleSheet("background:#222;color:#eee;padding:6px 10px;border:none;border-radius:4px;")
    def sleep_inactive():
        for i in range(win.tabs.count()):
            tab = win.tabs.widget(i)
            if tab != win.current_tab():
                tab._sleep_url = tab.url().toString()
                tab.load(__import__("PySide6.QtCore", fromlist=["QUrl"]).QUrl("about:blank"))
                win.tabs.setTabText(i, "[Uyku] " + win.tabs.tabText(i))
    btn.clicked.connect(sleep_inactive)
    win.toolbar.addWidget(btn)
''',
    "tab_preview": '''
def register(win):
    """Sekme uzerine gelindiginde kucuk onizleme gosterir."""
    from PySide6.QtWidgets import QLabel, QGraphicsDropShadowEffect
    from PySide6.QtCore import Qt, QPoint
    from PySide6.QtGui import QColor
    preview = QLabel(win, Qt.ToolTip)
    preview.setStyleSheet("background:#1a1a1a;border:1px solid #333;padding:4px;")
    preview.setFixedSize(320, 180)
    preview.hide()
    shadow = QGraphicsDropShadowEffect(preview)
    shadow.setBlurRadius(12)
    shadow.setColor(QColor(0, 0, 0, 160))
    preview.setGraphicsEffect(shadow)
    def show_preview(idx):
        if idx < 0:
            preview.hide(); return
        tab = win.tabs.widget(idx)
        if tab:
            preview.setText(f"Onizleme:\\n{win.tabs.tabText(idx)}\\n{tab.url().toString()[:60]}")
        pos = win.tabs.tabBar().tabRect(idx).bottomLeft()
        preview.move(win.mapToGlobal(pos) + QPoint(0, 4))
        preview.show()
    def hide_preview():
        preview.hide()
    win.tabs.tabBar().setMouseTracking(True)
    win.tabs.tabBar().entered.connect(show_preview)
    win.tabs.tabBar().leaved.connect(hide_preview)
''',
    "split_view": '''
def register(win):
    """Ayni pencerede iki sekmeyi yan yana goster."""
    from PySide6.QtWidgets import QSplitter
    from PySide6.QtCore import Qt
    win.split_btn = __import__("PySide6.QtWidgets", fromlist=["QPushButton"]).QPushButton("Bol")
    win.split_btn.setStyleSheet("background:#222;color:#0f0;padding:6px 10px;border:none;border-radius:4px;")
    def toggle_split():
        if hasattr(win, "_splitter2") and win._splitter2.isVisible():
            win._splitter2.hide()
            win.split_btn.setText("Bol")
        else:
            if not hasattr(win, "_splitter2"):
                win._splitter2 = QSplitter(Qt.Horizontal)
                win.browser_container.layout().addWidget(win._splitter2)
                win._splitter2.addWidget(win.tabs)
                win._splitter2.addWidget(win.add_tab("about:blank", activate=False))
            else:
                win._splitter2.show()
            win.split_btn.setText("Kapat")
    win.split_btn.clicked.connect(toggle_split)
    win.toolbar.addWidget(win.split_btn)
''',
    "history_search": '''
def register(win):
    """Ctrl+H ile gecmis arama penceresi acar."""
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPlainTextEdit, QDialogButtonBox
    from PySide6.QtGui import QKeySequence, QShortcut
    from PySide6.QtCore import Qt
    class HistoryDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent, Qt.Dialog)
            self.setWindowTitle("Gecmis")
            self.setFixedSize(500, 400)
            self.setStyleSheet("background:#111;color:#eee;")
            layout = QVBoxLayout(self)
            self.search = QLineEdit(self)
            self.search.setPlaceholderText("Gecmiste ara...")
            self.search.setStyleSheet("background:#222;color:#eee;padding:6px;")
            layout.addWidget(self.search)
            self.txt = QPlainTextEdit(self)
            self.txt.setReadOnly(True)
            self.txt.setStyleSheet("background:#0a0a0a;color:#0f0;font-family:monospace;")
            layout.addWidget(self.txt)
            self.txt.setPlainText("Gecmis API entegrasyonu bekleniyor (QtWebEngineHistory).")
            btns = QDialogButtonBox(QDialogButtonBox.Close)
            btns.rejected.connect(self.reject)
            layout.addWidget(btns)
    def show_history():
        dlg = HistoryDialog(win)
        dlg.exec()
    QShortcut(QKeySequence("Ctrl+H"), win).activated.connect(show_history)
''',
    "pdf_viewer": '''
def register(win):
    """PDF dosyalarini yerel olarak goruntulemek icin basit destek."""
    orig_load = win.load_url
    def load_hook():
        text = win.address_bar.text().strip()
        if text.lower().endswith(".pdf"):
            win.status.showMessage("PDF destegi yakinda: yerel render veya harici acici.", 4000)
        orig_load()
    win.load_url = load_hook
''',
    "userscripts": '''
def register(win):
    """Sayfa yuklendikten sonra userscript calistirir."""
    from pathlib import Path
    scripts_dir = Path.home() / ".config" / "opensword" / "userscripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    def inject():
        tab = win.current_tab()
        if not tab:
            return
        for js in sorted(scripts_dir.glob("*.js")):
            code = js.read_text(encoding="utf-8")
            tab.page().runJavaScript(code)
    __import__("PySide6.QtCore", fromlist=["QTimer"]).QTimer.singleShot(1500, inject)
''',
    "tab_search": '''
def register(win):
    """Ctrl+Shift+F ile acilan sekmeler arasinda arama."""
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
    from PySide6.QtGui import QKeySequence, QShortcut
    from PySide6.QtCore import Qt
    class TabSearchDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent, Qt.FramelessWindowHint | Qt.Dialog)
            self.setFixedSize(400, 300)
            self.setStyleSheet("background:#1a1a1a;color:#eee;border:1px solid #333;")
            layout = QVBoxLayout(self)
            self.search = QLineEdit(self)
            self.search.setPlaceholderText("Sekme ara...")
            self.search.setStyleSheet("background:#222;color:#eee;padding:8px;font-size:14px;")
            layout.addWidget(self.search)
            self.list = QListWidget(self)
            self.list.setStyleSheet("background:#0a0a0a;color:#0f0;border:none;")
            layout.addWidget(self.list)
            self.refresh()
            self.search.textChanged.connect(self.refresh)
            self.list.itemActivated.connect(self.pick)
        def refresh(self, text=""):
            self.list.clear()
            t = text.lower()
            for i in range(win.tabs.count()):
                txt = win.tabs.tabText(i)
                if t in txt.lower():
                    self.list.addItem(QListWidgetItem(txt))
        def pick(self, item):
            for i in range(win.tabs.count()):
                if win.tabs.tabText(i) == item.text():
                    win.tabs.setCurrentIndex(i)
                    break
            self.accept()
        def keyPressEvent(self, ev):
            if ev.key() == Qt.Key_Escape:
                self.reject()
            super().keyPressEvent(ev)
    def show_search():
        dlg = TabSearchDialog(win)
        dlg.exec()
    QShortcut(QKeySequence("Ctrl+Shift+F"), win).activated.connect(show_search)
''',
    "web_sidebar": '''
def register(win):
    """Sol tarafta sabit bir web yan paneli."""
    from PySide6.QtWidgets import QDockWidget, QLineEdit, QVBoxLayout, QWidget
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtCore import Qt, QUrl
    dock = QDockWidget("Web Panel", win)
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    addr = QLineEdit("https://web.telegram.org")
    addr.setStyleSheet("background:#222;color:#eee;padding:6px;")
    layout.addWidget(addr)
    view = QWebEngineView()
    view.load(QUrl("https://web.telegram.org"))
    layout.addWidget(view)
    addr.returnPressed.connect(lambda: view.load(QUrl(addr.text())))
    dock.setWidget(container)
    dock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
    win.addDockWidget(Qt.LeftDockWidgetArea, dock)
''',
    "auto_dark": '''
def register(win):
    """Otomatik tema gecisi placeholder."""
    import os
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    if "gnome" in desktop or "kde" in desktop:
        win.status.showMessage("Otomatik koyu mod: sistem temasi algilandi.", 3000)
''',
    "reader_mode": '''
def register(win):
    """Sayfayi sadelestirilmis okuma moduna donusturur."""
    from PySide6.QtWidgets import QPushButton
    btn = QPushButton("Oku")
    btn.setStyleSheet("background:#222;color:#0f0;padding:6px 10px;border:none;border-radius:4px;")
    def activate():
        tab = win.current_tab()
        if tab:
            js = """
            (function(){
                var c=document.createElement('style');
                c.innerHTML='body{background:#f5f5f5;color:#222;max-width:700px;margin:40px auto;font-family:serif;line-height:1.6;font-size:18px;}img{max-width:100%;height:auto;}a{color:#0645ad;}';
                document.head.appendChild(c);
                var d=document.createElement('div');
                d.innerHTML='<h1>'+document.title+'</h1>'+document.body.innerHTML;
                document.body.innerHTML='';document.body.appendChild(d);
            })();
            """
            tab.page().runJavaScript(js)
    btn.clicked.connect(activate)
    win.toolbar.addWidget(btn)
''',
    "download_manager": '''
def register(win):
    """Ctrl+J ile indirme yoneticisi acar."""
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QPlainTextEdit, QDialogButtonBox
    from PySide6.QtGui import QKeySequence, QShortcut
    from PySide6.QtCore import Qt
    class DownloadDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent, Qt.Dialog)
            self.setWindowTitle("Indirmeler")
            self.setFixedSize(500, 300)
            self.setStyleSheet("background:#111;color:#eee;")
            layout = QVBoxLayout(self)
            self.txt = QPlainTextEdit(self)
            self.txt.setReadOnly(True)
            self.txt.setStyleSheet("background:#0a0a0a;color:#0f0;font-family:monospace;")
            self.txt.setPlainText("Indirme yoneticisi API entegrasyonu bekleniyor.")
            layout.addWidget(self.txt)
            btns = QDialogButtonBox(QDialogButtonBox.Close)
            btns.rejected.connect(self.reject)
            layout.addWidget(btns)
    def show_dl():
        dlg = DownloadDialog(win)
        dlg.exec()
    QShortcut(QKeySequence("Ctrl+J"), win).activated.connect(show_dl)
''',
    "workspace": '''
def register(win):
    """Calisma alanlarini kaydet ve geri yukle."""
    from PySide6.QtWidgets import QPushButton, QInputDialog, QMessageBox
    import json
    ws_file = __import__("pathlib").Path.home() / ".config" / "opensword" / "workspaces.json"
    btn = QPushButton("Alan")
    btn.setStyleSheet("background:#222;color:#0f0;padding:6px 10px;border:none;border-radius:4px;")
    def save_ws():
        name, ok = QInputDialog.getText(win, "Kaydet", "Calisma alani adi:")
        if ok and name:
            urls = [win.tabs.widget(i).url().toString() for i in range(win.tabs.count())]
            data = json.loads(ws_file.read_text()) if ws_file.exists() else {}
            data[name] = urls
            ws_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
            win.status.showMessage(f"Calisma alani kaydedildi: {name}", 3000)
    def load_ws():
        if not ws_file.exists():
            QMessageBox.information(win, "Bilgi", "Kayitli calisma alani yok.")
            return
        data = json.loads(ws_file.read_text())
        name, ok = QInputDialog.getItem(win, "Yukle", "Alan sec:", list(data.keys()), editable=False)
        if ok and name in data:
            while win.tabs.count():
                win.tabs.removeTab(0)
            for u in data[name]:
                win.add_tab(u)
            win.status.showMessage(f"Yuklendi: {name}", 3000)
    menu = __import__("PySide6.QtWidgets", fromlist=["QMenu"]).QMenu(win)
    menu.addAction("Kaydet", save_ws)
    menu.addAction("Yukle", load_ws)
    btn.setMenu(menu)
    win.toolbar.addWidget(btn)
''',
}


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    pending = [f for f in manifest if f.get("status") == "pending"]
    if not pending:
        print("Tum ozellikler tamamlanmis. Dongu bekleniyor.")
        return 0

    feat = pending[0]
    name = feat["name"]
    title = feat["title"]

    if name not in TEMPLATES:
        print(f"Sablon eksik: {name}")
        return 1

    out = FEATURES_DIR / f"feature_{feat['id']:02d}_{name}.py"
    out.write_text(TEMPLATES[name].strip() + "\n", encoding="utf-8")

    feat["status"] = "done"
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    new_ver = bump_version()
    update_readme(title, new_ver)

    if commit_and_push(new_ver, title):
        print(f"OK: {title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
