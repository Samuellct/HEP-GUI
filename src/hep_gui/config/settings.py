import json

from hep_gui.config.constants import SETTINGS_FILE

DEFAULTS = {
    "last_script_dir": "",
    "last_yoda_dir": "",
    "normalize_default": True,
    "window_width": 1200,
    "window_height": 800,
}


def load_settings():
    if not SETTINGS_FILE.exists():
        return dict(DEFAULTS)
    try:
        with open(SETTINGS_FILE) as f:
            stored = json.load(f)
        merged = dict(DEFAULTS)
        merged.update(stored)
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULTS)


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)
