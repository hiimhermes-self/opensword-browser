def register(win):
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
