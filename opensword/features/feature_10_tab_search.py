def register(win):
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
