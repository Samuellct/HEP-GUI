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

# YODA files don't contain axis labels -- these come from Rivet .plot files
# prefix match on histogram path -> (xlabel, ylabel)
# palette for multi-dataset overlay (line = opaque RGB, fill = semi-transparent RGBA)
COLORS = [
    {"line": (31, 119, 180), "fill": (31, 119, 180, 60)},   # blue
    {"line": (255, 127, 14), "fill": (255, 127, 14, 60)},   # orange
    {"line": (44, 160, 44),  "fill": (44, 160, 44, 60)},    # green
    {"line": (214, 39, 40),  "fill": (214, 39, 40, 60)},    # red
    {"line": (148, 103, 189), "fill": (148, 103, 189, 60)},  # purple
    {"line": (140, 86, 75),  "fill": (140, 86, 75, 60)},    # brown
]

RIVET_ANALYSES = {
    "Tier 1 (general)": [
        "MC_XS", "MC_JETS", "MC_MET", "MC_FSPARTICLES", "MC_SUSY",
    ],
    "Tier 2 (channel)": [
        "MC_ELECTRONS", "MC_MUONS", "MC_TAUS", "MC_DILEPTON",
        "MC_DIPHOTON", "MC_HINC", "MC_HJETS", "MC_JETTAGS", "MC_HFJETS",
    ],
    "Tier 3 (specific)": [
        "MC_TTBAR", "MC_WINC", "MC_WJETS", "MC_ZINC", "MC_ZJETS",
        "MC_VH2BB", "MC_HHJETS", "MC_KTSPLITTINGS", "MC_PHOTONINC", "MC_PHOTONS",
    ],
}

AXIS_LABELS = {
    "/MC_JETS/jet_HT":     ("HT [GeV]", "dsigma/dHT [pb/GeV]"),
    "/MC_JETS/jet_eta_":   ("eta", "dsigma/deta [pb]"),
    "/MC_JETS/jet_pT_":    ("pT [GeV]", "dsigma/dpT [pb/GeV]"),
    "/MC_JETS/jet_y_":     ("y", "dsigma/dy [pb]"),
    "/MC_JETS/jet_mass_":  ("m [GeV]", "dsigma/dm [pb/GeV]"),
    "/MC_JETS/jet_multi_": ("N_jet", "sigma [pb]"),
    "/MC_JETS/jets_dR_":   ("dR", "dsigma/ddR [pb]"),
    "/MC_JETS/jets_deta_": ("deta", "dsigma/ddeta [pb]"),
    "/MC_JETS/jets_dphi_": ("dphi", "dsigma/ddphi [pb]"),
    "/MC_JETS/jets_mjj":   ("m_jj [GeV]", "dsigma/dm_jj [pb/GeV]"),
}
