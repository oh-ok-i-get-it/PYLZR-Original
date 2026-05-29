import pyaudio
import numpy as np
from ..core import CHUNK, SAMPLE_RATE
from ..core.app_logger import logger


class AudioInput:
    """Manages the PyAudio capture stream and precomputes display/analysis axes.

    Owns the hardware stream lifecycle. Call read_chunk() each frame and
    close() on shutdown.

    Pass device_index to open a specific input device; None uses the system
    default. Call get_input_devices() on an existing instance to enumerate
    available devices for the UI.
    """

    def __init__(self, chunk: int = CHUNK, rate: int = SAMPLE_RATE,
                 device_index: int | None = None):
        self.chunk = chunk
        self.rate  = rate

        # FFT bin boundaries matching FFTWorker's split points
        self.lo_cut   = chunk // 128
        self.med_cut  = chunk // 4
        self.hi_cut   = chunk // 2 + 1
        self.sp_scale = 2.0 / (128.0 * chunk)

        # Precomputed axes for waveform and spectrum plots
        self.waveform_x = np.arange(0, 2 * chunk, 2)
        self.f_low  = np.linspace(rate / chunk, rate / 128, self.lo_cut)
        self.f_med  = np.linspace(rate / 128, rate / 4,  self.med_cut - self.lo_cut)
        self.f_high = np.linspace(rate / 4,   rate / 2,  self.hi_cut  - self.med_cut)

        self.timer_interval_ms = int(chunk / rate * 1000)

        self._pa = pyaudio.PyAudio()

        # Resolve device index and human-readable name
        try:
            dev_info = (
                self._pa.get_default_input_device_info()
                if device_index is None
                else self._pa.get_device_info_by_index(device_index)
            )
            self.device_index = int(dev_info['index'])
            self.device_name  = dev_info['name']
        except Exception:
            self.device_index = device_index
            self.device_name  = 'Unknown'

        self._stream = self._pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=rate,
            input=True,
            frames_per_buffer=chunk,
            input_device_index=self.device_index,
        )
        logger.info(f'Audio: opened "{self.device_name}" (chunk={chunk}, rate={rate}Hz)')

    def get_input_devices(self) -> list[tuple[int, str]]:
        """Return (index, name) for every available input device."""
        devices = []
        for i in range(self._pa.get_device_count()):
            try:
                info = self._pa.get_device_info_by_index(i)
                if info.get('maxInputChannels', 0) > 0:
                    devices.append((int(info['index']), info['name']))
            except Exception:
                pass
        return devices

    def read_chunk(self) -> np.ndarray:
        """Read one chunk from the hardware stream. Returns int16 array."""
        raw = self._stream.read(self.chunk, exception_on_overflow=False)
        return np.frombuffer(raw, dtype=np.int16)

    def close(self):
        self._stream.stop_stream()
        self._stream.close()
        self._pa.terminate()
        logger.info(f'Audio: stream closed ("{self.device_name}")')
