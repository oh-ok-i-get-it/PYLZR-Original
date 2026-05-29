import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, pyqtSlot

from ..core import (
    AVG_COUNT_RATE_DEFAULT, DM_TIME_RATE,
    DEFAULT_LOW_THRESHOLDS, DEFAULT_HIGH_THRESHOLDS,
    WINDOW_W, WINDOW_H,
)
from ..core import text_styles as txt
from ..core.app_logger import logger
from ..audio    import AudioInput
from ..analysis import FFTWorker, AudioAnalyzer, SoundMode
from ..midi     import MIDIOutput, KeyboardMapper
from .spectrum_widget import SpectrumWidget
from .control_panel   import ControlPanel
from .log_panel       import LogPanel, AvgPanel


class PyLZR(QWidget):
    """Top-level application window. Owns all subsystem instances and wires
    them together through Qt signals and direct method calls.

    This class is intentionally thin — business logic lives in the
    audio/, analysis/, and midi/ packages.
    """

    _processAudio = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyLZR : SSP3CTRUM')
        self.setGeometry(100, 100, WINDOW_W, WINDOW_H)

        # Subsystems
        self.audio     = AudioInput()
        self.midi_out  = MIDIOutput()
        self.key_map   = KeyboardMapper(self.midi_out)
        self.analyzer  = AudioAnalyzer(AVG_COUNT_RATE_DEFAULT)
        self.soundmode = SoundMode(
            *DEFAULT_LOW_THRESHOLDS,
            *DEFAULT_HIGH_THRESHOLDS,
            self.midi_out,
            dm_toggle_rate=int(DM_TIME_RATE / AVG_COUNT_RATE_DEFAULT),
        )

        # GUI panels
        self.spectrum_widget = SpectrumWidget(self.audio)
        self.controls        = ControlPanel()
        self.log_panel       = LogPanel()
        self.avg_panel       = AvgPanel()

        bottom_row = QHBoxLayout()
        bottom_row.addWidget(self.log_panel, stretch=3)
        bottom_row.addWidget(self.avg_panel, stretch=1)

        layout = QVBoxLayout()
        layout.addWidget(self.controls)
        layout.addWidget(self.spectrum_widget)
        layout.addLayout(bottom_row)
        self.setLayout(layout)

        # Logger → log panel
        logger.message_logged.connect(self.log_panel.append_message)

        # Control panel → subsystem wiring
        self.controls.count_rate_changed.connect(self._on_count_rate)
        self.controls.low_cutoff_changed.connect(self._on_low_cutoff)
        self.controls.high_cutoff_changed.connect(self._on_high_cutoff)
        self.controls.sound_mode_toggled.connect(self._toggle_sound_mode)

        # FFT worker thread
        self.fft_thread = QThread(self)
        self.fft_worker = FFTWorker(
            sp_scale=self.audio.sp_scale,
            lo_cut=self.audio.lo_cut,
            med_cut=self.audio.med_cut,
            hi_cut=self.audio.hi_cut,
        )
        self.fft_worker.moveToThread(self.fft_thread)
        self.fft_thread.start()
        self._processAudio.connect(self.fft_worker.process, Qt.QueuedConnection)
        self.fft_worker.resultReady.connect(self._on_spectrum_ready)

        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._update)
        self.timer.start(self.audio.timer_interval_ms)

    # ------------------------------------------------------------------
    # Audio loop
    # ------------------------------------------------------------------

    def _update(self):
        try:
            chunk = self.audio.read_chunk()
            # Normalize int16 (±32767) to 0-255 for display; raw chunk is already zero-mean for FFT
            wf_display = ((chunk.astype(np.int32) >> 8) + 128).astype(np.int16)
            self.spectrum_widget.update_waveform(wf_display)
            self._processAudio.emit(chunk.copy())
        except IOError as e:
            print(f'Audio I/O Error: {e}')
            logger.error(f'Audio I/O Error: {e}')

    @pyqtSlot(np.ndarray, np.ndarray, np.ndarray)
    def _on_spectrum_ready(self, low: np.ndarray, med: np.ndarray, high: np.ndarray):
        self.spectrum_widget.update_spectrum(low, med, high)
        result = self.analyzer.push(low.mean(), high.mean())
        if result is not None:
            low_avg, high_avg = result
            self.soundmode.advance_dm_counter()
            if self.midi_out.sm_ON:
                self.soundmode.check_mode(low_avg, high_avg)
            self.controls.status_label.setText(
                f'Low Avg: {low_avg:.6f} | High Avg: {high_avg:.6f}'
            )
            self.avg_panel.append_avgs(low_avg, high_avg)
            self.controls.update_sound_modes(self.soundmode.low_mode, self.soundmode.high_mode)
            print(
                f'{txt.YELLOW}{txt.I}LOW: {txt.IOFF}{txt.B}{low_avg:.2f}{txt.BOFF}\t'
                f'{txt.PURPLE}{txt.I}HIGH: {txt.IOFF}{txt.B}{high_avg:.2f}{txt.RESET}'
            )

    # ------------------------------------------------------------------
    # Control panel handlers
    # ------------------------------------------------------------------

    def _on_count_rate(self, val: int):
        self.analyzer.count_rate = val
        self.soundmode.set_dm_toggle_rate(DM_TIME_RATE / val)

    def _on_low_cutoff(self, mode: int, val: int):
        self.soundmode.set_cutoff(val, mode, high=False)

    def _on_high_cutoff(self, mode: int, val: int):
        self.soundmode.set_cutoff(val, mode, high=True)

    def _toggle_sound_mode(self):
        self.midi_out.toggle_sm()
        self.controls.sync_sound_mode(self.midi_out.sm_ON)

    # ------------------------------------------------------------------
    # Qt event overrides
    # ------------------------------------------------------------------

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == 16777248:  # Left Shift — toggle sound mode
            self._toggle_sound_mode()
        else:
            self.key_map.handle_key(event.key())
        self.controls.status_label.setText(f'Key: {event.text()} (code {event.key()})')
        super().keyPressEvent(event)

    def closeEvent(self, event):
        self.timer.stop()
        self.audio.close()
        self.fft_thread.quit()
        self.fft_thread.wait()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PyLZR()
    window.show()
    sys.exit(app.exec_())
