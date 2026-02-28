# Changelog

All notable changes to this project will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [1.0.0-beta]

### Added
- `hep_gui.spec` : PyInstaller spec file (one-dir, Windows, no console)
- `scripts/build.bat` : build script for .exe

### Changed
- `config/constants.py` : frozen-aware ROOT path, version bump to 1.0.0-beta
- `main.py` : sys.path hack guarded behind frozen check

### Notes
- Output: `dist/hep-gui/` (160 MB), requires `data/` copied alongside
- Prerequisite: Docker Desktop installed

---

## [0.11.0-beta]

### Added
- Auto-pull Docker image in GenerateTab and AnalysisTab when it is missing
- `diagnose_docker_error()` to handle silent failures

### Changed
- `core/docker_interface.py` : PullWorker handles tags without ":"
- `gui/generate_tab.py` : auto-pull + diagnostics in error handler
- `gui/analysis_tab.py` : auto-pull + diagnostics in error handler
- `gui/plot_tab.py` : merged QMarginsF import, QMessageBox for all Docker errors
- `config/constants.py` : version bump to 0.11.0-beta

---

## [0.10.0-beta]

### Added
- `core/workflow_engine.py` : pipeline orchestration (Generation -> Analysis -> Plots)
- Export HTML button in PlotTab : rivet-mkhtml via Docker 4.0.2

### Changed
- `gui/generate_tab.py` : added `run_succeeded` signal emitting .hepmc path
- `gui/analysis_tab.py` : added `run_succeeded` signal emitting .yoda path
- `gui/plot_tab.py` : added Export HTML button and MkHtmlDialog
- `gui/main_window.py` : instantiate WorkflowEngine for tab-to-tab data flow
- `core/rivet_build.py` : renamed `hepmc_to_docker_path` to `local_to_docker_path`, added `build_mkhtml_command`

---

## [0.9.0-beta]

### Added
- `gui/analysis_tab.py` : onglet Analysis
- `core/rivet_build.py` : utilitaires commande Rivet et rivet-build

### Changed
- `gui/main_window.py` : remplacement placeholder Analysis par AnalysisTab
- `config/constants.py` : ajout RIVET_ANALYSES (3 tiers, 24 analyses MC_*)

---

## [0.8.0-beta]

### Added
- `gui/plot_tab.py` : onglet Plots

### Changed
- `gui/main_window.py` : replacement placeholder Plots by PlotTab
- `config/constants.py` : added COLORS palette for multi-dataset overlay

---

## [0.7.0-beta]

### Added
- `core/yoda_parser.py` : YODA parser perso v3
- `utils/normalization.py` : unit area normalization
- `utils/plot_helpers.py` : step coords, auto log scale, view range, axis labels

### Changed
- `config/constants.py` : added AXIS_LABELS lookup table

---

## [0.6.0-beta]

### Added
- `gui/generate_tab.py` : Generation tab (MG5+Pythia8 Docker run)

### Changed
- `gui/main_window.py` : replacement placeholder Generation by GenerateTab

---

## [0.5.0-beta]

### Added
- `gui/script_tab.py` : onglet Script

### Changed
- `gui/main_window.py` : replacement placeholder Script by ScriptTab

---

## [0.4.0-beta]

### Added
- `gui/main_window.py` : fenetre principale

### Changed
- `main.py` : utilise MainWindow au lieu du QMainWindow

---

## [0.3.0-beta]

### Added
- `gui/log_panel.py` : panneau de logs

---

## [0.2.0-beta]

### Added
- `core/docker_interface.py` : DockerWorker, PullWorker, check_docker, check_image

---

## [0.1.0-beta]

### Added
- `src/hep_gui/` : structure projet (config/, core/, gui/, utils/, models/)
- `config/constants.py` : constantes centralisées
- `config/settings.py` : lecture/ecriture settings.json avec valeurs par defaut
- `main.py` : QMainWindow

---

## [1.0.0-alpha]

### Added
- `T01_6_poc_app.py` : mini full POC
- Phase 01 (tests composants) completed

---

## [0.8.0-alpha]

### Added
- `test_ggH_100_30.txt` : second script MG5 (ms=30 GeV)
- `T01_5_pyqtgraph_plots.py` : test PyQtGraph (step histos, log auto, normalisation, 38+ observables)

### Changed
- `T01_4_yoda_parser.py` : ajout support BINNEDESTIMATE et BINNEDHISTO (jet_multi_*, etc.)

---

## [0.7.0-alpha]

### Added
- `T01_4_yoda_parser.py` : parser YODA custom (ESTIMATE1D)

---

## [0.6.0-alpha]

### Added
- `T01_3_rivet_run.py` : test Rivet analysis + rivet-mkhtml

---

## [0.5.0-alpha]

### Added
- `test_ggH_100.txt` : script MG5 adapte pour test (100 events, paths Docker)
- `HAHM_asymmetric_UFO` : modele UFO copie in data/models/
- `T01_2_madgraph_run.py` : test run MG5+Pythia8 dans Docker

---

## [0.4.1-alpha]

### Added
- `T01_1_docker_streaming.py` : test streaming logs Docker dans PySide6

---

## [0.4.0-alpha]

### Added
- `T00_3_pyside6_thread.py` : test PySide6 QThread + signals

---

## [0.3.0-alpha]

### Added
- `T00_2_docker_basics.py` : test docker-py connection

---

## [0.2.0-alpha]

### Added
- Docker image 4.1.2
- MG5 stable path
- `DOCKER_SHELL` config for login shell requirement

---

## [0.1.0-alpha]

### Added
- Initial project structure
- Planning tests phase alpha
- `requirements.txt`
- `Phase_00_tests/` : config.py, T00_0_check_imports.py

