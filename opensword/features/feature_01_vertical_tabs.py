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
