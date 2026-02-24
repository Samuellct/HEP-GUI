"""T18 -- AnalysisTab widget + rivet_build utilities."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtWidgets import QApplication, QMenu

app = QApplication.instance() or QApplication(sys.argv)

from hep_gui.gui.analysis_tab import AnalysisTab
from hep_gui.core.rivet_build import (
    build_rivet_command, build_rivetbuild_command,
    hepmc_to_docker_path, yoda_output_name,
)
from hep_gui.config.constants import RIVET_ANALYSES, DATA_DIR


def test_widget_creation():
    tab = AnalysisTab()
    assert tab.log_panel is not None
    assert tab.btn_run is not None
    assert tab.btn_cancel is not None
    assert tab.btn_browse is not None
    assert tab.btn_presets is not None
    assert tab.btn_upload_cc is not None
    assert tab.input_hepmc is not None
    assert tab.input_analyses is not None
    assert tab.label_status is not None
    print("OK  widget creation")


def test_initial_state():
    tab = AnalysisTab()
    # no hepmc selected => Run disabled, Cancel disabled
    assert not tab.btn_run.isEnabled(), "Run should be disabled initially"
    assert not tab.btn_cancel.isEnabled(), "Cancel should be disabled initially"
    assert tab.input_analyses.text() == "MC_JETS", "default analysis"
    print("OK  initial state")


def test_set_hepmc_path():
    tab = AnalysisTab()
    fake_path = str(DATA_DIR / "runs" / "test" / "Events" / "run_01" / "test.hepmc.gz")
    tab.set_hepmc_path(fake_path)
    assert tab.btn_run.isEnabled(), "Run should be enabled after setting hepmc path"
    assert tab.input_hepmc.text() == fake_path
    print("OK  set_hepmc_path")


def test_build_rivet_command():
    cmd = build_rivet_command(
        ["MC_JETS", "MC_MET"],
        "/data/runs/test/Events/run_01/test.hepmc.gz",
        "/data/analysis/test.yoda",
    )
    assert "rivet" in cmd
    assert "--analysis=MC_JETS,MC_MET" in cmd
    assert "/data/runs/test/Events/run_01/test.hepmc.gz" in cmd
    assert "-o /data/analysis/test.yoda" in cmd
    assert "mkdir -p /data/analysis" in cmd
    print("OK  build_rivet_command")
    print(f"    cmd = {cmd}")


def test_build_rivetbuild_command():
    cmd = build_rivetbuild_command("MyAnalysis.cc")
    assert "rivet-build" in cmd
    assert "RivetMyAnalysis.so" in cmd
    assert "MyAnalysis.cc" in cmd
    assert "cd /data/analysis" in cmd
    print("OK  build_rivetbuild_command")
    print(f"    cmd = {cmd}")


def test_hepmc_to_docker_path():
    local = str(DATA_DIR / "runs" / "test_ggH" / "Events" / "run_01" / "file.hepmc.gz")
    docker_path = hepmc_to_docker_path(local)
    assert docker_path == "/data/runs/test_ggH/Events/run_01/file.hepmc.gz"
    print("OK  hepmc_to_docker_path")
    print(f"    {local} -> {docker_path}")


def test_yoda_output_name():
    assert yoda_output_name("test_ggH_100.hepmc.gz") == "test_ggH_100.yoda"
    assert yoda_output_name("run.hepmc") == "run.yoda"
    assert yoda_output_name("path/to/data.hepmc.gz") == "data.yoda"
    print("OK  yoda_output_name")


def test_presets_menu():
    tab = AnalysisTab()
    menu = tab.btn_presets.menu()
    assert menu is not None, "Presets button should have a menu"

    # collect all action names from submenus
    all_names = []
    for action in menu.actions():
        sub = action.menu()
        if sub:
            for sub_action in sub.actions():
                all_names.append(sub_action.text())

    # check a few from each tier
    for name in ["MC_XS", "MC_JETS", "MC_ELECTRONS", "MC_TTBAR", "MC_PHOTONS"]:
        assert name in all_names, f"{name} missing from presets menu"

    total = sum(len(v) for v in RIVET_ANALYSES.values())
    assert len(all_names) == total, f"expected {total} presets, got {len(all_names)}"
    print(f"OK  presets menu ({len(all_names)} items)")


if __name__ == "__main__":
    test_widget_creation()
    test_initial_state()
    test_set_hepmc_path()
    test_build_rivet_command()
    test_build_rivetbuild_command()
    test_hepmc_to_docker_path()
    test_yoda_output_name()
    test_presets_menu()
    print("\nAll T18 tests passed.")
