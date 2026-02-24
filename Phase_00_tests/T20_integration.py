"""T20 -- Integration and polish: auto-pull, diagnostics, robustness."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtWidgets import QApplication

app = QApplication.instance() or QApplication(sys.argv)


def test_imports():
    """All modules should import without error."""
    from hep_gui.gui.main_window import MainWindow
    from hep_gui.gui.script_tab import ScriptTab
    from hep_gui.gui.generate_tab import GenerateTab
    from hep_gui.gui.analysis_tab import AnalysisTab
    from hep_gui.gui.plot_tab import PlotTab
    from hep_gui.core.docker_interface import (
        get_docker_client, check_docker, check_image,
        DockerWorker, PullWorker, diagnose_docker_error,
    )
    from hep_gui.core.workflow_engine import WorkflowEngine
    from hep_gui.core.yoda_parser import parse_yoda, filter_plottable
    from hep_gui.core.rivet_build import build_rivet_command, build_mkhtml_command
    from hep_gui.utils.normalization import normalize_to_area
    from hep_gui.utils.plot_helpers import build_step_coords, auto_log_scale
    print("OK  all modules import")


def test_main_window():
    from hep_gui.gui.main_window import MainWindow
    w = MainWindow()
    assert w is not None
    print("OK  MainWindow instantiates")


def test_diagnose_docker_error():
    from hep_gui.core.docker_interface import diagnose_docker_error

    msg1 = diagnose_docker_error("no space left on device")
    assert "docker system prune" in msg1
    print(f"OK  diagnose: disk full -> {msg1.splitlines()[-1].strip()}")

    msg2 = diagnose_docker_error("connection refused")
    assert "Docker Desktop" in msg2
    print(f"OK  diagnose: connection refused -> {msg2.splitlines()[-1].strip()}")

    msg3 = diagnose_docker_error("request timed out")
    assert "overloaded" in msg3
    print(f"OK  diagnose: timeout -> {msg3.splitlines()[-1].strip()}")

    msg4 = diagnose_docker_error("permission denied")
    assert "permissions" in msg4
    print(f"OK  diagnose: permission -> {msg4.splitlines()[-1].strip()}")

    msg5 = diagnose_docker_error("some unknown error")
    assert msg5 == "some unknown error"
    print("OK  diagnose: unknown -> passthrough")


def test_pullworker_no_tag():
    from unittest.mock import MagicMock
    from hep_gui.core.docker_interface import PullWorker

    client = MagicMock()
    # tag without ":"
    w = PullWorker(client, "myimage")
    assert w.tag == "myimage"
    # should not crash on init
    print("OK  PullWorker accepts tag without ':'")


def test_generate_tab_has_pull_finished():
    from hep_gui.gui.script_tab import ScriptTab
    from hep_gui.gui.generate_tab import GenerateTab

    script_tab = ScriptTab()
    tab = GenerateTab(script_tab)
    assert hasattr(tab, "_on_pull_finished"), "GenerateTab needs _on_pull_finished"
    assert hasattr(tab, "_pull_worker"), "GenerateTab needs _pull_worker attr"
    print("OK  GenerateTab has auto-pull support")


def test_analysis_tab_has_pull_finished():
    from hep_gui.gui.analysis_tab import AnalysisTab

    tab = AnalysisTab()
    assert hasattr(tab, "_on_pull_finished"), "AnalysisTab needs _on_pull_finished"
    assert hasattr(tab, "_pull_worker"), "AnalysisTab needs _pull_worker attr"
    print("OK  AnalysisTab has auto-pull support")


def test_plot_tab_export_html_feedback():
    """PlotTab._on_export_html should give feedback, not fail silently."""
    from hep_gui.gui.plot_tab import PlotTab
    import inspect

    tab = PlotTab()
    source = inspect.getsource(tab._on_export_html)
    assert "QMessageBox" in source, "PlotTab._on_export_html should use QMessageBox"
    print("OK  PlotTab._on_export_html uses QMessageBox for feedback")


def test_version():
    from hep_gui.config.constants import APP_VERSION
    assert APP_VERSION == "0.11.0-beta", f"expected 0.11.0-beta, got {APP_VERSION}"
    print(f"OK  APP_VERSION = {APP_VERSION}")


if __name__ == "__main__":
    test_imports()
    test_main_window()
    test_diagnose_docker_error()
    test_pullworker_no_tag()
    test_generate_tab_has_pull_finished()
    test_analysis_tab_has_pull_finished()
    test_plot_tab_export_html_feedback()
    test_version()
    print("\nAll T20 tests passed.")
