from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QSlider, QPushButton,
)
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
        root = QVBoxLayout()
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(4)

        # ── Top row: avg-rate slider + sound mode button ──────────────
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        rate_group = QGroupBox('Avgs Calc Rate')
        rate_layout = QVBoxLayout()
        rate_layout.setContentsMargins(4, 4, 4, 4)
        self._count_label = QLabel(str(AVG_COUNT_RATE_DEFAULT))
        self._count_label.setStyleSheet('font-weight: bold;')
        count_slider = QSlider(Qt.Horizontal)
        count_slider.setRange(AVG_COUNT_RATE_MIN, AVG_COUNT_RATE_MAX)
        count_slider.setValue(AVG_COUNT_RATE_DEFAULT)
        count_slider.setTickInterval(5)
        count_slider.setTickPosition(QSlider.TicksBelow)
        count_slider.valueChanged.connect(self._on_count_rate)
        rate_layout.addWidget(count_slider)
        rate_layout.addWidget(self._count_label)
        rate_group.setLayout(rate_layout)

        self._sm_button = QPushButton('Sound Mode: OFF')
        self._sm_button.setCheckable(True)
        self._sm_button.setFixedHeight(52)
        self._sm_button.setMinimumWidth(160)
        self._sm_button.setStyleSheet(
            'QPushButton { background-color: #8b0000; color: white; font-weight: bold; font-size: 14px; border-radius: 4px; }'
            'QPushButton:checked { background-color: #006400; color: white; }'
        )
        self._sm_button.clicked.connect(lambda: self.sound_mode_toggled.emit())

        top_row.addWidget(rate_group, stretch=1)
        top_row.addWidget(self._sm_button)
        root.addLayout(top_row)

        # ── Bottom row: low cutoffs (left) | high cutoffs (right) ─────
        cutoff_row = QHBoxLayout()
        cutoff_row.setSpacing(8)

        self._low_sliders  = []
        self._low_labels   = []
        self._high_sliders = []
        self._high_labels  = []

        for side, label_prefix, cutoffs, sliders_list, labels_list, callback in (
            ('Low Cutoffs',  'Low',  self._low_cutoffs,  self._low_sliders,  self._low_labels,  self._on_low_cutoff),
            ('High Cutoffs', 'High', self._high_cutoffs, self._high_sliders, self._high_labels, self._on_high_cutoff),
        ):
            group = QGroupBox(side)
            glayout = QVBoxLayout()
            glayout.setContentsMargins(4, 4, 4, 4)
            glayout.setSpacing(2)
            for mode in range(3):
                name = 'Quiet' if mode == 0 else f'Mode {mode}'
                lbl = QLabel(f'{name}: {cutoffs[mode]}')
                sld = QSlider(Qt.Horizontal)
                sld.setRange(0, CUTOFF_SLIDER_MAX)
                sld.setValue(cutoffs[mode])
                sld.valueChanged.connect(lambda v, m=mode, cb=callback: cb(v, m))
                glayout.addWidget(lbl)
                glayout.addWidget(sld)
                labels_list.append(lbl)
                sliders_list.append(sld)
            group.setLayout(glayout)
            cutoff_row.addWidget(group)

        root.addLayout(cutoff_row)

        # ── Status label ──────────────────────────────────────────────
        self.status_label = QLabel('Press any key')
        root.addWidget(self.status_label)

        self.setLayout(root)

    def sync_sound_mode(self, is_on: bool):
        """Sync button visual state to the current sound mode flag."""
        self._sm_button.setChecked(is_on)
        self._sm_button.setText('Sound Mode: ON' if is_on else 'Sound Mode: OFF')

    def _on_count_rate(self, val: int):
        self._count_label.setText(str(val))
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
        name = 'Quiet' if mode == 0 else f'Mode {mode}'
        self._low_labels[mode].setText(f'{name}: {val}')
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
        name = 'Quiet' if mode == 0 else f'Mode {mode}'
        self._high_labels[mode].setText(f'{name}: {val}')
        self.high_cutoff_changed.emit(mode, val)
