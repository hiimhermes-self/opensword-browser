def register(win):
    import os
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    if "gnome" in desktop or "kde" in desktop:
        win.status.showMessage("Otomatik koyu mod: sistem temasi algilandi.", 3000)
