# T01_5_pyqtgraph_plots.py -- PyQtGraph visualization of YODA histos
#
# Reads any .yoda file, extracts all plottable histograms, auto-detects
# log scale, normalizes for comparison. Not tied to MC_JETS.
#
# Area normalization (equivalent to `yodascale -c '.* 1'`) done in Python.

import sys

import docker
import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QSplitter, QComboBox,
    QLabel, QCheckBox,
)
from PySide6.QtCore import QThread, Signal, Qt

import config
from T01_4_yoda_parser import parse_yoda, YodaHisto1D

DATASETS = {
    "ms=10": {
        "script": "test_ggH_100",
        "yoda": config.ANALYSIS_DIR / "test_ggH_100.yoda",
    },
    "ms=30": {
        "script": "test_ggH_100_30",
        "yoda": config.ANALYSIS_DIR / "test_ggH_100_30.yoda",
    },
}

ANALYSIS = "MC_JETS"

COLORS = [
    {"line": (31, 119, 180), "fill": (31, 119, 180, 60)},
    {"line": (255, 127, 14), "fill": (255, 127, 14, 60)},
]

# optional axis label enrichment from rivet analysis definitions
# used when available, otherwise labels are derived from the path
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
    """Look up axis labels by prefix match, fallback to path-derived names."""
    for prefix, (xl, yl) in AXIS_LABELS.items():
        if path.startswith(prefix):
            return xl, yl
    # generic fallback: last component of path
    name = path.rsplit("/", 1)[-1]
    return name, ""


def _auto_log_scale(edges, vals):
    """Heuristic: use log if all edges > 0 and span > 1.5 decades (x),
    or if positive values span > 2 decades (y)."""
    edges = np.array(edges)
    xlog = False
    if edges.min() > 0 and edges.max() / edges.min() > 30:
        xlog = True

    positive = vals[vals > 0]
    ylog = False
    if len(positive) > 1 and positive.max() / positive.min() > 100:
        ylog = True

    return xlog, ylog


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


def _extract_histo_data(histo):
    """Extract plottable arrays from a YodaHisto1D.

    Returns (edges, values, err_dn, err_up) with underflow/overflow stripped
    and NaN replaced by 0.
    """
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
    """Normalize to unit area (equivalent to yodascale -c '.* 1')."""
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
    """Build step-function x,y for matplotlib-style steps-pre rendering."""
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


