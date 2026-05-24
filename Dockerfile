FROM archlinux:latest
RUN pacman -Sy --noconfirm python python-pyside6 && pacman -Scc --noconfirm
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt --break-system-packages || pip install -r requirements.txt
CMD ["python", "-m", "opensword.browser"]
