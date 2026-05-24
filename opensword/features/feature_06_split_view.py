def register(win):
    from PySide6.QtWidgets import QSplitter, QPushButton
    from PySide6.QtCore import Qt
    win.split_btn = QPushButton("Bol")
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
