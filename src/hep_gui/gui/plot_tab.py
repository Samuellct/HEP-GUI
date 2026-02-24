from pathlib import Path

import numpy as np
import pyqtgraph as pg
from pyqtgraph import exporters
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox,
    QCheckBox, QLineEdit, QLabel, QFileDialog, QDialog, QTextEdit,
    QMessageBox,
)
from PySide6.QtCore import Qt, Slot, QUrl, QMarginsF
from PySide6.QtGui import QPainter, QPageLayout, QPageSize, QFont, QDesktopServices

from hep_gui.config.constants import ANALYSIS_DIR, DATA_DIR, COLORS, DOCKER_IMAGE_MKHTML
from hep_gui.core.docker_interface import get_docker_client, check_docker, check_image, DockerWorker
from hep_gui.core.rivet_build import build_mkhtml_command, local_to_docker_path
from hep_gui.core.yoda_parser import parse_yoda, filter_plottable, YodaHisto1D
from hep_gui.utils.normalization import normalize_to_area
from hep_gui.utils.plot_helpers import (
    build_step_coords, auto_log_scale, compute_view_range, get_axis_labels,
)


class PlotTab(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # loaded datasets: {label: {"path": Path, "histos": dict}}
        self._datasets = {}
        # all observable paths across loaded files (sorted)
        self._all_paths = []
        # last directory used in file dialog
        self._last_dir = str(ANALYSIS_DIR)

        self._build_ui()
        self._connect_signals()

    # -- UI setup --

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # top: controls
        ctrl = QHBoxLayout()

        self.btn_load = QPushButton("Load .yoda")
        ctrl.addWidget(self.btn_load)

        ctrl.addWidget(QLabel("Filter:"))
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("type to filter observables...")
        self.filter_edit.setMaximumWidth(200)
        ctrl.addWidget(self.filter_edit)

        self.combo_obs = QComboBox()
        self.combo_obs.setMinimumWidth(350)
        ctrl.addWidget(self.combo_obs, stretch=1)

        self.cb_normalize = QCheckBox("Normalize")
        self.cb_normalize.setChecked(True)
        self.cb_normalize.setToolTip("Normalize to unit area")
        ctrl.addWidget(self.cb_normalize)

        self.cb_logy = QCheckBox("Log Y")
        ctrl.addWidget(self.cb_logy)

        self.cb_logx = QCheckBox("Log X")
        ctrl.addWidget(self.cb_logx)

        layout.addLayout(ctrl)

        # center: plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("w")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        layout.addWidget(self.plot_widget, stretch=1)

        # bottom: labels + export
        bottom = QHBoxLayout()

        bottom.addWidget(QLabel("Title:"))
        self.edit_title = QLineEdit()
        bottom.addWidget(self.edit_title)

        bottom.addWidget(QLabel("X:"))
        self.edit_xlabel = QLineEdit()
        self.edit_xlabel.setMaximumWidth(150)
        bottom.addWidget(self.edit_xlabel)

        bottom.addWidget(QLabel("Y:"))
        self.edit_ylabel = QLineEdit()
        self.edit_ylabel.setMaximumWidth(150)
        bottom.addWidget(self.edit_ylabel)

        self.btn_png = QPushButton("PNG")
        self.btn_svg = QPushButton("SVG")
        self.btn_pdf = QPushButton("PDF")
        self.btn_html = QPushButton("Export HTML")
        self.btn_html.setToolTip("Generate publication-quality HTML via rivet-mkhtml (Docker)")
        bottom.addWidget(self.btn_png)
        bottom.addWidget(self.btn_svg)
        bottom.addWidget(self.btn_pdf)
        bottom.addWidget(self.btn_html)

        layout.addLayout(bottom)

    def _connect_signals(self):
        self.btn_load.clicked.connect(self.load_yoda_files)
        self.combo_obs.currentIndexChanged.connect(self._on_observable_changed)
        self.filter_edit.textChanged.connect(self._apply_filter)
        self.cb_normalize.stateChanged.connect(self._on_controls_changed)
        self.cb_logy.stateChanged.connect(self._on_controls_changed)
        self.cb_logx.stateChanged.connect(self._on_controls_changed)
        self.edit_title.textEdited.connect(self._on_label_edited)
        self.edit_xlabel.textEdited.connect(self._on_label_edited)
        self.edit_ylabel.textEdited.connect(self._on_label_edited)
        self.btn_png.clicked.connect(lambda: self._export("png"))
        self.btn_svg.clicked.connect(lambda: self._export("svg"))
        self.btn_pdf.clicked.connect(lambda: self._export("pdf"))
        self.btn_html.clicked.connect(self._on_export_html)

    # -- public API --

    def load_yoda_files(self):
        """Open file dialog to load one or more .yoda files."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Load YODA files", self._last_dir,
            "YODA files (*.yoda);;All files (*)",
        )
        for f in files:
            self.load_yoda_path(f)

    def load_yoda_path(self, path):
        """Load a single .yoda file without dialog (for programmatic use)."""
        path = Path(path)
        if not path.exists():
            return
        self._last_dir = str(path.parent)
        label = path.stem
        # avoid label collisions
        if label in self._datasets:
            i = 2
            while f"{label}_{i}" in self._datasets:
                i += 1
            label = f"{label}_{i}"

        all_histos = parse_yoda(str(path))
        plottable = filter_plottable(all_histos)
        self._datasets[label] = {"path": path, "histos": plottable}

        self._rebuild_paths()
        self._apply_filter()

    # -- internal --

    def _rebuild_paths(self):
        """Rebuild the merged set of plottable paths from all datasets."""
        paths = set()
        for ds in self._datasets.values():
            paths.update(ds["histos"].keys())
        self._all_paths = sorted(paths)

    def _apply_filter(self, _text=None):
        """Re-populate combo with paths matching filter text."""
        filt = self.filter_edit.text().strip().lower()
        self.combo_obs.blockSignals(True)
        prev = self.combo_obs.currentData()
        self.combo_obs.clear()

        for p in self._all_paths:
            if filt and filt not in p.lower():
                continue
            # find a title from any dataset that has this path
            title = ""
            for ds in self._datasets.values():
                h = ds["histos"].get(p)
                if h and h.title:
                    title = h.title
                    break
            display = f"{p}  --  {title}" if title else p
            self.combo_obs.addItem(display, userData=p)

        # try to restore previous selection
        if prev:
            idx = self.combo_obs.findData(prev)
            if idx >= 0:
                self.combo_obs.setCurrentIndex(idx)

        self.combo_obs.blockSignals(False)
        # trigger plot if we have a selection
        if self.combo_obs.count() > 0:
            self._on_observable_changed()

    def _on_observable_changed(self, *_args):
        path = self.combo_obs.currentData()
        if path:
            self._do_plot(path)

    def _on_controls_changed(self, *_args):
        path = self.combo_obs.currentData()
        if path:
            self._do_plot(path)

    def _on_label_edited(self, *_args):
        pw = self.plot_widget
        pw.setTitle(self.edit_title.text())
        pw.setLabel("bottom", self.edit_xlabel.text())
        pw.setLabel("left", self.edit_ylabel.text())

    def _extract(self, histo):
        """Extract plottable arrays, replacing NaN with 0."""
        edges = np.array(histo.edges, dtype=float)
        n_bins = len(edges) - 1
        vals = histo.values[:n_bins].copy()
        vals = np.where(np.isnan(vals), 0, vals)

        err_dn = err_up = None
        if histo.err_dn is not None:
            err_dn = np.abs(histo.err_dn[:n_bins])
            err_up = histo.err_up[:n_bins]
            err_dn = np.where(np.isnan(err_dn), 0, err_dn)
            err_up = np.where(np.isnan(err_up), 0, err_up)

        return edges, vals, err_dn, err_up

    def _do_plot(self, histo_path):
        pw = self.plot_widget
        pw.clear()
        pw.setLogMode(x=False, y=False)

        do_norm = self.cb_normalize.isChecked()

        # gather data from all datasets
        plot_data = []
        for label, ds in self._datasets.items():
            histo = ds["histos"].get(histo_path)
            if not histo:
                continue
            edges, vals, err_dn, err_up = self._extract(histo)
            if do_norm:
                vals, err_dn, err_up = normalize_to_area(edges, vals, err_dn, err_up)
            plot_data.append((label, edges, vals, err_dn, err_up))

        if not plot_data:
            return

        # log scale: auto-detect from first dataset, then override with checkboxes
        ref_edges, ref_vals = plot_data[0][1], plot_data[0][2]
        xlog, ylog = auto_log_scale(ref_edges, ref_vals)
        if self.cb_logx.isChecked():
            xlog = True
        if self.cb_logy.isChecked():
            ylog = True

        # labels
        xlabel, ylabel = get_axis_labels(histo_path)
        if do_norm:
            ylabel = "normalized"
        title = histo_path.rsplit("/", 1)[-1]

        # update label edits (without triggering textEdited)
        self.edit_title.blockSignals(True)
        self.edit_xlabel.blockSignals(True)
        self.edit_ylabel.blockSignals(True)
        self.edit_title.setText(title)
        self.edit_xlabel.setText(xlabel)
        self.edit_ylabel.setText(ylabel)
        self.edit_title.blockSignals(False)
        self.edit_xlabel.blockSignals(False)
        self.edit_ylabel.blockSignals(False)

        pw.setTitle(title)
        pw.setLabel("bottom", xlabel)
        pw.setLabel("left", ylabel)
        pw.setLogMode(x=xlog, y=ylog)

        legend = pw.addLegend(offset=(10, 10))

        all_edges = []
        all_vals = []

        for i, (label, edges, vals, err_dn, err_up) in enumerate(plot_data):
            color = COLORS[i % len(COLORS)]
            centers = (edges[:-1] + edges[1:]) / 2.0

            # clamp zeros for log y
            plot_vals = vals.copy()
            if ylog:
                positive = plot_vals[plot_vals > 0]
                floor = positive.min() * 0.01 if len(positive) > 0 else 1e-10
                plot_vals = np.where(plot_vals > 0, plot_vals, floor)

            step_x, step_y = build_step_coords(edges, plot_vals)

            # fill between step curve and baseline
            fill_top = pg.PlotCurveItem(step_x, step_y, pen=pg.mkPen(None))
            if ylog:
                base = plot_vals[plot_vals > 0].min() * 0.1 if np.any(plot_vals > 0) else 1e-10
                fill_bot = pg.PlotCurveItem(step_x, np.full_like(step_y, base), pen=pg.mkPen(None))
            else:
                fill_bot = pg.PlotCurveItem(step_x, np.zeros_like(step_y), pen=pg.mkPen(None))
            pw.addItem(pg.FillBetweenItem(fill_top, fill_bot, brush=color["fill"]))

            # step outline
            pw.plot(step_x, step_y, pen=pg.mkPen(color["line"], width=1.5))

            # legend entry (invisible dummy trace)
            pw.plot([], [], pen=pg.mkPen(color["line"], width=3), name=label)

            # error bars on non-zero bins
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

        # set view range
        x_min, x_max, y_min, y_max = compute_view_range(all_edges, all_vals, xlog, ylog)
        if xlog:
            pw.setXRange(np.log10(max(x_min, 1e-30)), np.log10(max(x_max, 1e-30)), padding=0.05)
        else:
            pw.setXRange(x_min, x_max, padding=0)
        if ylog:
            pw.setYRange(np.log10(max(y_min, 1e-30)), np.log10(max(y_max, 1e-30)), padding=0.05)
        else:
            pw.setYRange(y_min, y_max, padding=0)

    def _export(self, fmt):
        """Export the current plot to PNG, SVG, or PDF."""
        filters = {
            "png": "PNG image (*.png)",
            "svg": "SVG image (*.svg)",
            "pdf": "PDF document (*.pdf)",
        }
        path, _ = QFileDialog.getSaveFileName(
            self, "Export plot", self._last_dir, filters.get(fmt, ""),
        )
        if not path:
            return

        if fmt == "png":
            exporter = exporters.ImageExporter(self.plot_widget.plotItem)
            exporter.export(path)
        elif fmt == "svg":
            exporter = exporters.SVGExporter(self.plot_widget.plotItem)
            exporter.export(path)
        elif fmt == "pdf":
            self._export_pdf(path)

    def _export_pdf(self, path):
        """Export plot to PDF via QPdfWriter."""
        from PySide6.QtGui import QPdfWriter
        writer = QPdfWriter(path)
        writer.setPageLayout(QPageLayout(
            QPageSize(QPageSize.A4), QPageLayout.Landscape, QMarginsF(10, 10, 10, 10),
        ))
        painter = QPainter(writer)
        self.plot_widget.render(painter)
        painter.end()

    def _on_export_html(self):
        if not self._datasets:
            QMessageBox.warning(self, "Export HTML", "No YODA files loaded.")
            return

        ok, info = check_docker()
        if not ok:
            QMessageBox.warning(self, "Export HTML",
                f"Docker is not running.\n{info}")
            return

        client = get_docker_client()
        if not client:
            QMessageBox.warning(self, "Export HTML", "Cannot connect to Docker.")
            return

        if not check_image(client, DOCKER_IMAGE_MKHTML):
            QMessageBox.warning(self, "Export HTML",
                f"Image {DOCKER_IMAGE_MKHTML} not found.\n"
                f"Pull it manually:\n  docker pull {DOCKER_IMAGE_MKHTML}")
            return

        # collect docker paths for all loaded .yoda files
        yoda_docker_paths = []
        for ds in self._datasets.values():
            try:
                yoda_docker_paths.append(local_to_docker_path(ds["path"]))
            except ValueError:
                pass

        if not yoda_docker_paths:
            QMessageBox.warning(self, "Export HTML",
                "No loaded YODA files are inside the data/ directory.")
            return

        # output dir name
        if len(yoda_docker_paths) == 1:
            stem = Path(yoda_docker_paths[0]).stem
            out_dir = f"/data/analysis/{stem}_plots"
            local_dir = ANALYSIS_DIR / f"{stem}_plots"
        else:
            out_dir = "/data/analysis/comparison_plots"
            local_dir = ANALYSIS_DIR / "comparison_plots"

        cmd = build_mkhtml_command(yoda_docker_paths, out_dir)
        dlg = MkHtmlDialog(self, client, cmd, local_dir)
        dlg.exec()


class MkHtmlDialog(QDialog):

    def __init__(self, parent, client, cmd, output_dir):
        super().__init__(parent)
        self.setWindowTitle("rivet-mkhtml")
        self.resize(600, 400)
        self._output_dir = output_dir
        self._worker = None

        layout = QVBoxLayout(self)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setFont(QFont("Consolas", 9))
        layout.addWidget(self._log)

        btn_row = QHBoxLayout()
        self._btn_cancel = QPushButton("Cancel")
        self._btn_cancel.clicked.connect(self._on_cancel)
        btn_row.addStretch()
        btn_row.addWidget(self._btn_cancel)
        self._btn_open = QPushButton("Open result")
        self._btn_open.setEnabled(False)
        self._btn_open.clicked.connect(self._on_open)
        btn_row.addWidget(self._btn_open)
        layout.addLayout(btn_row)

        # start the worker
        volumes = {str(DATA_DIR): {"bind": "/data", "mode": "rw"}}
        self._log.append("--- Running rivet-mkhtml ---")

        self._worker = DockerWorker(client, DOCKER_IMAGE_MKHTML, cmd, volumes=volumes)
        self._worker.log_line.connect(self._log.append)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    @Slot(int)
    def _on_finished(self, exit_code):
        self._worker = None
        self._btn_cancel.setEnabled(False)
        if exit_code == 0 and self._output_dir.exists():
            self._log.append(f"--- Done, output: {self._output_dir} ---")
            self._btn_open.setEnabled(True)
        else:
            self._log.append(f"--- rivet-mkhtml failed (exit code {exit_code}) ---")

    @Slot(str)
    def _on_error(self, msg):
        self._worker = None
        self._btn_cancel.setEnabled(False)
        self._log.append(f"ERROR: {msg}")

    def _on_cancel(self):
        if self._worker:
            self._worker.stop_container()
            self._log.append("--- Cancelled ---")

    def _on_open(self):
        index = self._output_dir / "index.html"
        if index.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(index)))
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._output_dir)))
