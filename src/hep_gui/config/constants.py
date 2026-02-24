from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent

DATA_DIR     = ROOT / "data"
MODELS_DIR   = DATA_DIR / "models"
SCRIPTS_DIR  = DATA_DIR / "scripts"
RUNS_DIR     = DATA_DIR / "runs"
ANALYSIS_DIR = DATA_DIR / "analysis"

SETTINGS_FILE = ROOT / "settings.json"

APP_NAME    = "HEP-GUI"
APP_VERSION = "0.1.0-beta"

DOCKER_IMAGE          = "hepstore/rivet-tutorial:4.1.2"
DOCKER_IMAGE_FALLBACK = "hepstore/rivet-tutorial:4.0.1"

# 4.1.2 has broken ROOT/cling, rivet-mkhtml can't run on it.
# 4.0.2 works and reads 4.1.2 .yoda files fine.
DOCKER_IMAGE_MKHTML = "hepstore/rivet-tutorial:4.0.2"

# stable symlink in the container
MG5_BIN     = "/work/MG5_aMC/bin/mg5_aMC"
MG5_BIN_401 = "/work/MG5_aMC_v3_5_5/bin/mg5_aMC"

# login shell needed to source /etc/profile.d/ env
DOCKER_SHELL = "bash -l -c"

# MG5 bundles Pythia8 8.316 but system has 8.315, ABI mismatch
PYTHIA8_LIB = "/work/MG5_aMC/HEPTools/pythia8/lib"
