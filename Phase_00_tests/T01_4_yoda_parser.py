# T01_4_yoda_parser.py -- custom YODA text parser + validation

import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

import config

YODA_FILE = config.ANALYSIS_DIR / "test_ggH_100.yoda"

SUPPORTED_1D = {"ESTIMATE1D", "HISTO1D", "BINNEDESTIMATE", "BINNEDHISTO"}
SUPPORTED_COUNTER = {"COUNTER"}
SKIPPED_TYPES = {"ESTIMATE0D"}


@dataclass
class YodaHisto1D:
    path: str
    title: str
    edges: list[float]
    values: np.ndarray
    err_dn: np.ndarray | None = None
    err_up: np.ndarray | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class YodaCounter:
    path: str
    sum_w: float
    sum_w2: float
    num_entries: float


# regex for BEGIN line -- captures the type keyword and the path
# e.g. "BEGIN YODA_ESTIMATE1D_V3 /MC_JETS/jet_pT_1"
# also handles angle-bracket types like BINNEDESTIMATE<S>
_RE_BEGIN = re.compile(r"^BEGIN YODA_(\w+(?:<\w+>)?)_V3\s+(.+)$")


def _parse_float(s):
    """Parse a single value, turning 'nan' and '---' into NaN."""
    s = s.strip()
    if s == "---" or s == "nan":
        return float("nan")
    return float(s)


def _parse_edges(line):
    """Parse 'Edges(A1): [1.0e+01, 2.0e+01, ...]' into a list of floats."""
    bracket_start = line.index("[")
    bracket_end = line.index("]")
    inner = line[bracket_start + 1 : bracket_end]
    return [float(x.strip()) for x in inner.split(",")]


def parse_yoda(filepath):
    """Parse a YODA V3 text file into a dict of path -> YodaHisto1D | YodaCounter."""
    results = {}
    skipped_counts = Counter()

    with open(filepath, "r") as f:
        line = f.readline()
        while line:
            m = _RE_BEGIN.match(line.strip())
            if not m:
                line = f.readline()
                continue

            raw_type = m.group(1)
            block_path = m.group(2).strip()

            # strip angle-bracket suffixes for type matching (BINNEDESTIMATE<I> -> BINNEDESTIMATE)
            sub_type = ""
            if "<" in raw_type:
                base_type, sub_type = raw_type.split("<")[0], raw_type.split("<")[1].rstrip(">")
            else:
                base_type = raw_type

            # skip string-binned types (<S>) -- can't plot those
            if sub_type.upper() == "S":
                skipped_counts[raw_type] += 1
                while line and not line.startswith("END "):
                    line = f.readline()
                line = f.readline()
                continue

            if base_type in SKIPPED_TYPES:
                skipped_counts[base_type] += 1
                # skip to END line
                while line and not line.startswith("END "):
                    line = f.readline()
                line = f.readline()
                continue

            if base_type not in SUPPORTED_1D and base_type not in SUPPORTED_COUNTER:
                skipped_counts[base_type] += 1
                while line and not line.startswith("END "):
                    line = f.readline()
                line = f.readline()
                continue

            # read metadata block until ---
            metadata = {}
            title = ""
            line = f.readline()
            while line and line.strip() != "---":
                if ":" in line:
                    key, _, val = line.partition(":")
                    key = key.strip()
                    val = val.strip()
                    if key == "Title":
                        title = val
                    else:
                        metadata[key] = val
                line = f.readline()

            # after ---, read data section until END
            edges = None
            data_rows = []
            line = f.readline()
            while line and not line.startswith("END "):
                stripped = line.strip()
                if stripped.startswith("Edges(A1):"):
                    edges = _parse_edges(stripped)
                elif stripped.startswith("#") or stripped.startswith("ErrorLabels:"):
                    pass  # column header or error labels, skip
                elif stripped:
                    cols = stripped.split()
                    data_rows.append([_parse_float(c) for c in cols])
                line = f.readline()

            # build the object
            if base_type in SUPPORTED_COUNTER:
                if data_rows:
                    row = data_rows[0]
                    obj = YodaCounter(
                        path=block_path,
                        sum_w=row[0] if len(row) > 0 else 0.0,
                        sum_w2=row[1] if len(row) > 1 else 0.0,
                        num_entries=row[2] if len(row) > 2 else 0.0,
                    )
                    results[block_path] = obj

            elif base_type in SUPPORTED_1D:
                if not edges or not data_rows:
                    line = f.readline()
                    continue

                # BINNEDESTIMATE = finalized (like ESTIMATE1D), BINNEDHISTO = raw (like HISTO1D)
                is_estimate = base_type in ("ESTIMATE1D", "BINNEDESTIMATE")

                # prefer finalized over raw when both share a path
                existing = results.get(block_path)
                if existing and isinstance(existing, YodaHisto1D):
                    existing_is_estimate = existing.metadata.get("Type") in ("ESTIMATE1D", "BINNEDESTIMATE")
                    if existing_is_estimate and not is_estimate:
                        line = f.readline()
                        continue

                if is_estimate:
                    values = np.array([r[0] for r in data_rows])
                    err_dn = np.array([r[1] if len(r) > 1 else float("nan") for r in data_rows])
                    err_up = np.array([r[2] if len(r) > 2 else float("nan") for r in data_rows])
                else:
                    # HISTO1D: first col is sumW
                    values = np.array([r[0] for r in data_rows])
                    err_dn = None
                    err_up = None

                metadata["Type"] = base_type
                obj = YodaHisto1D(
                    path=block_path,
                    title=title,
                    edges=edges,
                    values=values,
                    err_dn=err_dn,
                    err_up=err_up,
                    metadata=metadata,
                )
                results[block_path] = obj

            line = f.readline()

    return results, skipped_counts


