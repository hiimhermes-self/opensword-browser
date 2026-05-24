def register(win):
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
