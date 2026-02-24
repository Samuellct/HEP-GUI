"""TACHE 14 -- ScriptTab automated verification."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtWidgets import QApplication

from hep_gui.gui.script_tab import ScriptTab

app = QApplication.instance() or QApplication(sys.argv)

TEST_SCRIPT = ROOT / "data" / "scripts" / "test_ggH_100.txt"

tab = ScriptTab()

# 1. widgets exist
assert tab.editor is not None, "editor missing"
assert tab.btn_open is not None, "btn_open missing"
assert tab.btn_save is not None, "btn_save missing"
assert len(tab._spinboxes) == 4, f"expected 4 spinboxes, got {len(tab._spinboxes)}"
print("[OK] widgets exist")

# 2. load test script
tab.load_file(str(TEST_SCRIPT))
text = tab.get_script_text()
assert len(text) > 0, "editor empty after load"
assert tab.get_current_path() == str(TEST_SCRIPT), "current path wrong"
print("[OK] file loaded")

# 3. form values parsed correctly
assert tab._spinboxes["nevents"].value() == 100, f"nevents={tab._spinboxes['nevents'].value()}"
assert tab._spinboxes["iseed"].value() == 12346, f"iseed={tab._spinboxes['iseed'].value()}"
assert tab._spinboxes["ebeam1"].value() == 6800, f"ebeam1={tab._spinboxes['ebeam1'].value()}"
assert tab._spinboxes["ebeam2"].value() == 6800, f"ebeam2={tab._spinboxes['ebeam2'].value()}"
print("[OK] form values correct")

# 4. form -> editor sync
tab._spinboxes["nevents"].setValue(500)
text = tab.get_script_text()
assert "set nevents = 500" in text, f"nevents not updated in text"
print("[OK] form->editor sync works")

# 5. get_script_text returns content
assert "import model" in tab.get_script_text(), "get_script_text missing content"
print("[OK] get_script_text works")

print("\n=== ALL T14 TESTS PASSED ===")
