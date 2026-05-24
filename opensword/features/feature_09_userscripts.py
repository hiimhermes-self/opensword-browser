def register(win):
    from pathlib import Path
    scripts_dir = Path.home() / ".config" / "opensword" / "userscripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    def inject():
        tab = win.current_tab()
        if not tab:
            return
        for js in sorted(scripts_dir.glob("*.js")):
            code = js.read_text(encoding="utf-8")
            tab.page().runJavaScript(code)
    __import__("PySide6.QtCore", fromlist=["QTimer"]).QTimer.singleShot(1500, inject)
