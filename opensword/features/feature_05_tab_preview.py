def register(win):
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
            preview.setText(f"Onizleme:\n{win.tabs.tabText(idx)}\n{tab.url().toString()[:60]}")
        pos = win.tabs.tabBar().tabRect(idx).bottomLeft()
        preview.move(win.mapToGlobal(pos) + QPoint(0, 4))
        preview.show()
    def hide_preview():
        preview.hide()
    win.tabs.tabBar().setMouseTracking(True)
    win.tabs.tabBar().entered.connect(show_preview)
    win.tabs.tabBar().leaved.connect(hide_preview)
