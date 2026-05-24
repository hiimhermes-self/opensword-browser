def register(win):
    from PySide6.QtWidgets import QPushButton
    from PySide6.QtCore import QUrl
    btn = QPushButton("Uyku")
    btn.setStyleSheet("background:#222;color:#eee;padding:6px 10px;border:none;border-radius:4px;")
    def sleep_inactive():
        for i in range(win.tabs.count()):
            tab = win.tabs.widget(i)
            if tab != win.current_tab():
                tab._sleep_url = tab.url().toString()
                tab.load(QUrl("about:blank"))
                win.tabs.setTabText(i, "[Uyku] " + win.tabs.tabText(i))
    btn.clicked.connect(sleep_inactive)
    win.toolbar.addWidget(btn)
