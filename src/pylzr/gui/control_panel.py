from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QSignalBlocker
from ..core import (
    CUTOFF_SLIDER_MAX,
    AVG_COUNT_RATE_DEFAULT, AVG_COUNT_RATE_MIN, AVG_COUNT_RATE_MAX,
    DEFAULT_LOW_THRESHOLDS, DEFAULT_HIGH_THRESHOLDS,
)


class ControlPanel(QWidget):
    """Slider and button panel for runtime parameter control.

    Emits signals upward so main_window can route changes to the
    appropriate analysis/MIDI components without ControlPanel needing
    direct references to them.
    """

    count_rate_changed  = pyqtSignal(int)
    low_cutoff_changed  = pyqtSignal(int, int)  # (mode_index, value)
    high_cutoff_changed = pyqtSignal(int, int)  # (mode_index, value)
    sound_mode_toggled  = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._low_cutoffs  = list(DEFAULT_LOW_THRESHOLDS)
        self._high_cutoffs = list(DEFAULT_HIGH_THRESHOLDS)
        self._build()

    def _build(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)

        # Avg-rate slider
        self._count_label = QLabel(f'Avgs Calc Rate: {AVG_COUNT_RATE_DEFAULT}')
        count_slider = QSlider(Qt.Horizontal)
        count_slider.setRange(AVG_COUNT_RATE_MIN, AVG_COUNT_RATE_MAX)
        count_slider.setValue(AVG_COUNT_RATE_DEFAULT)
        count_slider.setTickInterval(5)
        count_slider.setTickPosition(QSlider.TicksBelow)
        count_slider.valueChanged.connect(self._on_count_rate)
        layout.addWidget(count_slider)
        layout.addWidget(self._count_label)

        # Low-mode cutoff sliders
        self._low_sliders = []
        self._low_labels  = []
        for mode in range(3):
            name = 'Quiet' if mode == 0 else f'Mode{mode}'
            lbl = QLabel(f'Low {name} Cutoff: {self._low_cutoffs[mode]}')
            sld = QSlider(Qt.Horizontal)
            sld.setRange(0, CUTOFF_SLIDER_MAX)
            sld.setValue(self._low_cutoffs[mode])
            sld.valueChanged.connect(lambda v, m=mode: self._on_low_cutoff(v, m))
            layout.addWidget(lbl)
            layout.addWidget(sld)
            self._low_labels.append(lbl)
            self._low_sliders.append(sld)

        # High-mode cutoff sliders
        self._high_sliders = []
        self._high_labels  = []
        for mode in range(3):
            name = 'Quiet' if mode == 0 else f'Mode{mode}'
            lbl = QLabel(f'High {name} Cutoff: {self._high_cutoffs[mode]}')
            sld = QSlider(Qt.Horizontal)
            sld.setRange(0, CUTOFF_SLIDER_MAX)
            sld.setValue(self._high_cutoffs[mode])
            sld.valueChanged.connect(lambda v, m=mode: self._on_high_cutoff(v, m))
            layout.addWidget(lbl)
            layout.addWidget(sld)
            self._high_labels.append(lbl)
            self._high_sliders.append(sld)

        # Sound mode toggle button
        self._sm_button = QPushButton('Sound Mode: OFF')
        self._sm_button.setCheckable(True)
        self._sm_button.setFixedHeight(40)
        self._sm_button.setStyleSheet(
            'QPushButton { background-color: #8b0000; color: white; font-weight: bold; font-size: 14px; border-radius: 4px; }'
            'QPushButton:checked { background-color: #006400; color: white; }'
        )
        self._sm_button.clicked.connect(lambda: self.sound_mode_toggled.emit())
        layout.addWidget(self._sm_button)

        # Status label
        self.status_label = QLabel('Press any key')
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def sync_sound_mode(self, is_on: bool):
        """Sync button visual state to the current sound mode flag."""
        self._sm_button.setChecked(is_on)
        self._sm_button.setText('Sound Mode: ON' if is_on else 'Sound Mode: OFF')

    def _on_count_rate(self, val: int):
        self._count_label.setText(f'Avgs Calc Rate: {val}')
        self.count_rate_changed.emit(val)

    def _on_low_cutoff(self, val: int, mode: int):
        if mode == 0:
            val = min(val, self._low_cutoffs[1])
        elif mode == 1:
            val = max(val, self._low_cutoffs[0])
            val = min(val, self._low_cutoffs[2])
        else:
            val = max(val, self._low_cutoffs[1])
        sld = self._low_sliders[mode]
        if sld.value() != val:
            with QSignalBlocker(sld):
                sld.setValue(val)
        self._low_cutoffs[mode] = val
        name = 'Quiet' if mode == 0 else f'Mode{mode}'
        self._low_labels[mode].setText(f'Low {name} Cutoff: {val}')
        self.low_cutoff_changed.emit(mode, val)

    def _on_high_cutoff(self, val: int, mode: int):
        if mode == 0:
            val = min(val, self._high_cutoffs[1])
        elif mode == 1:
            val = max(val, self._high_cutoffs[0])
            val = min(val, self._high_cutoffs[2])
        else:
            val = max(val, self._high_cutoffs[1])
        sld = self._high_sliders[mode]
        if sld.value() != val:
            with QSignalBlocker(sld):
                sld.setValue(val)
        self._high_cutoffs[mode] = val
        name = 'Quiet' if mode == 0 else f'Mode{mode}'
        self._high_labels[mode].setText(f'High {name} Cutoff: {val}')
        self.high_cutoff_changed.emit(mode, val)
