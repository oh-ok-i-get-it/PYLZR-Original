from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QFont


class LogPanel(QWidget):
    """In-app console that displays messages emitted by AppLogger."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 2, 4, 4)
        layout.setSpacing(2)

        label = QLabel('Console')
        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)
        self._text.setMaximumBlockCount(500)
        self._text.setFixedHeight(130)

        font = QFont('Monospace')
        font.setStyleHint(QFont.TypeWriter)
        font.setPointSize(9)
        self._text.setFont(font)
        self._text.setStyleSheet(
            'QPlainTextEdit { background-color: #1a1a1a; color: #d4d4d4; border: 1px solid #333; }'
        )

        layout.addWidget(label)
        layout.addWidget(self._text)
        self.setLayout(layout)

    @pyqtSlot(str)
    def append_message(self, text: str):
        self._text.appendPlainText(text)
        sb = self._text.verticalScrollBar()
        sb.setValue(sb.maximum())
