# T01_6_poc_app.py -- mini POC end-to-end
#
# Load a MG5 script -> run Docker pipeline (MG5+Pythia8+Rivet) ->
# stream logs in real time -> auto-plot the produced .yoda file.
# Last test of Phase 01 before moving to Phase 02.

import sys
from pathlib import Path

import docker
import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QWidget, QSplitter, QComboBox,
    QLabel, QFileDialog,
)
from PySide6.QtCore import QThread, Signal, Qt

import config
from T01_4_yoda_parser import parse_yoda, YodaHisto1D

# -- plot helpers (copied from T01_5, no shared lib in Phase 01) --

COLORS = [
    {"line": (31, 119, 180), "fill": (31, 119, 180, 60)},
]

AXIS_LABELS = {
    "/MC_JETS/jet_HT":     ("HT [GeV]", "dsigma/dHT [pb/GeV]"),
    "/MC_JETS/jet_eta_":    ("eta", "dsigma/deta [pb]"),
    "/MC_JETS/jet_pT_":     ("pT [GeV]", "dsigma/dpT [pb/GeV]"),
    "/MC_JETS/jet_y_":      ("y", "dsigma/dy [pb]"),
    "/MC_JETS/jet_mass_":   ("m [GeV]", "dsigma/dm [pb/GeV]"),
    "/MC_JETS/jet_multi_":  ("N_jet", "sigma [pb]"),
    "/MC_JETS/jets_dR_":    ("dR", "dsigma/ddR [pb]"),
    "/MC_JETS/jets_deta_":  ("deta", "dsigma/ddeta [pb]"),
    "/MC_JETS/jets_dphi_":  ("dphi", "dsigma/ddphi [pb]"),
    "/MC_JETS/jets_mjj":    ("m_jj [GeV]", "dsigma/dm_jj [pb/GeV]"),
}


def _get_axis_labels(path):
    for prefix, (xl, yl) in AXIS_LABELS.items():
        if path.startswith(prefix):
            return xl, yl
    name = path.rsplit("/", 1)[-1]
    return name, ""


def _auto_log_scale(edges, vals):
    edges = np.array(edges)
    xlog = False
    if edges.min() > 0 and edges.max() / edges.min() > 30:
        xlog = True

    positive = vals[vals > 0]
    ylog = False
    if len(positive) > 1 and positive.max() / positive.min() > 100:
        ylog = True

    return xlog, ylog


def _extract_histo_data(histo):
    edges = np.array(histo.edges, dtype=float)
    n_bins = len(edges) - 1

    if len(histo.values) > n_bins:
        vals = histo.values[1 : n_bins + 1]
    else:
        vals = histo.values[:n_bins]
    vals = np.where(np.isnan(vals), 0, vals)

    err_dn = err_up = None
    if histo.err_dn is not None:
        if len(histo.err_dn) > n_bins:
            err_dn = np.abs(histo.err_dn[1 : n_bins + 1])
            err_up = histo.err_up[1 : n_bins + 1]
        else:
            err_dn = np.abs(histo.err_dn[:n_bins])
            err_up = histo.err_up[:n_bins]
        err_dn = np.where(np.isnan(err_dn), 0, err_dn)
        err_up = np.where(np.isnan(err_up), 0, err_up)

    return edges, vals, err_dn, err_up


def _normalize_to_area(edges, vals, err_dn, err_up):
    widths = np.diff(edges)
    area = np.nansum(vals * widths)
    if area == 0:
        return vals, err_dn, err_up
    vals = vals / area
    if err_dn is not None:
        err_dn = err_dn / area
        err_up = err_up / area
    return vals, err_dn, err_up


def _build_step_coords(edges, vals):
    n = len(vals)
    x = np.empty(2 * n + 2)
    y = np.empty(2 * n + 2)
    x[0] = edges[0]
    y[0] = 0
    for i in range(n):
        x[1 + 2 * i] = edges[i]
        x[2 + 2 * i] = edges[i + 1]
        y[1 + 2 * i] = vals[i]
        y[2 + 2 * i] = vals[i]
    x[-1] = edges[-1]
    y[-1] = 0
    return x, y


def _compute_view_range(edges, vals, xlog, ylog):
    positive_vals = vals[vals > 0]

    if xlog:
        pos_edges = edges[edges > 0]
        if len(pos_edges) == 0:
            x_min, x_max = 1, 10
        else:
            x_min, x_max = pos_edges.min(), pos_edges.max()
    else:
        x_min, x_max = edges.min(), edges.max()
        pad = (x_max - x_min) * 0.02
        x_min -= pad
        x_max += pad

    if ylog:
        if len(positive_vals) == 0:
            y_min, y_max = 1, 10
        else:
            y_min = positive_vals.min() * 0.3
            y_max = positive_vals.max() * 3.0
    else:
        y_min = 0
        y_max = vals.max() * 1.1 if len(vals) > 0 else 1

    return x_min, x_max, y_min, y_max


