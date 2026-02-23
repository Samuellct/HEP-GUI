# T01_2_madgraph_run.py -- run MG5+Pythia8 in Docker

import sys
from pathlib import Path
import docker
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget,
)
from PySide6.QtCore import QThread, Signal
import config

SCRIPT_NAME = "test_ggH_100"
MG5_SCRIPT = f"/data/scripts/{SCRIPT_NAME}.txt"
# MG5 outputs to /work/ (container-local) to avoid NTFS exec issues, then we copy results back to /data/runs/
CONTAINER_RUN = f"/work/{SCRIPT_NAME}"
RUN_DIR = config.RUNS_DIR / SCRIPT_NAME / "Events" / "run_01"


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
        self.setWindowTitle("T01_2: MadGraph run")
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
        mg5_cmd = f"{config.MG5_BIN} {MG5_SCRIPT}"
        copy_cmd = f"cp -r {CONTAINER_RUN}/Events /data/runs/{SCRIPT_NAME}/"
        # MG5 crashes on quit (auto_update bug), so use ; to always run copy
        cmd = (
            f'{config.DOCKER_SHELL} "'
            f"export LD_PRELOAD={config.PYTHIA8_LIB}/libpythia8.so"
            f" && {mg5_cmd}"
            f"; mkdir -p /data/runs/{SCRIPT_NAME} && {copy_cmd}\""
        )
        volumes = {str(config.DATA_DIR): {"bind": "/data", "mode": "rw"}}

        self.worker = DockerWorker(client, config.DOCKER_IMAGE, cmd, volumes)
        self.worker.log_line.connect(self.log_view.append)
        self.worker.finished_with_code.connect(self.on_done)
        self.worker.start()

    def on_cancel(self):
        if self.worker:
            self.worker.stop_container()

    def on_done(self, exit_code):
        self.log_view.append(f"--- exit code: {exit_code} ---")
        self.list_output_files()
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

    def list_output_files(self):
        self.log_view.append("--- output files ---")
        if not RUN_DIR.exists():
            self.log_view.append("  (no output directory found)")
            return
        files = sorted(RUN_DIR.iterdir())
        if not files:
            self.log_view.append("  (directory empty)")
            return
        for f in files:
            self.log_view.append(f"  {f.name}")


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec())
