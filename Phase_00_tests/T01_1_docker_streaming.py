# T01_1_docker_streaming.py

import sys
import docker
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget,
)
from PySide6.QtCore import QThread, Signal
import config


class DockerWorker(QThread):
    log_line = Signal(str)
    finished_with_code = Signal(int)

    def __init__(self, client, image, cmd, volumes=None):
        super().__init__()
        self.client = client
        self.image = image
        self.cmd = cmd
        self.volumes = volumes
        self.container = None

    def run(self):
        self.container = self.client.containers.run(
            self.image, self.cmd, volumes=self.volumes, detach=True,
        )
        for chunk in self.container.logs(stream=True):
            line = chunk.decode().rstrip()
            if line:
                self.log_line.emit(line)
        result = self.container.wait()
        self.container.remove()
        self.container = None
        self.finished_with_code.emit(result["StatusCode"])

    def stop_container(self):
        if self.container:
            self.container.kill()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("T01_1: Docker log streaming")
        self.worker = None

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)

        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.on_run)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.on_cancel)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.cancel_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.log_view)
        layout.addLayout(btn_row)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_run(self):
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.log_view.clear()

        client = docker.from_env()
        cmd = f'{config.DOCKER_SHELL} "for i in $(seq 1 10); do echo line_$i; sleep 0.3; done"'

        self.worker = DockerWorker(client, config.DOCKER_IMAGE, cmd)
        self.worker.log_line.connect(self.log_view.append)
        self.worker.finished_with_code.connect(self.on_done)
        self.worker.start()

    def on_cancel(self):
        if self.worker:
            self.worker.stop_container()

    def on_done(self, exit_code):
        self.log_view.append(f"--- exit code: {exit_code} ---")
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec())
