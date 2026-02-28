import numpy as np
from src.audio_analyzer import AudioAnalyzer, AudioFeedback


def test_create():
    a = AudioAnalyzer()
    features = a.analyze()
    assert "rms" in features
    assert "spectral_centroid" in features
    assert "spectral_flux" in features


def test_feed_and_analyze():
    a = AudioAnalyzer()
    # Feed a sine wave (stereo interleaved, 16-bit signed)
    t = np.linspace(0, 1, 48000, dtype=np.float32)
    mono = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    # Interleave as stereo: L=mono, R=mono
    stereo = np.empty(len(mono) * 2, dtype=np.int16)
    stereo[0::2] = mono
    stereo[1::2] = mono
    a.feed(stereo.tobytes())
    features = a.analyze()
    assert features["rms"] > 0


def test_silence():
    a = AudioAnalyzer()
    # Stereo silence: 4800 frames * 2 channels
    silence = np.zeros(4800 * 2, dtype=np.int16).tobytes()
    a.feed(silence)
    features = a.analyze()
    assert features["rms"] == 0.0 or features["rms"] < 0.01


def test_rms_range():
    a = AudioAnalyzer()
    # Stereo noise
    noise = (np.random.randn(4800 * 2) * 10000).astype(np.int16).tobytes()
    a.feed(noise)
    features = a.analyze()
    assert 0.0 <= features["rms"] <= 1.0


def test_spectral_centroid_range():
    a = AudioAnalyzer()
    t = np.linspace(0, 1, 48000, dtype=np.float32)
    mono = (np.sin(2 * np.pi * 1000 * t) * 32767).astype(np.int16)
    stereo = np.empty(len(mono) * 2, dtype=np.int16)
    stereo[0::2] = mono
    stereo[1::2] = mono
    a.feed(stereo.tobytes())
    features = a.analyze()
    assert 0.0 <= features["spectral_centroid"] <= 1.0


def test_spectral_flux_range():
    a = AudioAnalyzer()
    noise = (np.random.randn(4800 * 2) * 10000).astype(np.int16).tobytes()
    a.feed(noise)
    # First analyze sets prev_spectrum
    a.analyze()
    a.feed(noise)
    features = a.analyze()
    assert 0.0 <= features["spectral_flux"] <= 1.0


def test_audio_feedback_compute():
    a = AudioAnalyzer()
    fb = AudioFeedback(a)
    result = fb.compute()
    assert "boids_speed" in result
    assert "physarum_sense_dist" in result
    assert "branch_trigger" in result


def test_audio_feedback_branch_trigger_type():
    a = AudioAnalyzer()
    fb = AudioFeedback(a)
    result = fb.compute()
    assert isinstance(result["branch_trigger"], (bool, np.bool_))


def test_empty_buffer_centroid():
    # Fresh analyzer with all-zero buffer returns 0.0 centroid
    a = AudioAnalyzer()
    assert a.get_spectral_centroid() == 0.0


def test_empty_buffer_rms():
    a = AudioAnalyzer()
    assert a.get_rms() == 0.0
