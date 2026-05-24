# SPDX-License-Identifier: Apache-2.0
"""Basit sayfa kaynagi goruntuleyici."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPlainTextEdit, QDialogButtonBox
from PySide6.QtCore import Qt

class SourceViewer(QDialog):
    def __init__(self, html, parent=None):
        super().__init__(parent, Qt.Dialog)
        self.setWindowTitle("Sayfa Kaynagi")
        self.setFixedSize(700, 500)
        self.setStyleSheet("background:#0a0a0a;color:#0f0;")
        layout = QVBoxLayout(self)
        self.txt = QPlainTextEdit(self)
        self.txt.setPlainText(html)
        self.txt.setStyleSheet("background:#0a0a0a;color:#0f0;font-family:monospace;")
        layout.addWidget(self.txt)
        btns = QDialogButtonBox(QDialogButtonBox.Close)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
