import shutil
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QFileDialog, QMenu,
)
from PySide6.QtCore import Slot

from hep_gui.config.constants import (
    DATA_DIR, RUNS_DIR, ANALYSIS_DIR,
    DOCKER_IMAGE, DOCKER_SHELL, RIVET_ANALYSES,
)
from hep_gui.core.docker_interface import (
    get_docker_client, check_docker, check_image, DockerWorker,
)
from hep_gui.core.rivet_build import (
    build_rivet_command, build_rivetbuild_command,
    hepmc_to_docker_path, yoda_output_name,
)
from hep_gui.gui.log_panel import LogPanel


class AnalysisTab(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._hepmc_path = None
        self._yoda_path = None

        self._build_ui()
        self._connect_signals()
        self._set_state_idle()

    # -- UI --

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # line 1: HepMC file selection
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("HepMC:"))
        self.input_hepmc = QLineEdit()
        self.input_hepmc.setReadOnly(True)
        self.input_hepmc.setPlaceholderText("Select a .hepmc file...")
        row1.addWidget(self.input_hepmc, 1)
        self.btn_browse = QPushButton("Browse")
        row1.addWidget(self.btn_browse)
        layout.addLayout(row1)

        # line 2: analyses
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Analyses:"))
        self.input_analyses = QLineEdit("MC_JETS")
        row2.addWidget(self.input_analyses, 1)
        self.btn_presets = QPushButton("Presets")
        self._build_presets_menu()
        row2.addWidget(self.btn_presets)
        layout.addLayout(row2)

        # line 3: actions
        row3 = QHBoxLayout()
        self.btn_upload_cc = QPushButton("Upload .cc")
        row3.addWidget(self.btn_upload_cc)
        self.btn_run = QPushButton("Run Rivet")
        row3.addWidget(self.btn_run)
        self.btn_cancel = QPushButton("Cancel")
        row3.addWidget(self.btn_cancel)
        self.label_status = QLabel("Ready")
        row3.addWidget(self.label_status)
        row3.addStretch()
        layout.addLayout(row3)

        # log panel
        self.log_panel = LogPanel()
        layout.addWidget(self.log_panel)

    def _build_presets_menu(self):
        menu = QMenu(self)
        for tier, analyses in RIVET_ANALYSES.items():
            sub = menu.addMenu(tier)
            for name in analyses:
                action = sub.addAction(name)
                action.triggered.connect(lambda checked, n=name: self._insert_analysis(n))
        self.btn_presets.setMenu(menu)

    def _connect_signals(self):
        self.btn_browse.clicked.connect(self._on_browse)
        self.btn_run.clicked.connect(self.start_run)
        self.btn_cancel.clicked.connect(self.cancel_run)
        self.btn_upload_cc.clicked.connect(self._on_upload_cc)

    # -- state management --

    def _set_state_idle(self):
        has_hepmc = self._hepmc_path is not None
        self.btn_run.setEnabled(has_hepmc)
        self.btn_cancel.setEnabled(False)
        self.btn_upload_cc.setEnabled(True)

    def _set_state_running(self):
        self.btn_run.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.btn_upload_cc.setEnabled(False)
        self.label_status.setText("Running...")

    def _set_state_finished(self, success):
        self.btn_run.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.btn_upload_cc.setEnabled(True)
        self.label_status.setText("Finished" if success else "Error")

    # -- public API --

    def set_hepmc_path(self, path):
        """Pre-fill the HepMC path (for pipeline integration)."""
        self._hepmc_path = path
        self.input_hepmc.setText(str(path))
        self._set_state_idle()

    def get_yoda_path(self):
        """Return the last generated .yoda path, or None."""
        return self._yoda_path

    # -- browse / presets --

    def _on_browse(self):
        start_dir = str(RUNS_DIR) if RUNS_DIR.exists() else ""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select HepMC file", start_dir,
            "HepMC files (*.hepmc *.hepmc.gz);;All files (*)",
        )
        if path:
            self.set_hepmc_path(path)

    def _insert_analysis(self, name):
        current = self.input_analyses.text().strip()
        if current:
            # don't add duplicates
            existing = [a.strip() for a in current.split(",")]
            if name in existing:
                return
            self.input_analyses.setText(current + ", " + name)
        else:
            self.input_analyses.setText(name)

    # -- run rivet --

    def start_run(self):
        if not self._hepmc_path:
            self.log_panel.append_line("ERROR: no HepMC file selected")
            return

        analyses_text = self.input_analyses.text().strip()
        if not analyses_text:
            self.log_panel.append_line("ERROR: no analyses specified")
            return

        ok, info = check_docker()
        if not ok:
            self.log_panel.append_line(f"ERROR: Docker not running -- {info}")
            return

        client = get_docker_client()
        if not client:
            self.log_panel.append_line("ERROR: cannot connect to Docker")
            return

        if not check_image(client, DOCKER_IMAGE):
            self.log_panel.append_line(f"ERROR: image {DOCKER_IMAGE} not found locally")
            return

        analyses = [a.strip() for a in analyses_text.split(",") if a.strip()]
        docker_hepmc = hepmc_to_docker_path(self._hepmc_path)
        yoda_name = yoda_output_name(self._hepmc_path)
        yoda_docker = f"/data/analysis/{yoda_name}"

        cmd = build_rivet_command(analyses, docker_hepmc, yoda_docker)
        volumes = {str(DATA_DIR): {"bind": "/data", "mode": "rw"}}

        self.log_panel.clear()
        self.log_panel.append_line(f"--- Running Rivet: {', '.join(analyses)} ---")
        self.log_panel.append_line(f"Input: {docker_hepmc}")
        self.log_panel.append_line(f"Output: {yoda_docker}")

        self._yoda_path = ANALYSIS_DIR / yoda_name

        self._worker = DockerWorker(client, DOCKER_IMAGE, cmd, volumes=volumes)
        self._worker.log_line.connect(self.log_panel.append_line)
        self._worker.finished.connect(self._on_run_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()
        self._set_state_running()

    def cancel_run(self):
        if self._worker:
            self._worker.stop_container()
            self.log_panel.append_line("--- Run cancelled ---")

    # -- upload .cc --

    def _on_upload_cc(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Rivet analysis .cc", "",
            "C++ files (*.cc);;All files (*)",
        )
        if not path:
            return

        src = Path(path)
        ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
        dst = ANALYSIS_DIR / src.name
        shutil.copy2(src, dst)
        self.log_panel.append_line(f"Copied {src.name} to {ANALYSIS_DIR}")

        # build the .so in Docker
        ok, info = check_docker()
        if not ok:
            self.log_panel.append_line(f"ERROR: Docker not running -- {info}")
            return

        client = get_docker_client()
        if not client:
            self.log_panel.append_line("ERROR: cannot connect to Docker")
            return

        if not check_image(client, DOCKER_IMAGE):
            self.log_panel.append_line(f"ERROR: image {DOCKER_IMAGE} not found locally")
            return

        cmd = build_rivetbuild_command(src.name)
        volumes = {str(DATA_DIR): {"bind": "/data", "mode": "rw"}}

        self.log_panel.append_line(f"--- Building {src.name} with rivet-build ---")

        self._worker = DockerWorker(client, DOCKER_IMAGE, cmd, volumes=volumes)
        self._worker.log_line.connect(self.log_panel.append_line)
        self._worker.finished.connect(self._on_build_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()
        self._set_state_running()

    # -- slots --

    @Slot(int)
    def _on_run_finished(self, exit_code):
        success = exit_code == 0 and self._yoda_path and self._yoda_path.exists()

        if success:
            self.log_panel.append_line(f"--- Rivet finished, output: {self._yoda_path} ---")
        else:
            self.log_panel.append_line(f"--- Rivet failed (exit code {exit_code}) ---")

        self._set_state_finished(success)
        self._worker = None

    @Slot(int)
    def _on_build_finished(self, exit_code):
        if exit_code == 0:
            self.log_panel.append_line("--- rivet-build finished ---")
        else:
            self.log_panel.append_line(f"--- rivet-build failed (exit code {exit_code}) ---")

        self._set_state_finished(exit_code == 0)
        self._worker = None

    @Slot(str)
    def _on_error(self, msg):
        self.log_panel.append_line(f"ERROR: {msg}")
        self._set_state_finished(False)
        self._worker = None
