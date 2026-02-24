import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from hep_gui.config.constants import APP_NAME, APP_VERSION


def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
