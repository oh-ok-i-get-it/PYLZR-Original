from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFrame,
)
from PyQt5.QtCore import Qt, pyqtSignal

_W = 300   # fixed panel width

_PANEL_STYLE = (
    'QWidget#SettingsPanel {'
    '  background: #111111;'
    '  border: 1px solid #333333;'
    '  border-top: 2px solid #58a6ff;'
    '}'
)

_SECTION_STYLE = 'color: #58a6ff; font-size: 9px; font-weight: bold; letter-spacing: 0.08em;'
_LABEL_STYLE   = 'color: #666666; font-size: 10px;'
_VALUE_STYLE   = 'color: #c9d1d9; font-size: 10px;'
_DIVIDER_STYLE = 'background: #222222; border: none;'

_COMBO_STYLE = (
    'QComboBox {'
    '  background: #1a1a1a; color: #c9d1d9;'
    '  border: 1px solid #2e2e2e; border-radius: 3px;'
    '  padding: 4px 8px; font-size: 11px;'
    '}'
    'QComboBox:hover { border-color: #58a6ff; }'
    'QComboBox::drop-down { border: none; width: 18px; }'
    'QComboBox QAbstractItemView {'
    '  background: #1a1a1a; color: #c9d1d9;'
    '  selection-background-color: #252525;'
    '  border: 1px solid #333;'
    '}'
)

_IND_ON  = 'border-radius: 5px; background: #2ecc71;'
_IND_OFF = 'border-radius: 5px; background: #e74c3c;'
_IND_NA  = 'border-radius: 5px; background: #383838;'


def _dot() -> QLabel:
    d = QLabel()
    d.setFixedSize(10, 10)
    d.setStyleSheet(_IND_NA)
    return d


def _section(text: str) -> QLabel:
    l = QLabel(text)
    l.setStyleSheet(_SECTION_STYLE)
    return l


def _hdivider() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setFixedHeight(1)
    f.setStyleSheet(_DIVIDER_STYLE)
    return f


def _wrap(contents_layout, top=10, bottom=10) -> QWidget:
    w = QWidget()
    w.setStyleSheet('background: transparent;')
    contents_layout.setContentsMargins(14, top, 14, bottom)
    w.setLayout(contents_layout)
    return w


class SettingsPanel(QWidget):
    """Floating settings panel anchored below the gear button.

    Positioned as a child widget of the main window with no layout slot —
    shown/hidden and repositioned by _toggle_settings in main_window.

    Signals:
        audio_device_changed(int): emits the PyAudio device index when changed.
        control_mode_changed(str): emits 'MIDI' or 'DMX' when changed.
            DMX is selectable but is a no-op until the DMX layer is built.
    """

    audio_device_changed = pyqtSignal(int)
    control_mode_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('SettingsPanel')
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(_PANEL_STYLE)
        self.setFixedWidth(_W)
        self._device_list: list[tuple[int, str]] = []
        self._build()
        self.adjustSize()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Connections ───────────────────────────────────────────────────
        cv = QVBoxLayout()
        cv.setSpacing(8)
        cv.addWidget(_section('CONNECTIONS'))

        self._audio_dot = _dot()
        self._audio_val = QLabel('—')
        self._audio_val.setStyleSheet(_VALUE_STYLE)
        self._midi_dot  = _dot()
        self._midi_val  = QLabel('—')
        self._midi_val.setStyleSheet(_VALUE_STYLE)
        self._dmx_dot   = _dot()
        self._dmx_val   = QLabel('—')
        self._dmx_val.setStyleSheet(_VALUE_STYLE)

        for dot, lbl_text, val in (
            (self._audio_dot, 'Audio In', self._audio_val),
            (self._midi_dot,  'MIDI',     self._midi_val),
            (self._dmx_dot,   'DMX',      self._dmx_val),
        ):
            row = QHBoxLayout()
            row.setSpacing(8)
            row.setContentsMargins(0, 0, 0, 0)
            lbl = QLabel(lbl_text)
            lbl.setStyleSheet(_LABEL_STYLE)
            lbl.setFixedWidth(52)
            row.addWidget(dot)
            row.addWidget(lbl)
            row.addWidget(val)
            row.addStretch(1)
            cv.addLayout(row)

        root.addWidget(_wrap(cv))
        root.addWidget(_hdivider())

        # ── Audio Device ──────────────────────────────────────────────────
        av = QVBoxLayout()
        av.setSpacing(6)
        av.addWidget(_section('AUDIO DEVICE'))

        self._device_combo = QComboBox()
        self._device_combo.setStyleSheet(_COMBO_STYLE)
        self._device_combo.setPlaceholderText('No input devices found')
        self._device_combo.currentIndexChanged.connect(self._on_device_changed)
        av.addWidget(self._device_combo)

        root.addWidget(_wrap(av))
        root.addWidget(_hdivider())

        # ── Control Mode ──────────────────────────────────────────────────
        mv = QVBoxLayout()
        mv.setSpacing(6)
        mv.addWidget(_section('CONTROL MODE'))

        self._mode_combo = QComboBox()
        self._mode_combo.setStyleSheet(_COMBO_STYLE)
        self._mode_combo.addItem('MIDI')
        self._mode_combo.addItem('DMX  (coming soon)')
        self._mode_combo.setToolTip('DMX output is not yet implemented.')
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mv.addWidget(self._mode_combo)

        root.addWidget(_wrap(mv, bottom=12))

    # ── Connection status setters ─────────────────────────────────────────

    def set_audio_status(self, connected: bool, detail: str = ''):
        self._audio_dot.setStyleSheet(_IND_ON if connected else _IND_OFF)
        label = detail or ('OK' if connected else 'Error')
        if len(label) > 26:
            label = label[:24] + '…'
        self._audio_val.setText(label)

    def set_midi_status(self, connected: bool, port_name: str = ''):
        self._midi_dot.setStyleSheet(_IND_ON if connected else _IND_OFF)
        label = port_name or ('OK' if connected else 'Error')
        if len(label) > 26:
            label = label[:24] + '…'
        self._midi_val.setText(label)

    def set_dmx_status(self, connected: bool = False, detail: str = 'Not connected'):
        self._dmx_dot.setStyleSheet(_IND_NA)
        self._dmx_val.setText(detail)

    # ── Device list population ────────────────────────────────────────────

    def set_audio_devices(self, devices: list[tuple[int, str]], current_index: int):
        """Populate the audio device combo. Call once after AudioInput is created."""
        self._device_list = devices
        self._device_combo.blockSignals(True)
        self._device_combo.clear()
        selected_row = 0
        for row, (idx, name) in enumerate(devices):
            label = name if len(name) <= 36 else name[:34] + '…'
            self._device_combo.addItem(label)
            if idx == current_index:
                selected_row = row
        self._device_combo.setCurrentIndex(selected_row)
        self._device_combo.blockSignals(False)

    # ── Private ───────────────────────────────────────────────────────────

    def _on_device_changed(self, row: int):
        if 0 <= row < len(self._device_list):
            self.audio_device_changed.emit(self._device_list[row][0])

    def _on_mode_changed(self, index: int):
        self.control_mode_changed.emit('MIDI' if index == 0 else 'DMX')
