import threading
from src.shared_state import SharedState


def test_create():
    s = SharedState()
    assert s.boids_density == 0.5


def test_update_visual_metrics():
    s = SharedState()
    s.update_visual_metrics(0.8, 0.3, 0.6)
    d, c, a = s.get_visual_metrics()
    assert d == 0.8
    assert c == 0.3
    assert a == 0.6


def test_update_audio_features():
    s = SharedState()
    s.update_audio_features(0.5, 0.7, 0.2)
    r, c, f = s.get_audio_features()
    assert r == 0.5
    assert c == 0.7
    assert f == 0.2


def test_ghost_state():
    s = SharedState()
    s.update_ghost_state("ACTIVE", True, 5.0)
    state, active, elapsed = s.get_ghost_info()
    assert state == "ACTIVE"
    assert active is True
    assert elapsed == 5.0


def test_thread_safety():
    s = SharedState()
    errors = []

    def writer():
        for i in range(100):
            s.update_visual_metrics(i / 100, i / 100, i / 100)

    def reader():
        for _ in range(100):
            try:
                s.get_visual_metrics()
            except Exception as e:
                errors.append(e)

    threads = [threading.Thread(target=writer), threading.Thread(target=reader)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(errors) == 0


def test_queues():
    s = SharedState()
    s.touch_events.put((0.5, 0.5, 0.1, 0.2))
    event = s.touch_events.get()
    assert event == (0.5, 0.5, 0.1, 0.2)


def test_default_ghost_state():
    s = SharedState()
    state, active, elapsed = s.get_ghost_info()
    assert state == "IDLE"
    assert active is False
    assert elapsed == 0.0


def test_visual_metrics_multiple_updates():
    s = SharedState()
    s.update_visual_metrics(0.1, 0.2, 0.3)
    s.update_visual_metrics(0.9, 0.8, 0.7)
    d, c, a = s.get_visual_metrics()
    assert d == 0.9
    assert c == 0.8
    assert a == 0.7
