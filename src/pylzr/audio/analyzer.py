from collections import deque


class AudioAnalyzer:
    def __init__(self, count_rate: int):
        self._count_rate = count_rate
        self._low_scale  = 1000.0  / count_rate
        self._high_scale = 10000.0 / count_rate
        self._low_means  = deque()
        self._high_means = deque()

    @property
    def count_rate(self) -> int:
        return self._count_rate

    @count_rate.setter
    def count_rate(self, val: int):
        self._count_rate = val
        self._low_scale  = 1000.0  / val
        self._high_scale = 10000.0 / val
        self._low_means.clear()
        self._high_means.clear()

    def push(self, low_mean: float, high_mean: float):
        """Accumulate one frame. Returns (low_avg, high_avg) when window fills, else None."""
        self._low_means.append(low_mean)
        self._high_means.append(high_mean)
        if len(self._low_means) >= self._count_rate:
            low_avg  = sum(self._low_means)  * self._low_scale
            high_avg = sum(self._high_means) * self._high_scale
            self._low_means.clear()
            self._high_means.clear()
            return low_avg, high_avg
        return None
