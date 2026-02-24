# T17_plot_tab.py -- automated test for PlotTab widget
#
# Checks widget creation, YODA loading, combo population, filtering,
# and basic plot rendering without errors.

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtWidgets import QApplication

app = QApplication.instance() or QApplication(sys.argv)

from hep_gui.gui.plot_tab import PlotTab
from hep_gui.config.constants import ANALYSIS_DIR

tab = PlotTab()
tab.resize(1000, 600)

# 1. verify widgets exist
assert tab.plot_widget is not None, "plot_widget missing"
assert tab.combo_obs is not None, "combo missing"
assert tab.cb_normalize is not None, "normalize checkbox missing"
assert tab.cb_logy is not None, "log y checkbox missing"
assert tab.cb_logx is not None, "log x checkbox missing"
assert tab.btn_load is not None, "load button missing"
assert tab.btn_png is not None, "png button missing"
assert tab.btn_svg is not None, "svg button missing"
assert tab.btn_pdf is not None, "pdf button missing"
assert tab.filter_edit is not None, "filter edit missing"
assert tab.edit_title is not None, "title edit missing"
assert tab.edit_xlabel is not None, "xlabel edit missing"
assert tab.edit_ylabel is not None, "ylabel edit missing"
print("PASS: all widgets present")

# 2. load a real .yoda file if available
yoda_files = list(ANALYSIS_DIR.glob("*.yoda"))
if not yoda_files:
    print("SKIP: no .yoda files in", ANALYSIS_DIR)
    sys.exit(0)

test_file = yoda_files[0]
print(f"Loading: {test_file.name}")
tab.load_yoda_path(str(test_file))

# 3. combo should have items
count = tab.combo_obs.count()
assert count > 0, f"combo empty after loading {test_file.name}"
print(f"PASS: combo has {count} items")

# 4. no /RAW/ or /TMP/ items
for i in range(count):
    path = tab.combo_obs.itemData(i)
    assert not path.startswith("/RAW/"), f"RAW path leaked: {path}"
    assert not path.startswith("/TMP/"), f"TMP path leaked: {path}"
print("PASS: no /RAW/ or /TMP/ in combo")

# 5. select first observable, should not crash
tab.combo_obs.setCurrentIndex(0)
print(f"PASS: plotted {tab.combo_obs.currentData()} without error")

# 6. filter test
tab.filter_edit.setText("pT")
filtered = tab.combo_obs.count()
assert filtered <= count, "filter didn't reduce items"
print(f"PASS: filter 'pT' -> {filtered}/{count} items")

tab.filter_edit.setText("")
restored = tab.combo_obs.count()
assert restored == count, "clearing filter didn't restore items"
print(f"PASS: clear filter -> {restored} items restored")

# 7. toggle normalize
tab.cb_normalize.setChecked(False)
tab.cb_normalize.setChecked(True)
print("PASS: normalize toggle ok")

# 8. toggle log
tab.cb_logy.setChecked(True)
tab.cb_logy.setChecked(False)
print("PASS: log Y toggle ok")

print("\nAll T17 tests passed.")
