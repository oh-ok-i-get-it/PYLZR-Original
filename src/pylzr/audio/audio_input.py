import pyaudio
import numpy as np
from ..core import CHUNK, SAMPLE_RATE


class AudioInput:
    """Manages the PyAudio capture stream and precomputes display/analysis axes.

    Owns the hardware stream lifecycle. Call read_chunk() each frame and
    close() on shutdown.
    """

    def __init__(self, chunk: int = CHUNK, rate: int = SAMPLE_RATE):
        self.chunk = chunk
        self.rate  = rate

        # FFT bin boundaries matching FFTWorker's split points
        self.lo_cut  = chunk // 128
        self.med_cut = chunk // 4
        self.hi_cut  = chunk // 2 + 1
        self.sp_scale = 2.0 / (128.0 * chunk)

        # Precomputed axes for waveform and spectrum plots
        self.waveform_x = np.arange(0, 2 * chunk, 2)
        self.f_low  = np.linspace(0,          rate / 128, self.lo_cut)
        self.f_med  = np.linspace(rate / 128, rate / 4,  self.med_cut - self.lo_cut)
        self.f_high = np.linspace(rate / 4,   rate / 2,  self.hi_cut  - self.med_cut)

        self.timer_interval_ms = int(chunk / rate * 1000)

        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=rate,
            input=True,
            output=True,
            frames_per_buffer=chunk,
        )

    def read_chunk(self) -> np.ndarray:
        """Read one chunk from the hardware stream. Returns int16 array."""
        raw = self._stream.read(self.chunk, exception_on_overflow=False)
        return np.frombuffer(raw, dtype=np.int16)

    def close(self):
        self._stream.stop_stream()
        self._stream.close()
        self._pa.terminate()
