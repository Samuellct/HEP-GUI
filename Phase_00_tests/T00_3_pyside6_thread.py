# T00_3_pyside6_thread.py

import sys
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget,
)
from PySide6.QtCore import QThread, Signal


class Worker(QThread):
    log_line = Signal(str)

    def run(self):
        for i in range(1, 11):
            self.log_line.emit(f"iteration {i}/10")
            time.sleep(0.5)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("T00_3: PySide6 + QThread")

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)

        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.on_start)

        layout = QVBoxLayout()
        layout.addWidget(self.log_view)
        layout.addWidget(self.start_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_start(self):
        self.start_btn.setEnabled(False)
        self.worker = Worker()
        self.worker.log_line.connect(self.log_view.append)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self):
        self.log_view.append("done.")
        self.start_btn.setEnabled(True)


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec())
