import numpy as np
from src.config import AUDIO_SAMPLE_RATE, FLUX_THRESHOLD, SPEED_SCALE, DIST_SCALE


class AudioAnalyzer:
    """Real-time audio feature extraction using numpy. Replaces Meyda.js."""

    def __init__(
        self, sample_rate: int = AUDIO_SAMPLE_RATE, buffer_size: int = 2048
    ) -> None:
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self._buffer = np.zeros(buffer_size, dtype=np.float32)
        self._prev_spectrum: np.ndarray | None = None

    def feed(self, pcm_data: bytes) -> None:
        """Add new PCM chunk to buffer. Expects 16-bit signed integer PCM, stereo."""
        samples = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32) / 32768.0
        # Mix stereo to mono
        if len(samples) >= 2:
            samples = samples[::2] * 0.5 + samples[1::2] * 0.5  # simple stereo→mono
        # Shift buffer and append new samples
        n = min(len(samples), self.buffer_size)
        self._buffer = np.roll(self._buffer, -n)
        self._buffer[-n:] = samples[-n:]

    def get_rms(self) -> float:
        """Root Mean Square energy, normalized to ~0-1."""
        rms = float(np.sqrt(np.mean(self._buffer**2)))
        return min(rms * 4.0, 1.0)  # scale up, ambient music is quiet

    def get_spectral_centroid(self) -> float:
        """Spectral centroid, normalized to 0-1."""
        spectrum = np.abs(np.fft.rfft(self._buffer * np.hanning(len(self._buffer))))
        if spectrum.sum() < 1e-10:
            return 0.0
        freqs = np.fft.rfftfreq(len(self._buffer), 1.0 / self.sample_rate)
        centroid = float(np.sum(freqs * spectrum) / np.sum(spectrum))
        nyquist = self.sample_rate / 2.0
        return min(centroid / nyquist, 1.0)

    def get_spectral_flux(self) -> float:
        """Spectral flux: rate of spectral change."""
        spectrum = np.abs(np.fft.rfft(self._buffer * np.hanning(len(self._buffer))))
        if self._prev_spectrum is None:
            self._prev_spectrum = spectrum.copy()
            return 0.0
        diff = spectrum - self._prev_spectrum
        flux = float(np.sum(np.maximum(diff, 0.0)))
        self._prev_spectrum = spectrum.copy()
        # Normalize
        norm = float(np.sum(spectrum)) + 1e-10
        return min(flux / norm, 1.0)

    def analyze(self) -> dict:
        """Return all audio features."""
        return {
            "rms": self.get_rms(),
            "spectral_centroid": self.get_spectral_centroid(),
            "spectral_flux": self.get_spectral_flux(),
        }


class AudioFeedback:
    """Maps audio features to Tolvera visual parameters."""

    def __init__(self, analyzer: AudioAnalyzer) -> None:
        self.analyzer = analyzer
        self.flux_threshold = FLUX_THRESHOLD
        self.speed_scale = SPEED_SCALE
        self.dist_scale = DIST_SCALE

    def compute(self) -> dict:
        """Compute Tolvera parameter adjustments from audio.

        Returns dict with:
            boids_speed: float - target speed for Boids (from RMS)
            physarum_sense_dist: float - sense distance for Physarum (from centroid)
            branch_trigger: bool - whether to trigger Physarum branching (from flux)
        """
        features = self.analyzer.analyze()
        return {
            "boids_speed": features["rms"] * self.speed_scale,
            "physarum_sense_dist": features["spectral_centroid"] * self.dist_scale,
            "branch_trigger": features["spectral_flux"] > self.flux_threshold,
        }
