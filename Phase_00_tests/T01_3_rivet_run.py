# T01_3_rivet_run.py -- run Rivet analysis + rivet-mkhtml in Docker

import sys
from pathlib import Path
import docker
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget,
)
from PySide6.QtCore import QThread, Signal
import config

HEPMC_FILE = "/data/runs/test_ggH_100/Events/run_01/tag_1_pythia8_events.hepmc.gz"
YODA_OUTPUT = "/data/analysis/test_ggH_100.yoda"
MKHTML_DIR = "/data/analysis/test_ggH_100_plots"
ANALYSIS = "MC_JETS"

YODA_LOCAL = config.ANALYSIS_DIR / "test_ggH_100.yoda"
PLOTS_LOCAL = config.ANALYSIS_DIR / "test_ggH_100_plots"


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
        self.setWindowTitle("T01_3: Rivet analysis")
        self.worker = None

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)

        self.run_btn = QPushButton("Run Rivet")
        self.run_btn.clicked.connect(self.on_run_rivet)

        self.mkhtml_btn = QPushButton("Run mkhtml (4.0.2)")
        self.mkhtml_btn.clicked.connect(self.on_run_mkhtml)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.on_cancel)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.mkhtml_btn)
        btn_row.addWidget(self.cancel_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.log_view)
        layout.addLayout(btn_row)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _set_running(self, running):
        self.run_btn.setEnabled(not running)
        self.mkhtml_btn.setEnabled(not running)
        self.cancel_btn.setEnabled(running)

    def _start_worker(self, image, cmd):
        self._set_running(True)
        self.log_view.clear()
        client = docker.from_env()
        volumes = {str(config.DATA_DIR): {"bind": "/data", "mode": "rw"}}
        self.worker = DockerWorker(client, image, cmd, volumes)
        self.worker.log_line.connect(self.log_view.append)
        self.worker.finished_with_code.connect(self.on_done)
        self.worker.start()

    def on_run_rivet(self):
        rivet_cmd = f"rivet --analysis={ANALYSIS} {HEPMC_FILE} -o {YODA_OUTPUT}"
        cmd = f'{config.DOCKER_SHELL} "mkdir -p /data/analysis && {rivet_cmd}"'
        self._start_worker(config.DOCKER_IMAGE, cmd)

    def on_run_mkhtml(self):
        # 4.1.2 has broken ROOT/cling (segfault on import yoda), use 4.0.2 for mkhtml
        mkhtml_cmd = f"rivet-mkhtml {YODA_OUTPUT} -o {MKHTML_DIR}"
        cmd = f'{config.DOCKER_SHELL} "{mkhtml_cmd}"'
        self._start_worker(config.DOCKER_IMAGE_MKHTML, cmd)

    def on_cancel(self):
        if self.worker:
            self.worker.stop_container()

    def on_done(self, exit_code):
        self.log_view.append(f"--- exit code: {exit_code} ---")
        self.check_output()
        self._set_running(False)

    def check_output(self):
        self.log_view.append("--- output check ---")

        if YODA_LOCAL.exists():
            size_mb = YODA_LOCAL.stat().st_size / 1024 / 1024
            self.log_view.append(f"  .yoda file: {size_mb:.1f} MB")
        else:
            self.log_view.append("  .yoda file: NOT FOUND")

        if PLOTS_LOCAL.exists() and PLOTS_LOCAL.is_dir():
            png_count = len(list(PLOTS_LOCAL.rglob("*.png")))
            pdf_count = len(list(PLOTS_LOCAL.rglob("*.pdf")))
            self.log_view.append(f"  plots: {png_count} PNG, {pdf_count} PDF")
            index = PLOTS_LOCAL / "index.html"
            if index.exists():
                self.log_view.append("  index.html: OK")
            else:
                self.log_view.append("  index.html: NOT FOUND")
        else:
            self.log_view.append("  plots dir: NOT FOUND")


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec())
