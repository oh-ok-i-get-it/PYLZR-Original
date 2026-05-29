from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QFont


def _console_text_widget() -> QPlainTextEdit:
    t = QPlainTextEdit()
    t.setReadOnly(True)
    t.setFixedHeight(130)
    font = QFont('Monospace')
    font.setStyleHint(QFont.TypeWriter)
    font.setPointSize(9)
    t.setFont(font)
    t.setStyleSheet(
        'QPlainTextEdit { background-color: #1a1a1a; color: #d4d4d4; border: 1px solid #333; }'
    )
    return t


class LogPanel(QWidget):
    """In-app console that displays messages emitted by AppLogger."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 2, 4, 4)
        layout.setSpacing(2)
        layout.addWidget(QLabel('Console'))
        self._text = _console_text_widget()
        self._text.setMaximumBlockCount(500)
        layout.addWidget(self._text)
        self.setLayout(layout)

    @pyqtSlot(str)
    def append_message(self, text: str):
        self._text.appendPlainText(text)
        sb = self._text.verticalScrollBar()
        sb.setValue(sb.maximum())


class AvgPanel(QWidget):
    """Scrolling display of the 10 most recent low/high windowed averages."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 2, 4, 4)
        layout.setSpacing(2)
        layout.addWidget(QLabel('Averages'))
        self._text = _console_text_widget()
        self._text.setMaximumBlockCount(10)
        layout.addWidget(self._text)
        self.setLayout(layout)

    def append_avgs(self, low_avg: float, high_avg: float):
        self._text.appendPlainText(f'L {low_avg:>10.4f}   H {high_avg:>10.4f}')
        sb = self._text.verticalScrollBar()
        sb.setValue(sb.maximum())
