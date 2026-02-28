"""T21 -- PyInstaller packaging: frozen-aware paths and build readiness."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtWidgets import QApplication

app = QApplication.instance() or QApplication(sys.argv)


def test_imports():
    from hep_gui.gui.main_window import MainWindow
    from hep_gui.core.docker_interface import DockerWorker, PullWorker
    from hep_gui.core.yoda_parser import parse_yoda
    from hep_gui.core.rivet_build import build_rivet_command
    from hep_gui.utils.normalization import normalize_to_area
    from hep_gui.utils.plot_helpers import build_step_coords
    print("OK  all modules import")


def test_version():
    from hep_gui.config.constants import APP_VERSION
    assert APP_VERSION == "1.0.0-beta", f"expected 1.0.0-beta, got {APP_VERSION}"
    print(f"OK  APP_VERSION = {APP_VERSION}")


def test_root_dev_mode():
    from hep_gui.config import constants
    # in dev mode (not frozen), ROOT should be the project root
    assert not getattr(sys, 'frozen', False), "this test must run in dev mode"
    assert constants.ROOT == ROOT, f"ROOT mismatch: {constants.ROOT} != {ROOT}"
    assert (constants.ROOT / "src").exists(), "ROOT/src/ should exist"
    assert (constants.ROOT / "data").exists(), "ROOT/data/ should exist"
    print(f"OK  ROOT = {constants.ROOT}")


def test_frozen_path_code_exists():
    """Verify that constants.py has the sys.frozen check."""
    constants_path = ROOT / "src" / "hep_gui" / "config" / "constants.py"
    source = constants_path.read_text()
    assert "frozen" in source, "constants.py must check sys.frozen"
    assert "sys.executable" in source, "constants.py must use sys.executable for frozen"
    print("OK  constants.py has frozen-aware ROOT")


def test_main_frozen_guard():
    """Verify that main.py guards sys.path hack behind frozen check."""
    main_path = ROOT / "src" / "hep_gui" / "main.py"
    source = main_path.read_text()
    assert "frozen" in source, "main.py must check sys.frozen"
    print("OK  main.py has frozen guard for sys.path")


def test_spec_file():
    spec = ROOT / "hep_gui.spec"
    assert spec.exists(), "hep_gui.spec must exist"
    content = spec.read_text()
    assert "src/hep_gui/main.py" in content, "spec must point to main.py"
    assert "console=False" in content, "spec must be windowed (no console)"
    assert "one-dir" in content.lower() or "COLLECT" in content, "spec should be one-dir mode"
    print("OK  hep_gui.spec exists and looks correct")


def test_build_script():
    bat = ROOT / "scripts" / "build.bat"
    assert bat.exists(), "scripts/build.bat must exist"
    content = bat.read_text()
    assert "pyinstaller" in content.lower(), "build.bat must call pyinstaller"
    print("OK  scripts/build.bat exists")


def test_main_window():
    from hep_gui.gui.main_window import MainWindow
    w = MainWindow()
    assert "1.0.0-beta" in w.windowTitle()
    print(f"OK  MainWindow title: {w.windowTitle()}")


if __name__ == "__main__":
    test_imports()
    test_version()
    test_root_dev_mode()
    test_frozen_path_code_exists()
    test_main_frozen_guard()
    test_spec_file()
    test_build_script()
    test_main_window()
    print("\nAll T21 tests passed.")
