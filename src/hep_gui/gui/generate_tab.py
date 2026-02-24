import re
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
)
from PySide6.QtCore import Slot, Signal

from hep_gui.config.constants import (
    DATA_DIR, SCRIPTS_DIR, RUNS_DIR,
    DOCKER_IMAGE, MG5_BIN, DOCKER_SHELL, PYTHIA8_LIB,
)
from hep_gui.core.docker_interface import (
    get_docker_client, check_docker, check_image, DockerWorker,
)
from hep_gui.gui.log_panel import LogPanel


class GenerateTab(QWidget):

    run_succeeded = Signal(str)  # emitted with .hepmc path on success

    def __init__(self, script_tab, parent=None):
        super().__init__(parent)
        self._script_tab = script_tab
        self._worker = None
        self._run_name = None
        self._temp_script = None

        self._build_ui()
        self._connect_signals()
        self._set_state_idle()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # control bar
        bar = QHBoxLayout()

        self.label_script = QLabel("No script loaded")
        bar.addWidget(self.label_script, 1)

        self.btn_run = QPushButton("Run")
        self.btn_cancel = QPushButton("Cancel")
        bar.addWidget(self.btn_run)
        bar.addWidget(self.btn_cancel)

        self.label_status = QLabel("Ready")
        bar.addWidget(self.label_status)

        layout.addLayout(bar)

        # log panel
        self.log_panel = LogPanel()
        layout.addWidget(self.log_panel)

    def _connect_signals(self):
        self.btn_run.clicked.connect(self.start_run)
        self.btn_cancel.clicked.connect(self.cancel_run)

    # -- refresh when tab becomes visible --

    def showEvent(self, event):
        super().showEvent(event)
        if not self._worker:
            self._set_state_idle()

    # -- state management --

    def _set_state_idle(self):
        has_script = bool(self._script_tab.get_script_text().strip())
        self.btn_run.setEnabled(has_script)
        self.btn_cancel.setEnabled(False)
        path = self._script_tab.get_current_path()
        self.label_script.setText(path if path else "No script loaded")

    def _set_state_running(self):
        self.btn_run.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.label_status.setText("Running...")

    def _set_state_finished(self, success):
        self.btn_run.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        if success:
            self.label_status.setText("Finished")
        else:
            self.label_status.setText("Error")

    # -- public API --

    def start_run(self):
        text = self._script_tab.get_script_text().strip()
        if not text:
            self.log_panel.append_line("ERROR: no script loaded")
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

        run_name = _extract_run_name(text)
        if not run_name:
            self.log_panel.append_line("ERROR: no 'output /work/<name>' line found in script")
            return

        self._run_name = run_name
        self.label_script.setText(self._script_tab.get_current_path() or "(unsaved script)")

        # write temp script
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._temp_script = SCRIPTS_DIR / f"_run_{stamp}.txt"
        self._temp_script.write_text(text, encoding="utf-8")

        cmd = _build_command(self._temp_script.name, run_name)
        volumes = {str(DATA_DIR): {"bind": "/data", "mode": "rw"}}

        self.log_panel.clear()
        self.log_panel.append_line(f"--- Starting MG5+Pythia8 run: {run_name} ---")

        self._worker = DockerWorker(client, DOCKER_IMAGE, cmd, volumes=volumes)
        self._worker.log_line.connect(self.log_panel.append_line)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

        self._set_state_running()

    def cancel_run(self):
        if self._worker:
            self._worker.stop_container()
            self.log_panel.append_line("--- Run cancelled ---")

    def get_run_name(self):
        return self._run_name

    # -- slots --

    @Slot(int)
    def _on_finished(self, exit_code):
        self._cleanup_temp()

        # MG5 3.6.7 crashes on quit (exit 1 even when generation succeeded)
        # so we check for output files instead of trusting the exit code
        success = self._check_output_files()

        if success:
            out_dir = RUNS_DIR / self._run_name / "Events"
            self.log_panel.append_line(f"--- HepMC files at: {out_dir} ---")
            # find the first .hepmc file for the workflow
            hepmc_files = list(out_dir.rglob("*.hepmc*"))
            if hepmc_files:
                self.run_succeeded.emit(str(hepmc_files[0]))
        else:
            self.log_panel.append_line(f"--- Run failed (exit code {exit_code}), no output files ---")

        self._set_state_finished(success)
        self._worker = None

    @Slot(str)
    def _on_error(self, msg):
        self._cleanup_temp()
        self.log_panel.append_line(f"ERROR: {msg}")
        self._set_state_finished(False)
        self._worker = None

    # -- helpers --

    def _check_output_files(self):
        if not self._run_name:
            return False
        events_dir = RUNS_DIR / self._run_name / "Events"
        if not events_dir.exists():
            return False
        # look for .hepmc.gz or .hepmc files
        hepmc = list(events_dir.rglob("*.hepmc*"))
        return len(hepmc) > 0

    def _cleanup_temp(self):
        if self._temp_script and self._temp_script.exists():
            self._temp_script.unlink()
            self._temp_script = None


def _extract_run_name(script_text):
    match = re.search(r"^output\s+/work/(\S+)", script_text, re.MULTILINE)
    if match:
        return match.group(1)
    return None


def _build_command(script_filename, run_name):
    return (
        f'{DOCKER_SHELL} "'
        f"export LD_PRELOAD={PYTHIA8_LIB}/libpythia8.so "
        f"&& {MG5_BIN} /data/scripts/{script_filename} "
        f"; mkdir -p /data/runs/{run_name} "
        f"&& cp -r /work/{run_name}/Events /data/runs/{run_name}/"
        f'"'
    )
