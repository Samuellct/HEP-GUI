import re

from PySide6.QtWidgets import (
    QWidget, QSplitter, QTextEdit, QVBoxLayout, QHBoxLayout,
    QFormLayout, QSpinBox, QPushButton, QFileDialog, QGroupBox, QLabel,
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from hep_gui.config.constants import SCRIPTS_DIR
from hep_gui.config.settings import load_settings, save_settings


# params tracked in the form: (key, label, min, max, default)
FORM_PARAMS = [
    ("nevents", "nevents",  10, 1_000_000, 100),
    ("iseed",   "iseed",     0,   999_999, 12346),
    ("ebeam1",  "ebeam1 [GeV]", 1, 100_000, 6800),
    ("ebeam2",  "ebeam2 [GeV]", 1, 100_000, 6800),
]


class ScriptTab(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_path = None
        self._syncing = False  # guard against recursive updates

        self._build_ui()
        self._connect_signals()

    # -- UI setup --

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # left: editor
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Consolas", 9))
        self.editor.setAcceptRichText(False)
        self.editor.setPlaceholderText("Open a MG5 script (.txt)...")
        splitter.addWidget(self.editor)

        # right: form + buttons
        right = QWidget()
        right_layout = QVBoxLayout(right)

        # param group
        group = QGroupBox("Run parameters")
        form = QFormLayout(group)

        self._spinboxes = {}
        for key, label, lo, hi, default in FORM_PARAMS:
            sb = QSpinBox()
            sb.setRange(lo, hi)
            sb.setValue(default)
            sb.setProperty("param_key", key)
            form.addRow(label, sb)
            self._spinboxes[key] = sb

        right_layout.addWidget(group)

        # buttons
        btn_layout = QVBoxLayout()
        self.btn_open = QPushButton("Open")
        self.btn_save = QPushButton("Save")
        btn_layout.addWidget(self.btn_open)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addStretch()
        right_layout.addLayout(btn_layout)

        right_layout.addStretch()
        splitter.addWidget(right)

        # 2/3 - 1/3 split
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

    def _connect_signals(self):
        self.btn_open.clicked.connect(self.open_script)
        self.btn_save.clicked.connect(self.save_script)

        for sb in self._spinboxes.values():
            sb.valueChanged.connect(self._on_form_changed)

    # -- form <-> editor sync --

    def _on_form_changed(self):
        if self._syncing:
            return
        sb = self.sender()
        key = sb.property("param_key")
        value = sb.value()
        self._update_line_in_editor(key, value)

    def _update_line_in_editor(self, key, value):
        """Replace `set <key> ...` line in the editor with the new value."""
        text = self.editor.toPlainText()
        # match lines like "set nevents = 100" or "set nevents 100"
        pattern = re.compile(
            rf"^(set\s+{re.escape(key)}\s*=?\s*).*$", re.MULTILINE
        )
        match = pattern.search(text)
        if not match:
            return
        # keep the original prefix (e.g. "set nevents = ") and replace value
        prefix = match.group(1)
        new_line = f"{prefix}{value}"
        new_text = text[:match.start()] + new_line + text[match.end():]
        # preserve cursor
        cursor = self.editor.textCursor()
        pos = cursor.position()
        self._syncing = True
        self.editor.setPlainText(new_text)
        cursor.setPosition(min(pos, len(new_text)))
        self.editor.setTextCursor(cursor)
        self._syncing = False

    def _fill_form_from_text(self, text):
        """Parse `set <key> ...` lines and update spinboxes."""
        self._syncing = True
        for key, sb in self._spinboxes.items():
            pattern = re.compile(
                rf"^set\s+{re.escape(key)}\s*=?\s*(\S+)", re.MULTILINE
            )
            match = pattern.search(text)
            if match:
                try:
                    sb.setValue(int(match.group(1)))
                except ValueError:
                    pass
        self._syncing = False

    # -- public API --

    def open_script(self):
        settings = load_settings()
        start_dir = settings.get("last_script_dir") or str(SCRIPTS_DIR)

        path, _ = QFileDialog.getOpenFileName(
            self, "Open MG5 script", start_dir, "Text files (*.txt);;All (*)"
        )
        if not path:
            return

        self.load_file(path)

        # remember directory
        from pathlib import Path
        settings["last_script_dir"] = str(Path(path).parent)
        save_settings(settings)

    def save_script(self):
        if self._current_path:
            self._write_file(self._current_path)
        else:
            settings = load_settings()
            start_dir = settings.get("last_script_dir") or str(SCRIPTS_DIR)
            path, _ = QFileDialog.getSaveFileName(
                self, "Save MG5 script", start_dir, "Text files (*.txt);;All (*)"
            )
            if not path:
                return
            self._write_file(path)
            self._current_path = path

    def load_file(self, path):
        """Load a script file into the editor (no dialog)."""
        with open(path, encoding="utf-8") as f:
            text = f.read()
        self._current_path = path
        self._syncing = True
        self.editor.setPlainText(text)
        self._syncing = False
        self._fill_form_from_text(text)

    def get_script_text(self):
        return self.editor.toPlainText()

    def get_current_path(self):
        return self._current_path

    def _write_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.editor.toPlainText())
