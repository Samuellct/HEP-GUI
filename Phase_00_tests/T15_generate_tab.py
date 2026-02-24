"""TACHE 15 -- GenerateTab automated verification."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtWidgets import QApplication

from hep_gui.gui.script_tab import ScriptTab
from hep_gui.gui.generate_tab import GenerateTab, _extract_run_name, _build_command
from hep_gui.config.constants import MG5_BIN, PYTHIA8_LIB

app = QApplication.instance() or QApplication(sys.argv)

TEST_SCRIPT = ROOT / "data" / "scripts" / "test_ggH_100.txt"
SCRIPT_TEXT = TEST_SCRIPT.read_text(encoding="utf-8")

# -- test 1: widgets exist --
script_tab = ScriptTab()
tab = GenerateTab(script_tab)

assert tab.btn_run is not None, "btn_run missing"
assert tab.btn_cancel is not None, "btn_cancel missing"
assert tab.log_panel is not None, "log_panel missing"
assert tab.label_status is not None, "label_status missing"
assert tab.label_script is not None, "label_script missing"
print("[OK] test 1: widgets exist")

# -- test 2: initial state (no script loaded) --
assert not tab.btn_run.isEnabled(), "Run should be disabled without script"
assert not tab.btn_cancel.isEnabled(), "Cancel should be disabled initially"
assert tab.label_status.text() == "Ready", f"status={tab.label_status.text()}"
print("[OK] test 2: initial state correct")

# -- test 3: initial state with script loaded --
script_tab.load_file(str(TEST_SCRIPT))
tab2 = GenerateTab(script_tab)
assert tab2.btn_run.isEnabled(), "Run should be enabled with script loaded"
assert not tab2.btn_cancel.isEnabled(), "Cancel should be disabled initially"
print("[OK] test 3: state with script loaded")

# -- test 4: _extract_run_name --
name = _extract_run_name(SCRIPT_TEXT)
assert name == "test_ggH_100", f"run_name={name}"

assert _extract_run_name("output /work/my_run_42\nlaunch /work/my_run_42") == "my_run_42"
assert _extract_run_name("no output line here") is None
print("[OK] test 4: _extract_run_name")

# -- test 5: _build_command --
cmd = _build_command("_run_test.txt", "test_ggH_100")

assert MG5_BIN in cmd, f"MG5_BIN not in command"
assert f"{PYTHIA8_LIB}/libpythia8.so" in cmd, "LD_PRELOAD missing"
assert "/data/scripts/_run_test.txt" in cmd, "script path missing"
assert "mkdir -p /data/runs/test_ggH_100" in cmd, "mkdir missing"
assert "cp -r /work/test_ggH_100/Events /data/runs/test_ggH_100/" in cmd, "cp missing"
# ; between MG5 and mkdir (not &&) because MG5 exit code 1 on quit
assert f"/data/scripts/_run_test.txt ; mkdir" in cmd, "should use ; not && after MG5"
print("[OK] test 5: _build_command")

# -- test 6: get_run_name --
assert tab.get_run_name() is None, "run_name should be None before any run"
print("[OK] test 6: get_run_name")

print("\n=== ALL T15 TESTS PASSED ===")
