def register(win):
    from PySide6.QtWidgets import QPushButton, QInputDialog, QMessageBox
    from PySide6.QtCore import Qt
    import json
    ws_file = Path.home() / ".config" / "opensword" / "workspaces.json"
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
