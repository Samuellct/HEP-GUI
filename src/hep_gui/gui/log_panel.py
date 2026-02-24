import html

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QFileDialog,
)
from PySide6.QtGui import QFont

# patterns that indicate MG5 build output (Fortran compilation, linking, etc.)
_BUILD_PATTERNS = ("gfortran", "compiling", "linking", "ar ", "ranlib", "creating library")


class LogPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._lines = []
        self._filter_build = False

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)

        self._btn_filter = QPushButton("Hide build output")
        self._btn_filter.setCheckable(True)
        self._btn_filter.toggled.connect(self._on_filter_toggled)
        toolbar.addWidget(self._btn_filter)

        toolbar.addStretch()

        btn_save = QPushButton("Save log")
        btn_save.clicked.connect(self._on_save)
        toolbar.addWidget(btn_save)

        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(self.clear)
        toolbar.addWidget(btn_clear)

        self._text_edit = QTextEdit()
        self._text_edit.setReadOnly(True)
        self._text_edit.setFont(QFont("Consolas", 9))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(toolbar)
        layout.addWidget(self._text_edit)

    def append_line(self, text):
        self._lines.append(text)
        if self._filter_build and self._is_build_line(text):
            return
        self._append_html(text)

    def clear(self):
        self._lines.clear()
        self._text_edit.clear()

    def _append_html(self, text):
        sb = self._text_edit.verticalScrollBar()
        at_bottom = sb.value() >= sb.maximum() - 10

        escaped = html.escape(text)
        low = text.lower()
        if "error" in low:
            line_html = f'<span style="color:#cc0000">{escaped}</span>'
        elif "warning" in low:
            line_html = f'<span style="color:#cc7700">{escaped}</span>'
        else:
            line_html = escaped

        self._text_edit.append(line_html)

        if at_bottom:
            sb.setValue(sb.maximum())

    def _is_build_line(self, text):
        low = text.lower()
        return any(p in low for p in _BUILD_PATTERNS)

    def _on_filter_toggled(self, checked):
        self._filter_build = checked
        self._rerender()

    def _rerender(self):
        self._text_edit.clear()
        for line in self._lines:
            if self._filter_build and self._is_build_line(line):
                continue
            self._append_html(line)

    def _on_save(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save log", "", "Text files (*.txt)")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(self._lines))
