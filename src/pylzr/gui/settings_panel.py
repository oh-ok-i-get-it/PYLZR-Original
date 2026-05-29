from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFrame,
)
from PyQt5.QtCore import Qt, pyqtSignal

_W = 280   # fixed panel width

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


def _hdivider() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setFixedHeight(1)
    f.setStyleSheet(_DIVIDER_STYLE)
    return f


class SettingsPanel(QWidget):
    """Floating settings panel anchored below the gear button.

    Positioned as a child widget of the main window with no layout slot —
    shown/hidden and repositioned by _toggle_settings in main_window.

    control_mode_changed emits 'MIDI' or 'DMX'. DMX is selectable but is a
    no-op until the DMX output layer is implemented.
    """

    control_mode_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('SettingsPanel')
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(_PANEL_STYLE)
        self.setFixedWidth(_W)
        self._build()
        self.adjustSize()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Connections section ───────────────────────────────────────────
        conn_wrap = QWidget()
        conn_wrap.setStyleSheet('background: transparent;')
        cv = QVBoxLayout(conn_wrap)
        cv.setContentsMargins(14, 10, 14, 10)
        cv.setSpacing(8)

        sec_label = QLabel('CONNECTIONS')
        sec_label.setStyleSheet(_SECTION_STYLE)
        cv.addWidget(sec_label)

        self._audio_dot = _dot()
        self._audio_val = QLabel('—')
        self._audio_val.setStyleSheet(_VALUE_STYLE)

        self._midi_dot = _dot()
        self._midi_val = QLabel('—')
        self._midi_val.setStyleSheet(_VALUE_STYLE)

        self._dmx_dot = _dot()
        self._dmx_val = QLabel('—')
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
            lbl.setFixedWidth(56)
            row.addWidget(dot)
            row.addWidget(lbl)
            row.addWidget(val)
            row.addStretch(1)
            cv.addLayout(row)

        root.addWidget(conn_wrap)
        root.addWidget(_hdivider())

        # ── Control Mode section ──────────────────────────────────────────
        mode_wrap = QWidget()
        mode_wrap.setStyleSheet('background: transparent;')
        mv = QVBoxLayout(mode_wrap)
        mv.setContentsMargins(14, 10, 14, 12)
        mv.setSpacing(8)

        mode_label = QLabel('CONTROL MODE')
        mode_label.setStyleSheet(_SECTION_STYLE)
        mv.addWidget(mode_label)

        self._combo = QComboBox()
        self._combo.setStyleSheet(_COMBO_STYLE)
        self._combo.addItem('MIDI')
        self._combo.addItem('DMX  (coming soon)')
        self._combo.setToolTip('DMX output is not yet implemented.')
        self._combo.currentIndexChanged.connect(self._on_mode_changed)
        mv.addWidget(self._combo)

        root.addWidget(mode_wrap)

    # ── Public status setters ─────────────────────────────────────────────

    def set_audio_status(self, connected: bool, detail: str = ''):
        self._audio_dot.setStyleSheet(_IND_ON if connected else _IND_OFF)
        self._audio_val.setText(detail or ('OK' if connected else 'Error'))

    def set_midi_status(self, connected: bool, port_name: str = ''):
        self._midi_dot.setStyleSheet(_IND_ON if connected else _IND_OFF)
        label = port_name or ('OK' if connected else 'Error')
        if len(label) > 24:
            label = label[:22] + '…'
        self._midi_val.setText(label)

    def set_dmx_status(self, connected: bool = False, detail: str = 'Not connected'):
        self._dmx_dot.setStyleSheet(_IND_NA)
        self._dmx_val.setText(detail)

    # ── Private ───────────────────────────────────────────────────────────

    def _on_mode_changed(self, index: int):
        self.control_mode_changed.emit('MIDI' if index == 0 else 'DMX')
