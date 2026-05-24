def register(win):
    from PySide6.QtWidgets import QPushButton
    btn = QPushButton("Oku")
    btn.setStyleSheet("background:#222;color:#0f0;padding:6px 10px;border:none;border-radius:4px;")
    def activate():
        tab = win.current_tab()
        if tab:
            js = """
            (function(){
                var c=document.createElement('style');
                c.innerHTML='body{background:#f5f5f5;color:#222;max-width:700px;margin:40px auto;font-family:serif;line-height:1.6;font-size:18px;}img{max-width:100%;height:auto;}a{color:#0645ad;}';
                document.head.appendChild(c);
                var d=document.createElement('div');
                d.innerHTML='<h1>'+document.title+'</h1>'+document.body.innerHTML;
                document.body.innerHTML='';document.body.appendChild(d);
            })();
            """
            tab.page().runJavaScript(js)
    btn.clicked.connect(activate)
    win.toolbar.addWidget(btn)
