# Changelog

All notable changes to this project will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [0.3.0-beta] - 2026-02-24

### Added
- `gui/log_panel.py` : panneau de logs

---

## [0.2.0-beta] - 2026-02-24

### Added
- `core/docker_interface.py` : DockerWorker, PullWorker, check_docker, check_image

---

## [0.1.0-beta] - 2026-02-24

### Added
- `src/hep_gui/` : structure projet (config/, core/, gui/, utils/, models/)
- `config/constants.py` : constantes centralisées
- `config/settings.py` : lecture/ecriture settings.json avec valeurs par defaut
- `main.py` : QMainWindow

---

## [1.0.0-alpha] - 2026-02-23

### Added
- `T01_6_poc_app.py` : mini full POC
- Phase 01 (tests composants) completed

---

## [0.8.0-alpha] - 2026-02-23

### Added
- `test_ggH_100_30.txt` : second script MG5 (ms=30 GeV)
- `T01_5_pyqtgraph_plots.py` : test PyQtGraph (step histos, log auto, normalisation, 38+ observables)

### Changed
- `T01_4_yoda_parser.py` : ajout support BINNEDESTIMATE<I> et BINNEDHISTO<I> (jet_multi_*, etc.)

---

## [0.7.0-alpha] - 2026-02-23

### Added
- `T01_4_yoda_parser.py` : parser YODA custom (ESTIMATE1D)

---

## [0.6.0-alpha] - 2026-02-23

### Added
- `T01_3_rivet_run.py` : test Rivet analysis + rivet-mkhtml

---

## [0.5.0-alpha] - 2026-02-23

### Added
- `test_ggH_100.txt` : script MG5 adapte pour test (100 events, paths Docker)
- `HAHM_asymmetric_UFO` : modele UFO copie in data/models/
- `T01_2_madgraph_run.py` : test run MG5+Pythia8 dans Docker

---

## [0.4.1-alpha] - 2026-02-23

### Added
- `T01_1_docker_streaming.py` : test streaming logs Docker dans PySide6

---

## [0.4.0-alpha] - 2026-02-23

### Added
- `T00_3_pyside6_thread.py` : test PySide6 QThread + signals

---

## [0.3.0-alpha] - 2026-02-23

### Added
- `T00_2_docker_basics.py` : test docker-py connection

---

## [0.2.0-alpha] - 2026-02-23

### Added
- Docker image 4.1.2
- MG5 stable path
- `DOCKER_SHELL` config for login shell requirement

---

## [0.1.0-alpha] - 2026-02-22

### Added
- Initial project structure
- Planning tests phase alpha
- `requirements.txt`
- `Phase_00_tests/` : config.py, T00_0_check_imports.py

