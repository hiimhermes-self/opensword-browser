def register(win):
    from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineUrlRequestInterceptor
    from PySide6.QtCore import QUrl
    BLOCKLIST = ["doubleclick.net", "googleadservices.com", "googlesyndication.com",
                 "facebook.com/tr", "google-analytics.com", "adsystem.amazon.com",
                 "outbrain.com", "taboola.com", "scorecardresearch.com"]
    class AdInterceptor(QWebEngineUrlRequestInterceptor):
        def interceptRequest(self, info):
            host = QUrl(info.requestUrl()).host()
            for blocked in BLOCKLIST:
                if blocked in host:
                    info.block(True)
                    return
    QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(AdInterceptor())
