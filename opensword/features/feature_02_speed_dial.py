def register(win):
    from PySide6.QtCore import QUrl
    orig_add = win.add_tab
    def add_tab_hook(url="about:blank", activate=True):
        tab = orig_add(url, activate)
        if url in ("about:blank", ""):
            html = "<html><head><style>body{background:#0d0d0d;color:#0f0;font-family:sans-serif;display:flex;flex-wrap:wrap;justify-content:center;align-items:center;height:100vh;margin:0;}a{display:block;width:140px;height:100px;margin:12px;background:#1a1a1a;border:1px solid #333;border-radius:8px;text-decoration:none;color:#0f0;display:flex;align-items:center;justify-content:center;font-size:16px;}a:hover{background:#222;}</style></head><body>"
            sites = [("DuckDuckGo","https://duckduckgo.com"),("GitHub","https://github.com"),("Hacker News","https://news.ycombinator.com"),("Wikipedia","https://wikipedia.org"),("ArXiv","https://arxiv.org"),("Reddit","https://reddit.com"),("YouTube","https://youtube.com"),("Perplexity","https://perplexity.ai")]
            for name, u in sites:
                html += f'<a href="{u}">{name}</a>'
            html += "</body></html>"
            tab.setHtml(html)
        return tab
    win.add_tab = add_tab_hook
