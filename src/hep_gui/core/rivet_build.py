from pathlib import Path, PurePosixPath

from hep_gui.config.constants import DATA_DIR, DOCKER_SHELL


def build_rivet_command(analyses, hepmc_docker_path, output_yoda_path):
    """Build the rivet Docker command string."""
    ana_str = ",".join(a.strip() for a in analyses if a.strip())
    return (
        f'{DOCKER_SHELL} "'
        f"mkdir -p /data/analysis "
        f"&& rivet --analysis={ana_str} {hepmc_docker_path} "
        f"-o {output_yoda_path}"
        f'"'
    )


def build_rivetbuild_command(cc_filename):
    """Build the rivet-build Docker command string."""
    name = Path(cc_filename).stem
    return (
        f'{DOCKER_SHELL} "'
        f"cd /data/analysis "
        f"&& rivet-build Rivet{name}.so {cc_filename}"
        f'"'
    )


def hepmc_to_docker_path(hepmc_local_path):
    """Convert a Windows path under data/ to a Docker /data/ path."""
    local = Path(hepmc_local_path).resolve()
    data = DATA_DIR.resolve()
    rel = local.relative_to(data)
    return str(PurePosixPath("/data") / rel.as_posix())


def yoda_output_name(hepmc_path):
    """Derive .yoda filename from HepMC path.

    e.g. test_ggH_100.hepmc.gz -> test_ggH_100.yoda
    """
    name = Path(hepmc_path).name
    # strip .gz, .hepmc, etc.
    stem = name
    for suffix in (".gz", ".hepmc"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
    return stem + ".yoda"
