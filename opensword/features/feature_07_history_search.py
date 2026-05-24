def register(win):
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
            self.txt.setPlainText("Gecmis API entegrasyonu bekleniyor.")
            btns = QDialogButtonBox(QDialogButtonBox.Close)
            btns.rejected.connect(self.reject)
            layout.addWidget(btns)
    def show_history():
        dlg = HistoryDialog(win)
        dlg.exec()
    QShortcut(QKeySequence("Ctrl+H"), win).activated.connect(show_history)
