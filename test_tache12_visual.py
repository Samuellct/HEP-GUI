import sys
sys.path.insert(0, "src")

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow

from hep_gui.gui.log_panel import LogPanel

app = QApplication(sys.argv)

win = QMainWindow()
win.setWindowTitle("LogPanel -- visual test")
win.resize(800, 500)

panel = LogPanel()
win.setCentralWidget(panel)
win.show()

# simulate MG5-like log output
fake_lines = [
    "MadGraph5_aMC@NLO v3.6.7",
    "INFO: loading model sm",
    "INFO: importing model HAHM_asymmetric_UFO",
    "INFO: Generating Feynman diagrams",
    "gfortran -O -w -fbounds-check -ffixed-line-length-132",
    "compiling SubProcesses/P1_gg_h_h_ffff",
    "compiling SubProcesses/P1_gg_h_h_ffff/matrix1.f",
    "linking ../lib/libdhelas.a",
    "ar cru libmodel.a coupl.o",
    "ranlib ../lib/libmodel.a",
    "creating library ../lib/libpdf.a",
    "WARNING: process has large number of diagrams",
    "INFO: running survey",
    "INFO: Running Pythia8 shower",
    "ERROR: Pythia8 initialization failed (fake error for test)",
    "INFO: Events generated successfully",
    "WARNING: cross section uncertainty is large",
    "INFO: Done.",
]

i = [0]

def add_line():
    if i[0] < len(fake_lines):
        panel.append_line(fake_lines[i[0]])
        i[0] += 1

# add lines one by one, 200ms apart (simulates streaming)
timer = QTimer()
timer.timeout.connect(add_line)
timer.start(200)

print("Visual test launched. Check:")
print("  - Red lines for ERROR")
print("  - Orange lines for WARNING")
print("  - Toggle 'Hide build output' to hide gfortran/compiling/linking lines")
print("  - 'Save log' and 'Clear' buttons")
print("Close the window when done.")

app.exec()
