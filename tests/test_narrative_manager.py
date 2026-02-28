import time
from src.narrative_manager import SessionNarrativeManager


def test_initial_narrative():
    m = SessionNarrativeManager()
    result = m.get()
    assert "virgin" in result
    assert "VISITOR PROFILE" in result


def test_ghost_overlay_active():
    m = SessionNarrativeManager()
    result = m.get(ghost_state="ACTIVE", ghost_value=15.0)
    assert "GHOST REPLAY ACTIVE" in result


def test_ghost_overlay_imminent():
    m = SessionNarrativeManager()
    result = m.get(ghost_state="IMMINENT", ghost_value=5.0)
    assert "GHOST REPLAY IMMINENT" in result


def test_ghost_overlay_idle_unchanged():
    m = SessionNarrativeManager()
    result_idle = m.get(ghost_state="IDLE", ghost_value=None)
    result_no_args = m.get()
    assert result_idle == result_no_args


def test_record_touch():
    m = SessionNarrativeManager()
    m.record_touch(0.5, 0.5, time.time(), 0.3)
    m.update(n_pairs=3)
    result = m.get()
    assert "VISITOR PROFILE" in result


def test_adaptation_tag_progression():
    m = SessionNarrativeManager()

    m.update(n_pairs=0)
    assert "virgin" in m.get()

    m.update(n_pairs=10)
    assert "awakening" in m.get()

    m.update(n_pairs=20)
    assert "learning" in m.get()

    m.update(n_pairs=35)
    assert "evolved" in m.get()


def test_reset():
    m = SessionNarrativeManager()
    m.record_touch(0.5, 0.5, time.time(), 0.5)
    m.update(n_pairs=10)
    m.reset()
    result = m.get()
    assert "virgin" in result


def test_reset_clears_touch_history():
    m = SessionNarrativeManager()
    for i in range(5):
        m.record_touch(float(i) / 10, float(i) / 10, time.time(), 0.3)
    m.reset()
    # After reset, update with n_pairs=0 should still show virgin
    m.update(n_pairs=0)
    assert "virgin" in m.get()


def test_organism_state_in_narrative():
    m = SessionNarrativeManager()
    m.update(n_pairs=5)
    result = m.get()
    assert "ORGANISM STATE" in result


def test_music_cue_in_narrative():
    m = SessionNarrativeManager()
    result = m.get()
    assert "MUSIC CUE" in result


def test_adaptation_boundary_awakening():
    m = SessionNarrativeManager()
    m.update(n_pairs=5)
    assert "awakening" in m.get()


def test_adaptation_boundary_learning():
    m = SessionNarrativeManager()
    m.update(n_pairs=15)
    assert "learning" in m.get()


def test_adaptation_boundary_evolved():
    m = SessionNarrativeManager()
    m.update(n_pairs=30)
    assert "evolved" in m.get()
