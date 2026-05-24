def register(win):
    orig_load = win.load_url
    def load_hook():
        text = win.address_bar.text().strip()
        if text.lower().endswith(".pdf"):
            win.status.showMessage("PDF destegi yakinda.", 4000)
        orig_load()
    win.load_url = load_hook
