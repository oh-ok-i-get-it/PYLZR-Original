import datetime
from PyQt5.QtCore import QObject, pyqtSignal

_COLOR_ERROR   = '#e74c3c'
_COLOR_WARNING = '#d4a017'
_COLOR_DEBUG   = '#666666'


class AppLogger(QObject):
    """Central logging service. Emits (text, hex_color) for the GUI panel.

    Use the module-level `logger` singleton — do not instantiate directly.
    """

    message_logged = pyqtSignal(str, str)  # (formatted text, hex color)

    def _log(self, level: str, message: str, color: str):
        ts = datetime.datetime.now().strftime('%H:%M:%S')
        self.message_logged.emit(f'[{ts}] {level:<7} {message}', color)

    def debug(self, message: str, color: str = _COLOR_DEBUG):
        self._log('DEBUG', message, color)

    def info(self, message: str, color: str = ''):
        self._log('INFO', message, color)

    def warning(self, message: str, color: str = _COLOR_WARNING):
        self._log('WARNING', message, color)

    def error(self, message: str, color: str = _COLOR_ERROR):
        self._log('ERROR', message, color)


logger = AppLogger()
