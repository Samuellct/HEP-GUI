import numpy as np

from hep_gui.config.constants import AXIS_LABELS


def build_step_coords(edges, values):
    """Build step-function x,y arrays for histogram rendering."""
    n = len(values)
    x = np.empty(2 * n + 2)
    y = np.empty(2 * n + 2)
    x[0] = edges[0]
    y[0] = 0
    for i in range(n):
        x[1 + 2 * i] = edges[i]
        x[2 + 2 * i] = edges[i + 1]
        y[1 + 2 * i] = values[i]
        y[2 + 2 * i] = values[i]
    x[-1] = edges[-1]
    y[-1] = 0
    return x, y


def auto_log_scale(edges, values):
    """Heuristic for log axes. Returns (xlog, ylog)."""
    edges = np.asarray(edges)
    xlog = False
    if edges.min() > 0 and edges.max() / edges.min() > 30:
        xlog = True

    positive = values[values > 0]
    ylog = False
    if len(positive) > 1 and positive.max() / positive.min() > 100:
        ylog = True

    return xlog, ylog


def compute_view_range(edges_list, vals_list, xlog, ylog):
    """Compute axis limits from all plotted datasets. Returns (xmin, xmax, ymin, ymax)."""
    all_edges = np.concatenate(edges_list)
    all_vals = np.concatenate(vals_list)

    if xlog:
        pos_edges = all_edges[all_edges > 0]
        if len(pos_edges) == 0:
            x_min, x_max = 1, 10
        else:
            x_min, x_max = pos_edges.min(), pos_edges.max()
    else:
        x_min, x_max = all_edges.min(), all_edges.max()
        pad = (x_max - x_min) * 0.02
        x_min -= pad
        x_max += pad

    positive_vals = all_vals[all_vals > 0]
    if ylog:
        if len(positive_vals) == 0:
            y_min, y_max = 1, 10
        else:
            y_min = positive_vals.min() * 0.3
            y_max = positive_vals.max() * 3.0
    else:
        y_min = 0
        y_max = all_vals.max() * 1.1 if len(all_vals) > 0 else 1

    return x_min, x_max, y_min, y_max


def get_axis_labels(path):
    """Lookup axis labels by path prefix. Returns (xlabel, ylabel)."""
    for prefix, labels in AXIS_LABELS.items():
        if path.startswith(prefix):
            return labels
    # fallback: last path component as xlabel
    parts = path.rstrip("/").split("/")
    return parts[-1] if parts else path, ""
