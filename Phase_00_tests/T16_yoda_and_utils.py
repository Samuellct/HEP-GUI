"""TACHE 16 -- YODA parser + plot helpers + normalization verification."""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from hep_gui.core.yoda_parser import parse_yoda, filter_plottable, YodaHisto1D, YodaCounter
from hep_gui.utils.normalization import normalize_to_area
from hep_gui.utils.plot_helpers import build_step_coords, auto_log_scale, compute_view_range, get_axis_labels

YODA_FILE = ROOT / "data" / "analysis" / "test_ggH_100.yoda"

# === 1. parse_yoda ===
assert YODA_FILE.exists(), f"test file missing: {YODA_FILE}"
results = parse_yoda(YODA_FILE)
assert len(results) > 1000, f"expected thousands of objects, got {len(results)}"

h = results.get("/MC_JETS/jet_pT_1")
assert h is not None, "/MC_JETS/jet_pT_1 not found"
assert isinstance(h, YodaHisto1D), f"expected YodaHisto1D, got {type(h)}"
assert len(h.edges) > 1, "edges empty"
assert len(h.values) == len(h.edges) - 1, "values/edges mismatch"
assert h.err_dn is not None, "ESTIMATE1D should have errors"

counters = [v for v in results.values() if isinstance(v, YodaCounter)]
assert len(counters) > 0, "no counters found"
print(f"[OK] test 1: parse_yoda ({len(results)} objects, {len(counters)} counters)")

# === 2. filter_plottable ===
plottable = filter_plottable(results)
assert len(plottable) > 0, "no plottable histos"
for path in plottable:
    assert not path.startswith("/RAW/"), f"RAW leaked: {path}"
    assert not path.startswith("/TMP/"), f"TMP leaked: {path}"
    assert not path.startswith("/_"), f"private leaked: {path}"
    assert "[" not in path, f"variation leaked: {path}"
    parts = path.split("/")
    if len(parts) >= 3:
        assert not parts[2].startswith("_"), f"private histo leaked: {path}"
for obj in plottable.values():
    assert isinstance(obj, YodaHisto1D), f"non-histo in plottable: {type(obj)}"
print(f"[OK] test 2: filter_plottable ({len(plottable)} histos)")

# === 3. normalize_to_area ===
edges = [0.0, 1.0, 2.0, 3.0]
vals = np.array([2.0, 4.0, 6.0])
err_d = np.array([0.2, 0.4, 0.6])
err_u = np.array([0.2, 0.4, 0.6])
nv, nd, nu = normalize_to_area(edges, vals, err_d, err_u)
area = np.sum(nv * np.diff(edges))
assert abs(area - 1.0) < 1e-10, f"area after normalization: {area}"
# zero area edge case
nv0, _, _ = normalize_to_area([0, 1], np.array([0.0]), None, None)
assert nv0[0] == 0.0, "zero area should return unchanged"
print("[OK] test 3: normalize_to_area")

# === 4. build_step_coords ===
edges4 = [0, 1, 2, 3]
vals4 = np.array([5.0, 10.0, 3.0])
x, y = build_step_coords(edges4, vals4)
assert len(x) == 2 * 3 + 2, f"x length: {len(x)}"
assert len(y) == 2 * 3 + 2, f"y length: {len(y)}"
assert y[0] == 0 and y[-1] == 0, "should start/end at 0"
assert x[0] == 0 and x[-1] == 3, "x should span edges"
print("[OK] test 4: build_step_coords")

# === 5. auto_log_scale ===
xlog, ylog = auto_log_scale(np.array([1, 10, 100, 1000]), np.array([1e-3, 1e-1, 1e1]))
assert xlog is True, "edges [1..1000] should be xlog"
assert ylog is True, "values spanning 4 decades should be ylog"

xlog2, ylog2 = auto_log_scale(np.array([-1, 0, 1]), np.array([5.0, 6.0]))
assert xlog2 is False, "negative edges should not be xlog"
assert ylog2 is False, "values spanning <2 decades should not be ylog"
print("[OK] test 5: auto_log_scale")

# === 6. compute_view_range ===
xmin, xmax, ymin, ymax = compute_view_range(
    [np.array([0, 1, 2])], [np.array([5.0, 10.0])], False, False
)
assert ymin == 0, f"linear ymin should be 0, got {ymin}"
assert ymax > 10.0, f"linear ymax should be > 10, got {ymax}"

xmin_l, xmax_l, ymin_l, ymax_l = compute_view_range(
    [np.array([1, 10, 100])], [np.array([0.01, 10.0])], True, True
)
assert ymin_l > 0, f"log ymin should be > 0, got {ymin_l}"
assert xmin_l >= 1, f"log xmin should be >= 1, got {xmin_l}"
print("[OK] test 6: compute_view_range")

# === 7. get_axis_labels ===
xl, yl = get_axis_labels("/MC_JETS/jet_pT_1")
assert xl == "pT [GeV]", f"xlabel: {xl}"
assert "dpT" in yl, f"ylabel: {yl}"

xl2, yl2 = get_axis_labels("/SOME_UNKNOWN/observable")
assert xl2 == "observable", f"fallback xlabel: {xl2}"
assert yl2 == "", f"fallback ylabel: {yl2}"
print("[OK] test 7: get_axis_labels")

print("\n=== ALL T16 TESTS PASSED ===")
