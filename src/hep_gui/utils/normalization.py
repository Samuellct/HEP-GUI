import numpy as np


def normalize_to_area(edges, values, err_dn, err_up):
    """Normalize histogram to unit area (equivalent to yodascale -c '.* 1')."""
    widths = np.diff(edges)
    area = np.nansum(values * widths)
    if area == 0:
        return values, err_dn, err_up
    values = values / area
    if err_dn is not None:
        err_dn = err_dn / area
        err_up = err_up / area
    return values, err_dn, err_up
