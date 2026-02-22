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

# stable symlink
MG5_BIN = "/work/MG5_aMC/bin/mg5_aMC"
MG5_BIN_401 = "/work/MG5_aMC_v3_5_5/bin/mg5_aMC" # 4.0.1 only (fallback)

# container needs login shell to source /etc/profile.d/ (rivet, yoda, ROOT)
DOCKER_SHELL = "bash -l -c"