# -- Docker worker (same as T01_5) --

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


# -- main window --

ANALYSIS_LIST = ["MC_JETS"]


class PocWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("T01_6: POC end-to-end")
        self.resize(1300, 750)

        self.worker = None
        self.script_path = None
        self.run_name = None
        self.yoda_data = None
        self.state = "idle"

        # -- row 1: script loading + run controls --
        self.script_label = QLabel("(no script loaded)")
        self.script_label.setMinimumWidth(250)

        self.load_btn = QPushButton("Load script")
        self.load_btn.clicked.connect(self.on_load)

        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.on_run)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.on_cancel)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Script:"))
        row1.addWidget(self.script_label, stretch=1)
        row1.addWidget(self.load_btn)
        row1.addWidget(self.run_btn)
        row1.addWidget(self.cancel_btn)

        # -- row 2: analysis + observable selection --
        self.analysis_combo = QComboBox()
        self.analysis_combo.addItems(ANALYSIS_LIST)
        self.analysis_combo.setMinimumWidth(120)

        self.histo_combo = QComboBox()
        self.histo_combo.setMinimumWidth(350)
        self.histo_combo.currentIndexChanged.connect(self._on_histo_changed)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Analysis:"))
        row2.addWidget(self.analysis_combo)
        row2.addWidget(QLabel("Observable:"))
        row2.addWidget(self.histo_combo, stretch=1)

        # -- main panels --
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("w")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.log_view)
        splitter.addWidget(self.plot_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout = QVBoxLayout()
        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addWidget(splitter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self._sync_ui()

    # -- state machine --

    def _sync_ui(self):
        s = self.state
        self.load_btn.setEnabled(s in ("idle", "script_loaded", "done"))
        self.run_btn.setEnabled(s in ("script_loaded", "done"))
        self.cancel_btn.setEnabled(s == "running")
        self.histo_combo.setEnabled(s == "done")
        self.analysis_combo.setEnabled(s == "done")

    def _set_state(self, new_state):
        self.state = new_state
        self._sync_ui()

    # -- handlers --

    def on_load(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select MG5 script",
            str(config.SCRIPTS_DIR),
            "MG5 scripts (*.txt);;All files (*)",
        )
        if not path:
            return

        self.script_path = Path(path)
        self.run_name = self.script_path.stem
        self.script_label.setText(self.script_path.name)
        self.log_view.clear()
        self.log_view.append(f"Loaded: {self.script_path}")

        # warn if script is outside data/scripts/ (won't be visible in Docker)
        try:
            self.script_path.relative_to(config.SCRIPTS_DIR)
        except ValueError:
            self.log_view.append(
                "WARNING: script is outside data/scripts/ -- Docker won't see it"
            )

        self._set_state("script_loaded")

    def on_run(self):
        if not self.script_path:
            return

        # check Docker is available
        try:
            client = docker.from_env()
        except docker.errors.DockerException as e:
            self.log_view.append(f"ERROR: can't connect to Docker -- {e}")
            return

        self._set_state("running")
        self.log_view.clear()
        self.log_view.append(f"Starting pipeline for {self.run_name}...")

        analysis = self.analysis_combo.currentText()
        cmd = self._build_cmd(analysis)
        self.log_view.append(f"cmd: {cmd}")

        volumes = {str(config.DATA_DIR): {"bind": "/data", "mode": "rw"}}
        self.worker = DockerWorker(client, config.DOCKER_IMAGE, cmd, volumes)
        self.worker.log_line.connect(self.log_view.append)
        self.worker.finished_with_code.connect(self.on_done)
        self.worker.start()

    def _build_cmd(self, analysis):
        mg5_script = f"/data/scripts/{self.run_name}.txt"
        container_run = f"/work/{self.run_name}"
        hepmc = (
            f"/data/runs/{self.run_name}/Events/run_01/"
            f"tag_1_pythia8_events.hepmc.gz"
        )
        yoda = f"/data/analysis/{self.run_name}.yoda"

        return (
            f'{config.DOCKER_SHELL} "'
            f"export LD_PRELOAD={config.PYTHIA8_LIB}/libpythia8.so"
            f" && {config.MG5_BIN} {mg5_script}"
            f"; mkdir -p /data/runs/{self.run_name}"
            f" && cp -r {container_run}/Events /data/runs/{self.run_name}/"
            f" && mkdir -p /data/analysis"
            f" && rivet --analysis={analysis} {hepmc} -o {yoda}"
            f'"'
        )

    def on_cancel(self):
        if self.worker:
            self.log_view.append("Cancelling...")
            self.worker.stop_container()

    def on_done(self, exit_code):
        self.log_view.append(f"--- exit code: {exit_code} ---")
        self.worker = None

        if exit_code != 0:
            self.log_view.append("Pipeline failed, check logs above.")
            self._set_state("script_loaded")
            return

        # look for the .yoda output
        yoda_path = config.ANALYSIS_DIR / f"{self.run_name}.yoda"
        if not yoda_path.exists():
            self.log_view.append(f"ERROR: expected .yoda not found: {yoda_path}")
            self._set_state("script_loaded")
            return

        # parse and populate dropdown
        try:
            results, skipped = parse_yoda(yoda_path)
        except Exception as e:
            self.log_view.append(f"ERROR parsing .yoda: {e}")
            self._set_state("script_loaded")
            return

        self.yoda_data = results
        self._populate_histo_combo()
        self._set_state("done")

        # auto-plot first observable
        if self.histo_combo.count() > 0 and self.histo_combo.currentData():
            self._do_plot(self.histo_combo.currentData())

    def _populate_histo_combo(self):
        self.histo_combo.blockSignals(True)
        self.histo_combo.clear()

        if not self.yoda_data:
            self.histo_combo.addItem("(no data)", userData=None)
            self.histo_combo.blockSignals(False)
            return

        paths = []
        for path, obj in self.yoda_data.items():
            if not isinstance(obj, YodaHisto1D):
                continue
            if path.startswith("/RAW/") or path.startswith("/TMP/"):
                continue
            parts = path.split("/")
            if len(parts) >= 3 and parts[2].startswith("_"):
                continue
            if "[" in path:
                continue
            if path.startswith("/_"):
                continue
            paths.append(path)

        paths.sort()
        for p in paths:
            histo = self.yoda_data[p]
            title = histo.title if histo.title else p.rsplit("/", 1)[-1]
            self.histo_combo.addItem(f"{p}  --  {title}", userData=p)

        self.histo_combo.blockSignals(False)
        self.log_view.append(f"Loaded {len(paths)} plottable histograms")

    def _on_histo_changed(self, _index):
        path = self.histo_combo.currentData()
        if path and self.yoda_data:
            self._do_plot(path)

    def _do_plot(self, histo_path):
        histo = self.yoda_data.get(histo_path)
        if not histo or not isinstance(histo, YodaHisto1D):
            return

        pw = self.plot_widget
        pw.clear()
        pw.setLogMode(x=False, y=False)

        edges, vals, err_dn, err_up = _extract_histo_data(histo)
        vals, err_dn, err_up = _normalize_to_area(edges, vals, err_dn, err_up)

        xlog, ylog = _auto_log_scale(edges, vals)

        xlabel, ylabel = _get_axis_labels(histo_path)
        ylabel = "normalized"
        title = histo_path.rsplit("/", 1)[-1]

        pw.setTitle(title)
        pw.setLabel("bottom", xlabel)
        pw.setLabel("left", ylabel)
        pw.setLogMode(x=xlog, y=ylog)

        color = COLORS[0]

        # for log y, clamp zeros
        plot_vals = vals.copy()
        if ylog:
            positive = plot_vals[plot_vals > 0]
            if len(positive) > 0:
                floor = positive.min() * 0.01
                plot_vals = np.where(plot_vals > 0, plot_vals, floor)
            else:
                plot_vals = np.where(plot_vals > 0, plot_vals, 1e-10)

        step_x, step_y = _build_step_coords(edges, plot_vals)

        # fill
        fill_top = pg.PlotCurveItem(step_x, step_y, pen=pg.mkPen(None))
        if ylog:
            base = plot_vals[plot_vals > 0].min() * 0.1 if np.any(plot_vals > 0) else 1e-10
            fill_bot = pg.PlotCurveItem(step_x, np.full_like(step_y, base), pen=pg.mkPen(None))
        else:
            fill_bot = pg.PlotCurveItem(step_x, np.zeros_like(step_y), pen=pg.mkPen(None))
        pw.addItem(pg.FillBetweenItem(fill_top, fill_bot, brush=color["fill"]))

        # step outline
        pw.plot(step_x, step_y, pen=pg.mkPen(color["line"], width=1.5))

        # error bars
        if err_dn is not None:
            centers = (edges[:-1] + edges[1:]) / 2.0
            mask = vals > 0
            if mask.any():
                pw.addItem(pg.ErrorBarItem(
                    x=centers[mask], y=plot_vals[mask],
                    top=err_up[mask], bottom=err_dn[mask],
                    pen=pg.mkPen(color["line"], width=1.2),
                ))

        # set view range
        x_min, x_max, y_min, y_max = _compute_view_range(edges, plot_vals, xlog, ylog)
        if xlog:
            pw.setXRange(np.log10(max(x_min, 1e-30)), np.log10(max(x_max, 1e-30)), padding=0.05)
        else:
            pw.setXRange(x_min, x_max, padding=0)
        if ylog:
            pw.setYRange(np.log10(max(y_min, 1e-30)), np.log10(max(y_max, 1e-30)), padding=0.05)
        else:
            pw.setYRange(y_min, y_max, padding=0)

        self.log_view.append(f"Plotted: {histo_path}")


app = QApplication(sys.argv)
win = PocWindow()
win.show()
sys.exit(app.exec())
