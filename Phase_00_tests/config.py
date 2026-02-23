# config.py -- paths and constants for tests

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR     = ROOT / "data"
MODELS_DIR   = DATA_DIR / "models"
SCRIPTS_DIR  = DATA_DIR / "scripts"
RUNS_DIR     = DATA_DIR / "runs"
ANALYSIS_DIR = DATA_DIR / "analysis"

DOCKER_IMAGE          = "hepstore/rivet-tutorial:4.1.2"
DOCKER_IMAGE_FALLBACK = "hepstore/rivet-tutorial:4.0.1"

# 4.1.2 has broken ROOT/cling (segfault on `import yoda`), so rivet-mkhtml
# (Python script) can't run on it. 4.0.2 works and reads 4.1.2 .yoda files.
DOCKER_IMAGE_MKHTML   = "hepstore/rivet-tutorial:4.0.2"

# stable symlink
MG5_BIN = "/work/MG5_aMC/bin/mg5_aMC"
MG5_BIN_401 = "/work/MG5_aMC_v3_5_5/bin/mg5_aMC" # 4.0.1 only (fallback)

# container needs login shell to source /etc/profile.d/ (rivet, yoda, ROOT)
DOCKER_SHELL = "bash -l -c"

# MG5 bundles Pythia8 8.316 but container has system 8.315 in /usr/local/lib.
# LD_PRELOAD needed to force the correct lib (ABI mismatch on Settings::mode).
PYTHIA8_LIB = "/work/MG5_aMC/HEPTools/pythia8/lib"
