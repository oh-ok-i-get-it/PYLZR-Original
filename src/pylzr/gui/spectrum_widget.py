import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout


class SpectrumWidget(QWidget):
    def __init__(self, audio_input):
        super().__init__()
        self._audio  = audio_input
        self._traces = {}

        pg.setConfigOptions(antialias=True)
        self._gfx = pg.GraphicsLayoutWidget()
        self._build_plots()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._gfx)
        self.setLayout(layout)

    def _build_plots(self):
        chunk = self._audio.chunk
        rate  = self._audio.rate

        wf_x = pg.AxisItem(orientation='bottom')
        wf_x.setTicks([[(0, '0'), (1024, '1024'), (2048, '2048'), (3072, '3072'), (4096, '4096')]])
        self.waveform = self._gfx.addPlot(title='WAVEFORM', row=1, col=1, axisItems={'bottom': wf_x})
        self.waveform.setYRange(0, 255, padding=0)
        self.waveform.setXRange(0, 2 * chunk, padding=0.005)

        sp_x = pg.AxisItem(orientation='bottom')
        sp_x.setTicks([[(np.log10(10),    '10Hz'),  (np.log10(100),   '100Hz'),
                         (np.log10(250),   '250Hz'), (np.log10(400),   '400Hz'),
                         (np.log10(1000),  '1kHz'),  (np.log10(22050), '22kHz')]])
        self.spectrum = self._gfx.addPlot(title='SPECTRUM', row=2, col=1, axisItems={'bottom': sp_x})
        self.spectrum.setLogMode(x=True, y=True)
        self.spectrum.setYRange(-4, 0, padding=0)
        self.spectrum.setXRange(np.log10(20), np.log10(rate / 2), padding=0.005)

        for plot in (self.waveform, self.spectrum):
            plot.getViewBox().keyPressEvent = lambda ev: ev.ignore()

    def update_waveform(self, data: np.ndarray):
        if 'waveform' not in self._traces:
            self._traces['waveform'] = self.waveform.plot(pen='c', width=3)
        self._traces['waveform'].setData(self._audio.waveform_x, data)

    def update_spectrum(self, low: np.ndarray, med: np.ndarray, high: np.ndarray):
        for name, data, axis in (
            ('spectrum_low',  low,  self._audio.f_low),
            ('spectrum_med',  med,  self._audio.f_med),
            ('spectrum_high', high, self._audio.f_high),
        ):
            if name not in self._traces:
                pen = {'spectrum_low': 'y', 'spectrum_med': 'b', 'spectrum_high': 'm'}[name]
                self._traces[name] = self.spectrum.plot(pen=pen, width=3)
            self._traces[name].setData(axis, data)
