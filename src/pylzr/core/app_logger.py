import datetime
from PyQt5.QtCore import QObject, pyqtSignal


class AppLogger(QObject):
    """Central logging service. Emits message_logged for the GUI panel
    and is the only place non-GUI components need to touch for logging.

    Use the module-level `logger` singleton — do not instantiate directly.
    """

    message_logged = pyqtSignal(str)

    def _log(self, level: str, message: str):
        ts = datetime.datetime.now().strftime('%H:%M:%S')
        self.message_logged.emit(f'[{ts}] {level:<7} {message}')

    def debug(self, message: str):
        self._log('DEBUG', message)

    def info(self, message: str):
        self._log('INFO', message)

    def warning(self, message: str):
        self._log('WARNING', message)

    def error(self, message: str):
        self._log('ERROR', message)


logger = AppLogger()