def _compute_view_range(edges_list, vals_list, xlog, ylog):
    """Compute sensible axis limits from all plotted data.

    For log axes, limits are tight around the data range.
    For linear axes, includes 0 on y and 5% padding.
    """
    all_edges = np.concatenate(edges_list)
    all_vals = np.concatenate(vals_list)

    positive_vals = all_vals[all_vals > 0]

    # X range from bin edges
    if xlog:
        pos_edges = all_edges[all_edges > 0]
        if len(pos_edges) == 0:
            x_min, x_max = 1, 10
        else:
            x_min, x_max = pos_edges.min(), pos_edges.max()
    else:
        x_min, x_max = all_edges.min(), all_edges.max()
        pad = (x_max - x_min) * 0.02
        x_min -= pad
        x_max += pad

    # Y range from values
    if ylog:
        if len(positive_vals) == 0:
            y_min, y_max = 1, 10
        else:
            y_min = positive_vals.min() * 0.3
            y_max = positive_vals.max() * 3.0
    else:
        y_min = 0
        y_max = all_vals.max() * 1.1 if len(all_vals) > 0 else 1

    return x_min, x_max, y_min, y_max


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("T01_5: PyQtGraph plots")
        self.resize(1300, 750)
        self.worker = None
        self._yoda_cache = {}

        # -- row 1: generate buttons --
        self.gen_btns = {}
        for label in DATASETS:
            btn = QPushButton(f"Generate {label}")
            btn.clicked.connect(lambda checked=False, lbl=label: self.on_generate(lbl))
            self.gen_btns[label] = btn

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.on_cancel)

        gen_row = QHBoxLayout()
        for btn in self.gen_btns.values():
            gen_row.addWidget(btn)
        gen_row.addWidget(self.cancel_btn)
        gen_row.addStretch()

        # -- row 2: plot controls --
        self.histo_combo = QComboBox()
        self.histo_combo.setMinimumWidth(350)
        self.histo_combo.currentIndexChanged.connect(self._on_controls_changed)

        self.plot_btn = QPushButton("Plot")
        self.plot_btn.clicked.connect(self.on_plot)

        self.ds_checks = {}
        for label in DATASETS:
            cb = QCheckBox(label)
            cb.setChecked(label == "ms=10")
            cb.stateChanged.connect(self._on_controls_changed)
            self.ds_checks[label] = cb

        self.normalize_cb = QCheckBox("Normalize")
        self.normalize_cb.setChecked(True)
        self.normalize_cb.setToolTip("Normalize to unit area (like yodascale -c '.* 1')")
        self.normalize_cb.stateChanged.connect(self._on_controls_changed)

        ctrl_row = QHBoxLayout()
        ctrl_row.addWidget(QLabel("Observable:"))
        ctrl_row.addWidget(self.histo_combo, stretch=1)
        ctrl_row.addWidget(self.plot_btn)
        for cb in self.ds_checks.values():
            ctrl_row.addWidget(cb)
        ctrl_row.addWidget(self.normalize_cb)

        # -- panels --
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
        layout.addLayout(gen_row)
        layout.addLayout(ctrl_row)
        layout.addWidget(splitter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self._update_buttons()
        self._populate_combo_from_yoda()

    def _populate_combo_from_yoda(self):
        """Fill dropdown from actual YODA file contents (not hardcoded)."""
        self.histo_combo.blockSignals(True)
        self.histo_combo.clear()

        # use whichever dataset is available (prefer ms=10)
        results = None
        for label, ds in DATASETS.items():
            if ds["yoda"].exists():
                results = self._load_yoda(label)
                break

        if not results:
            self.histo_combo.addItem("(no .yoda file found)", userData=None)
            self.histo_combo.blockSignals(False)
            return

        # collect plottable paths: skip /RAW/, skip private (_prefix), skip variations ([n])
        paths = []
        for path, obj in results.items():
            if not isinstance(obj, YodaHisto1D):
                continue
            if path.startswith("/RAW/"):
                continue
            if path.startswith("/TMP/"):
                continue
            # skip internal histos (start with _ after the analysis prefix)
            parts = path.split("/")
            if len(parts) >= 3 and parts[2].startswith("_"):
                continue
            # skip weight variations ([n] suffix)
            if "[" in path:
                continue
            # skip counters-like paths
            if path.startswith("/_"):
                continue
            paths.append(path)

        paths.sort()
        for p in paths:
            histo = results[p]
            title = histo.title if histo.title else p.rsplit("/", 1)[-1]
            self.histo_combo.addItem(f"{p}  --  {title}", userData=p)

        self.histo_combo.blockSignals(False)
        self.log_view.append(f"Loaded {len(paths)} plottable histograms from YODA")

    def _update_buttons(self):
        for label, ds in DATASETS.items():
            exists = ds["yoda"].exists()
            self.gen_btns[label].setEnabled(not exists)
            if exists:
                self.gen_btns[label].setText(f"{label} (ready)")
            self.ds_checks[label].setEnabled(exists)

        can_plot = any(
            self.ds_checks[label].isChecked() and DATASETS[label]["yoda"].exists()
            for label in DATASETS
        )
        self.plot_btn.setEnabled(can_plot)

    def _set_running(self, running):
        for btn in self.gen_btns.values():
            btn.setEnabled(False)
        self.plot_btn.setEnabled(False)
        self.cancel_btn.setEnabled(running)

    def _build_generate_cmd(self, script_name):
        mg5_script = f"/data/scripts/{script_name}.txt"
        container_run = f"/work/{script_name}"
        hepmc = f"/data/runs/{script_name}/Events/run_01/tag_1_pythia8_events.hepmc.gz"
        yoda = f"/data/analysis/{script_name}.yoda"
        return (
            f'{config.DOCKER_SHELL} "'
            f"export LD_PRELOAD={config.PYTHIA8_LIB}/libpythia8.so"
            f" && {config.MG5_BIN} {mg5_script}"
            f"; mkdir -p /data/runs/{script_name} && cp -r {container_run}/Events /data/runs/{script_name}/"
            f" && mkdir -p /data/analysis && rivet --analysis={ANALYSIS} {hepmc} -o {yoda}"
            f'"'
        )

    def on_generate(self, label):
        ds = DATASETS[label]
        self._set_running(True)
        self.log_view.clear()
        self.log_view.append(f"Generating {label}...")

        cmd = self._build_generate_cmd(ds["script"])
        client = docker.from_env()
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
        self._yoda_cache.clear()
        self._update_buttons()
        self._populate_combo_from_yoda()

    def on_plot(self):
        path = self.histo_combo.currentData()
        if path:
            self._do_plot(path)

    def _on_controls_changed(self, *_args):
        self._update_buttons()
        path = self.histo_combo.currentData()
        if not path:
            return
        has_data = any(
            self.ds_checks[label].isChecked() and DATASETS[label]["yoda"].exists()
            for label in DATASETS
        )
        if has_data:
            self._do_plot(path)

    def _load_yoda(self, label):
        if label not in self._yoda_cache:
            ds = DATASETS[label]
            if not ds["yoda"].exists():
                return {}
            results, _ = parse_yoda(ds["yoda"])
            self._yoda_cache[label] = results
        return self._yoda_cache[label]

    def _do_plot(self, histo_path):
        pw = self.plot_widget
        pw.clear()
        # reset log mode to linear before anything else
        pw.setLogMode(x=False, y=False)

        do_normalize = self.normalize_cb.isChecked()

        # collect which datasets to plot
        active = [
            (label, ds) for label, ds in DATASETS.items()
            if self.ds_checks[label].isChecked() and ds["yoda"].exists()
        ]

        # first pass: extract all data to determine axis scales
        plot_data = []
        for label, ds in active:
            results = self._load_yoda(label)
            histo = results.get(histo_path)
            if not histo or not isinstance(histo, YodaHisto1D):
                self.log_view.append(f"  {histo_path} not found in {label}")
                continue
            edges, vals, err_dn, err_up = _extract_histo_data(histo)
            if do_normalize:
                vals, err_dn, err_up = _normalize_to_area(edges, vals, err_dn, err_up)
            plot_data.append((label, edges, vals, err_dn, err_up))

        if not plot_data:
            self.log_view.append(f"  nothing to plot for {histo_path}")
            return

        # auto-detect log scale from data
        ref_edges, ref_vals = plot_data[0][1], plot_data[0][2]
        xlog, ylog = _auto_log_scale(ref_edges, ref_vals)

        # axis labels from lookup or path
        xlabel, ylabel = _get_axis_labels(histo_path)
        if do_normalize:
            ylabel = "normalized"

        title = histo_path.rsplit("/", 1)[-1]
        pw.setTitle(title)
        pw.setLabel("bottom", xlabel)
        pw.setLabel("left", ylabel)
        pw.setLogMode(x=xlog, y=ylog)

        legend = pw.addLegend(offset=(10, 10))

        # collect edges and vals for view range computation
        all_edges = []
        all_vals = []

        for i, (label, edges, vals, err_dn, err_up) in enumerate(plot_data):
            centers = (edges[:-1] + edges[1:]) / 2.0
            color = COLORS[i % len(COLORS)]

            # for log y, clamp zeros to a floor below the minimum positive value
            plot_vals = vals.copy()
            if ylog:
                positive = plot_vals[plot_vals > 0]
                if len(positive) > 0:
                    floor = positive.min() * 0.01
                    plot_vals = np.where(plot_vals > 0, plot_vals, floor)
                else:
                    plot_vals = np.where(plot_vals > 0, plot_vals, 1e-10)

            step_x, step_y = _build_step_coords(edges, plot_vals)

            # fill under the step curve
            fill_top = pg.PlotCurveItem(step_x, step_y, pen=pg.mkPen(None))
            if ylog:
                base = plot_vals[plot_vals > 0].min() * 0.1 if np.any(plot_vals > 0) else 1e-10
                fill_bot = pg.PlotCurveItem(step_x, np.full_like(step_y, base), pen=pg.mkPen(None))
            else:
                fill_bot = pg.PlotCurveItem(step_x, np.zeros_like(step_y), pen=pg.mkPen(None))
            pw.addItem(pg.FillBetweenItem(fill_top, fill_bot, brush=color["fill"]))

            # step outline
            pw.plot(step_x, step_y, pen=pg.mkPen(color["line"], width=1.5))

            # legend entry
            pw.plot([], [], pen=pg.mkPen(color["line"], width=3), name=label)

            # error bars on non-zero bins only
            if err_dn is not None:
                mask = vals > 0
                if mask.any():
                    pw.addItem(pg.ErrorBarItem(
                        x=centers[mask], y=plot_vals[mask],
                        top=err_up[mask], bottom=err_dn[mask],
                        pen=pg.mkPen(color["line"], width=1.2),
                    ))

            all_edges.append(edges)
            all_vals.append(plot_vals)

        # set explicit view range computed from data
        x_min, x_max, y_min, y_max = _compute_view_range(all_edges, all_vals, xlog, ylog)
        if xlog:
            # pyqtgraph log mode works in log10 space
            pw.setXRange(np.log10(max(x_min, 1e-30)), np.log10(max(x_max, 1e-30)), padding=0.05)
        else:
            pw.setXRange(x_min, x_max, padding=0)
        if ylog:
            pw.setYRange(np.log10(max(y_min, 1e-30)), np.log10(max(y_max, 1e-30)), padding=0.05)
        else:
            pw.setYRange(y_min, y_max, padding=0)

        self.log_view.append(f"Plotted: {histo_path}")


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec())
