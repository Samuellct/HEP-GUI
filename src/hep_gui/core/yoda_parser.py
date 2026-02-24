import re
from dataclasses import dataclass, field

import numpy as np


_SUPPORTED_1D = {"ESTIMATE1D", "HISTO1D", "BINNEDESTIMATE", "BINNEDHISTO"}
_SUPPORTED_COUNTER = {"COUNTER"}
_SKIPPED_TYPES = {"ESTIMATE0D"}

_RE_BEGIN = re.compile(r"^BEGIN YODA_(\w+(?:<\w+>)?)_V3\s+(.+)$")


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


def _parse_float(s):
    s = s.strip()
    if s == "---" or s == "nan":
        return float("nan")
    return float(s)


def _parse_edges(line):
    bracket_start = line.index("[")
    bracket_end = line.index("]")
    inner = line[bracket_start + 1 : bracket_end]
    return [float(x.strip()) for x in inner.split(",")]


def parse_yoda(filepath):
    """Parse a YODA V3 file. Returns dict of path -> YodaHisto1D | YodaCounter."""
    results = {}

    with open(filepath, "r") as f:
        line = f.readline()
        while line:
            m = _RE_BEGIN.match(line.strip())
            if not m:
                line = f.readline()
                continue

            raw_type = m.group(1)
            block_path = m.group(2).strip()

            # BINNEDESTIMATE<I> -> base=BINNEDESTIMATE, sub=I
            if "<" in raw_type:
                base_type = raw_type.split("<")[0]
                sub_type = raw_type.split("<")[1].rstrip(">")
            else:
                base_type = raw_type
                sub_type = ""

            # string-binned -> not plottable
            if sub_type.upper() == "S":
                while line and not line.startswith("END "):
                    line = f.readline()
                line = f.readline()
                continue

            if base_type in _SKIPPED_TYPES:
                while line and not line.startswith("END "):
                    line = f.readline()
                line = f.readline()
                continue

            if base_type not in _SUPPORTED_1D and base_type not in _SUPPORTED_COUNTER:
                while line and not line.startswith("END "):
                    line = f.readline()
                line = f.readline()
                continue

            # metadata until ---
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

            # data section until END
            edges = None
            data_rows = []
            line = f.readline()
            while line and not line.startswith("END "):
                stripped = line.strip()
                if stripped.startswith("Edges(A1):"):
                    edges = _parse_edges(stripped)
                elif stripped.startswith("#") or stripped.startswith("ErrorLabels:"):
                    pass
                elif stripped:
                    cols = stripped.split()
                    data_rows.append([_parse_float(c) for c in cols])
                line = f.readline()

            # build object
            if base_type in _SUPPORTED_COUNTER:
                if data_rows:
                    row = data_rows[0]
                    results[block_path] = YodaCounter(
                        path=block_path,
                        sum_w=row[0] if len(row) > 0 else 0.0,
                        sum_w2=row[1] if len(row) > 1 else 0.0,
                        num_entries=row[2] if len(row) > 2 else 0.0,
                    )

            elif base_type in _SUPPORTED_1D:
                if not edges or not data_rows:
                    line = f.readline()
                    continue

                # YODA V3 includes underflow + overflow rows
                n_bins = len(edges) - 1
                if len(data_rows) == n_bins + 2:
                    data_rows = data_rows[1:-1]

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
                    values = np.array([r[0] for r in data_rows])
                    err_dn = None
                    err_up = None

                metadata["Type"] = base_type
                results[block_path] = YodaHisto1D(
                    path=block_path,
                    title=title,
                    edges=edges,
                    values=values,
                    err_dn=err_dn,
                    err_up=err_up,
                    metadata=metadata,
                )

            line = f.readline()

    return results


def filter_plottable(histos):
    """Keep only YodaHisto1D entries suitable for plotting."""
    out = {}
    for path, obj in histos.items():
        if not isinstance(obj, YodaHisto1D):
            continue
        if path.startswith("/RAW/") or path.startswith("/TMP/"):
            continue
        if path.startswith("/_"):
            continue
        # private histos: /<analysis>/_<name>
        parts = path.split("/")
        if len(parts) >= 3 and parts[2].startswith("_"):
            continue
        # weight variations
        if "[" in path:
            continue
        out[path] = obj
    return out
