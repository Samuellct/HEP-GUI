from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QLabel, QMenuBar, QMessageBox,
)
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtCore import Qt, QUrl

from hep_gui.config.constants import APP_NAME, APP_VERSION, DOCKER_IMAGE
from hep_gui.core.docker_interface import check_docker, check_image, get_docker_client
from hep_gui.gui.script_tab import ScriptTab
from hep_gui.gui.generate_tab import GenerateTab
from hep_gui.gui.analysis_tab import AnalysisTab
from hep_gui.gui.plot_tab import PlotTab
from hep_gui.core.workflow_engine import WorkflowEngine


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(1200, 800)

        self._build_tabs()
        self._build_menu()
        self._build_status_bar()
        self._update_docker_status()

    def _build_tabs(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_script = ScriptTab()
        self.tab_generate = GenerateTab(self.tab_script)
        self.tab_analysis = AnalysisTab()
        self.tab_plots = PlotTab()

        self.tabs.addTab(self.tab_script, "Script")
        self.tabs.addTab(self.tab_generate, "Generation")
        self.tabs.addTab(self.tab_analysis, "Analysis")
        self.tabs.addTab(self.tab_plots, "Plots")

        self._workflow = WorkflowEngine(
            self.tabs, self.tab_generate, self.tab_analysis, self.tab_plots,
        )

    def _build_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")

        self.action_open = QAction("Open script", self)
        file_menu.addAction(self.action_open)

        self.action_save = QAction("Save script", self)
        file_menu.addAction(self.action_save)

        self.action_open.triggered.connect(self.tab_script.open_script)
        self.action_save.triggered.connect(self.tab_script.save_script)

        file_menu.addSeparator()

        action_exit = QAction("Exit", self)
        action_exit.triggered.connect(self.close)
        file_menu.addAction(action_exit)

        help_menu = menu_bar.addMenu("Help")
        action_about = QAction("About", self)
        action_about.triggered.connect(self._show_about)
        help_menu.addAction(action_about)

    def _build_status_bar(self):
        self._docker_label = QLabel("Docker: checking...")
        self._action_label = QLabel("Ready")

        sb = self.statusBar()
        sb.addWidget(self._docker_label, 1)
        sb.addPermanentWidget(self._action_label)

    def _update_docker_status(self):
        ok, info = check_docker()
        if not ok:
            self._docker_label.setText("Docker: not running")
            return

        client = get_docker_client()
        has_image = check_image(client, DOCKER_IMAGE) if client else False

        if has_image:
            self._docker_label.setText(f"Docker: connected v{info} | image OK")
        else:
            self._docker_label.setText(f"Docker: connected v{info} | image missing")

    def set_status(self, text):
        self._action_label.setText(text)

    def _show_about(self):
        text = (
            f"<h3>{APP_NAME} v{APP_VERSION}</h3>"
            f"<p>MIT License</p>"
            f'<p><a href="https://github.com/Samuellct/HEP-GUI">GitHub</a></p>'
        )
        dlg = QMessageBox(self)
        dlg.setWindowTitle(f"About {APP_NAME}")
        dlg.setTextFormat(Qt.RichText)
        dlg.setText(text)
        dlg.exec()
