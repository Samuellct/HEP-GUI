# config.py -- paths and constants for tests

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR     = ROOT / "data"
MODELS_DIR   = DATA_DIR / "models"
SCRIPTS_DIR  = DATA_DIR / "scripts"
RUNS_DIR     = DATA_DIR / "runs"
ANALYSIS_DIR = DATA_DIR / "analysis"

# fallback = ATLAS week 2024 tutorial, confirmed working
DOCKER_IMAGE          = "hepstore/rivet-tutorial:4.1.2"
DOCKER_IMAGE_FALLBACK = "hepstore/rivet-tutorial:4.0.1"

# 4.0.1 only
MG5_BIN_401 = "/work/MG5_aMC_v3_5_5/bin/mg5_aMC"
