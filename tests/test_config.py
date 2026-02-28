from src.config import (
    PARTICLES,
    EVAPORATE,
    SCREEN_W,
    SCREEN_H,
    COLORS,
    LYRIA_MODEL,
    GEMINI_MODEL,
    DEFAULT_DENSITY,
    DEFAULT_BRIGHTNESS,
    FEEDBACK_INTERVAL,
    GHOST_DURATION,
    GHOST_PEAK_BRIGHTNESS,
    IML_INTERVAL,
    IML_MAX_PAIRS,
    AUDIO_SAMPLE_RATE,
    AUDIO_BLOCK_SIZE,
)


def test_particles():
    assert PARTICLES == 4096


def test_evaporate():
    assert 0.9 <= EVAPORATE <= 1.0


def test_screen():
    assert SCREEN_W == 1920
    assert SCREEN_H == 1080


def test_colors():
    assert len(COLORS) == 4


def test_models():
    assert "lyria" in LYRIA_MODEL
    assert "gemini" in GEMINI_MODEL


def test_defaults():
    assert 0.0 <= DEFAULT_DENSITY <= 1.0
    assert 0.0 <= DEFAULT_BRIGHTNESS <= 1.0


def test_intervals():
    assert FEEDBACK_INTERVAL > 0
    assert IML_INTERVAL > 0


def test_ghost_constants():
    assert GHOST_DURATION > 0
    assert GHOST_PEAK_BRIGHTNESS > 1.0


def test_iml():
    assert IML_MAX_PAIRS > 0


def test_audio():
    assert AUDIO_SAMPLE_RATE == 48000
    assert AUDIO_BLOCK_SIZE > 0