def main():
    if not YODA_FILE.exists():
        print(f"YODA file not found: {YODA_FILE}")
        sys.exit(1)

    size_mb = YODA_FILE.stat().st_size / 1024 / 1024
    print(f"Parsing {YODA_FILE.name} ({size_mb:.1f} MB)...")

    results, skipped = parse_yoda(YODA_FILE)

    # summary by type
    type_counts = Counter()
    for obj in results.values():
        if isinstance(obj, YodaHisto1D):
            type_counts[obj.metadata.get("Type", "?")] += 1
        elif isinstance(obj, YodaCounter):
            type_counts["COUNTER"] += 1

    print(f"\nParsed: {len(results)} objects")
    for t, n in sorted(type_counts.items()):
        print(f"  {t}: {n}")
    if skipped:
        print(f"Skipped:")
        for t, n in sorted(skipped.items()):
            print(f"  {t}: {n}")

    # detail on a few known MC_JETS histos
    print("\n--- MC_JETS samples ---")
    # list all MC_JETS paths
    mc_paths = sorted(p for p in results if p.startswith("/MC_JETS/"))
    print(f"  MC_JETS histos: {len(mc_paths)}")
    for p in mc_paths[:10]:
        print(f"    {p}")
    if len(mc_paths) > 10:
        print(f"    ... ({len(mc_paths) - 10} more)")

    sample_paths = [
        "/MC_JETS/jet_pT_1",
        "/MC_JETS/jet_eta_1",
    ]
    for path in sample_paths:
        h = results.get(path)
        if not h or not isinstance(h, YodaHisto1D):
            print(f"  {path}: NOT FOUND")
            continue
        nbins = len(h.edges) - 1
        nonzero = int(np.count_nonzero(~np.isnan(h.values) & (h.values != 0)))
        print(f"  {h.path} ({h.metadata.get('Type', '?')})")
        print(f"    bins: {nbins}, range: [{h.edges[0]:.1f}, {h.edges[-1]:.1f}]")
        print(f"    non-zero: {nonzero}/{nbins}")
        if h.err_dn is not None:
            has_err = int(np.count_nonzero(~np.isnan(h.err_dn)))
            print(f"    errors defined: {has_err}/{nbins}")

    # counter check
    print("\n--- Counters ---")
    for path in ["/RAW/_EVTCOUNT", "/_EVTCOUNT"]:
        c = results.get(path)
        if c and isinstance(c, YodaCounter):
            print(f"  {path}: sumW={c.sum_w:.4e}, entries={c.num_entries:.0f}")

    print("\nDone.")


if __name__ == "__main__":
    main()
