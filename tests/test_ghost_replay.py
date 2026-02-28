import time
from src.ghost_replay import GhostReplay
from src.config import GHOST_IMMINENT_THRESHOLD


def test_initial_state():
    g = GhostReplay()
    state, value = g.tick()
    assert state == "IDLE"
    assert value is None


def test_trigger():
    g = GhostReplay()
    g.trigger()
    state, value = g.tick()
    assert state == "ACTIVE"
    assert value is not None


def test_imminent_transition():
    g = GhostReplay()
    # Record exactly GHOST_IMMINENT_THRESHOLD touches to trigger IMMINENT
    for i in range(GHOST_IMMINENT_THRESHOLD):
        g.record_touch(100 + i, 100)
    state, value = g.tick()
    assert state == "IMMINENT"


def test_imminent_returns_countdown():
    g = GhostReplay()
    for i in range(GHOST_IMMINENT_THRESHOLD):
        g.record_touch(100 + i, 100)
    state, value = g.tick()
    assert state == "IMMINENT"
    assert value is not None
    assert value > 0


def test_reset():
    g = GhostReplay()
    g.trigger()
    g.reset()
    state, value = g.tick()
    assert state == "IDLE"
    assert value is None


def test_reset_clears_touch_count():
    g = GhostReplay()
    for i in range(GHOST_IMMINENT_THRESHOLD):
        g.record_touch(i, i)
    g.reset()
    assert g.touch_count == 0
    assert g.state == "IDLE"


def test_brightness_ramp():
    g = GhostReplay()
    g.trigger()
    # Immediately after trigger, elapsed ~= 0, factor = 0/3 = 0, brightness = 1.0
    state, value = g.tick()
    assert state == "ACTIVE"
    assert value >= 1.0


def test_brightness_below_peak_at_start():
    g = GhostReplay()
    g.trigger()
    state, value = g.tick()
    assert state == "ACTIVE"
    from src.config import GHOST_PEAK_BRIGHTNESS

    assert value <= GHOST_PEAK_BRIGHTNESS


def test_active_expires_after_duration():
    g = GhostReplay()
    g.trigger()
    # Manually backdate start_time past duration
    g.start_time = time.time() - g.duration - 1.0
    state, value = g.tick()
    assert state == "IDLE"
    assert value is None


def test_has_paths():
    g = GhostReplay()
    assert g.has_paths is False
    g.record_touch(10, 20)
    assert g.has_paths is True


def test_record_touch_increments_count():
    g = GhostReplay()
    g.record_touch(50, 50)
    assert g.touch_count == 1
