"""T19 -- WorkflowEngine + rivet-mkhtml utilities."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtWidgets import QApplication, QTabWidget

app = QApplication.instance() or QApplication(sys.argv)

from hep_gui.gui.script_tab import ScriptTab
from hep_gui.gui.generate_tab import GenerateTab
from hep_gui.gui.analysis_tab import AnalysisTab
from hep_gui.gui.plot_tab import PlotTab, MkHtmlDialog
from hep_gui.core.workflow_engine import WorkflowEngine
from hep_gui.core.rivet_build import build_mkhtml_command, local_to_docker_path
from hep_gui.config.constants import DATA_DIR, ANALYSIS_DIR


def test_workflow_gen_to_analysis():
    tabs = QTabWidget()
    script_tab = ScriptTab()
    gen_tab = GenerateTab(script_tab)
    analysis_tab = AnalysisTab()
    plot_tab = PlotTab()
    tabs.addTab(script_tab, "Script")
    tabs.addTab(gen_tab, "Generation")
    tabs.addTab(analysis_tab, "Analysis")
    tabs.addTab(plot_tab, "Plots")

    wf = WorkflowEngine(tabs, gen_tab, analysis_tab, plot_tab)

    fake_hepmc = str(DATA_DIR / "runs" / "test" / "Events" / "run_01" / "test.hepmc.gz")
    gen_tab.run_succeeded.emit(fake_hepmc)

    assert analysis_tab.input_hepmc.text() == fake_hepmc, "hepmc path not set"
    assert tabs.currentWidget() is analysis_tab, "should switch to Analysis tab"
    print("OK  workflow: Generation -> Analysis")


def test_workflow_analysis_to_plots():
    tabs = QTabWidget()
    script_tab = ScriptTab()
    gen_tab = GenerateTab(script_tab)
    analysis_tab = AnalysisTab()
    plot_tab = PlotTab()
    tabs.addTab(script_tab, "Script")
    tabs.addTab(gen_tab, "Generation")
    tabs.addTab(analysis_tab, "Analysis")
    tabs.addTab(plot_tab, "Plots")

    wf = WorkflowEngine(tabs, gen_tab, analysis_tab, plot_tab)

    # use a real .yoda file if available, otherwise just test tab switch
    yoda_files = list(ANALYSIS_DIR.glob("*.yoda")) if ANALYSIS_DIR.exists() else []
    if yoda_files:
        yoda_path = str(yoda_files[0])
        analysis_tab.run_succeeded.emit(yoda_path)
        assert tabs.currentWidget() is plot_tab, "should switch to Plots tab"
        assert plot_tab.combo_obs.count() > 0, "combo should have items after loading .yoda"
        print(f"OK  workflow: Analysis -> Plots (loaded {yoda_files[0].name}, {plot_tab.combo_obs.count()} observables)")
    else:
        # no .yoda available, just test the signal/tab switch with a fake path
        analysis_tab.run_succeeded.emit("C:/fake/path.yoda")
        assert tabs.currentWidget() is plot_tab, "should switch to Plots tab"
        print("OK  workflow: Analysis -> Plots (no .yoda file available, tab switch only)")


def test_build_mkhtml_command():
    cmd = build_mkhtml_command(
        ["/data/analysis/test.yoda"],
        "/data/analysis/test_plots",
    )
    assert "rivet-mkhtml" in cmd
    assert "/data/analysis/test.yoda" in cmd
    assert "-o /data/analysis/test_plots" in cmd
    print("OK  build_mkhtml_command (single)")
    print(f"    cmd = {cmd}")

    cmd2 = build_mkhtml_command(
        ["/data/analysis/a.yoda", "/data/analysis/b.yoda"],
        "/data/analysis/comparison_plots",
    )
    assert "/data/analysis/a.yoda" in cmd2
    assert "/data/analysis/b.yoda" in cmd2
    assert "-o /data/analysis/comparison_plots" in cmd2
    print("OK  build_mkhtml_command (multi)")
    print(f"    cmd = {cmd2}")


def test_local_to_docker_path():
    local = str(DATA_DIR / "analysis" / "test.yoda")
    docker_path = local_to_docker_path(local)
    assert docker_path == "/data/analysis/test.yoda"
    print("OK  local_to_docker_path (yoda)")
    print(f"    {local} -> {docker_path}")

    local2 = str(DATA_DIR / "runs" / "test" / "Events" / "run_01" / "file.hepmc.gz")
    docker_path2 = local_to_docker_path(local2)
    assert docker_path2 == "/data/runs/test/Events/run_01/file.hepmc.gz"
    print("OK  local_to_docker_path (hepmc)")


def test_generate_tab_has_signal():
    script_tab = ScriptTab()
    gen_tab = GenerateTab(script_tab)
    assert hasattr(gen_tab, "run_succeeded"), "GenerateTab must have run_succeeded signal"
    print("OK  GenerateTab.run_succeeded signal exists")


def test_analysis_tab_has_signal():
    tab = AnalysisTab()
    assert hasattr(tab, "run_succeeded"), "AnalysisTab must have run_succeeded signal"
    print("OK  AnalysisTab.run_succeeded signal exists")


def test_plot_tab_export_html_button():
    tab = PlotTab()
    assert hasattr(tab, "btn_html"), "PlotTab must have btn_html"
    assert tab.btn_html.text() == "Export HTML"
    print("OK  PlotTab.btn_html exists")


def test_main_window_workflow():
    from hep_gui.gui.main_window import MainWindow
    w = MainWindow()
    assert hasattr(w, "_workflow"), "MainWindow must have _workflow"
    assert isinstance(w._workflow, WorkflowEngine)
    print("OK  MainWindow._workflow is WorkflowEngine")


if __name__ == "__main__":
    test_workflow_gen_to_analysis()
    test_workflow_analysis_to_plots()
    test_build_mkhtml_command()
    test_local_to_docker_path()
    test_generate_tab_has_signal()
    test_analysis_tab_has_signal()
    test_plot_tab_export_html_button()
    test_main_window_workflow()
    print("\nAll T19 tests passed.")
