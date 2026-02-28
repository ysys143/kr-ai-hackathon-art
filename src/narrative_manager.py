import time
import threading
from dataclasses import dataclass


@dataclass
class TouchEvent:
    x: float
    y: float
    t: float
    velocity: float


@dataclass
class SessionState:
    n_pairs: int = 0
    touch_freq: float = 0.0
    avg_speed: float = 0.0
    linearity: float = 0.0
    circularity: float = 0.0
    dominant_region: str = "none"
    pattern_type: str = "none"
    bpm: int = 72
    texture: str = "ambient sparse"


class SessionNarrativeManager:
    """Generates session narrative for Gemini's {{SESSION_CONTEXT}} placeholder."""

    def __init__(self) -> None:
        self._cache: str = self._initial_narrative()
        self._lock = threading.Lock()
        self._touch_history: list[TouchEvent] = []
        self._session_start: float = time.time()

    def get(self, ghost_state: str = "IDLE", ghost_value: float | None = None) -> str:
        """Get current narrative with optional ghost overlay."""
        overlay = self._ghost_overlay(ghost_state, ghost_value)
        with self._lock:
            if overlay:
                return overlay + "\n" + self._cache
            return self._cache

    def update(self, n_pairs: int = 0) -> None:
        """Recompute narrative from touch history. Called every 30 seconds."""
        state = self._compute_state(n_pairs)
        narrative = self._template_narrative(state)
        with self._lock:
            self._cache = narrative

    def record_touch(self, x: float, y: float, t: float, velocity: float) -> None:
        """Record a touch event for statistics."""
        self._touch_history.append(TouchEvent(x=x, y=y, t=t, velocity=velocity))
        # Keep only last 5 minutes of history
        cutoff = time.time() - 300
        self._touch_history = [e for e in self._touch_history if e.t > cutoff]

    def reset(self) -> None:
        """Clear all history, reset to initial narrative."""
        self._touch_history.clear()
        self._session_start = time.time()
        with self._lock:
            self._cache = self._initial_narrative()

    def _compute_state(self, n_pairs: int) -> SessionState:
        state = SessionState(n_pairs=n_pairs)
        if not self._touch_history:
            return state

        elapsed_min = max((time.time() - self._session_start) / 60.0, 0.01)
        state.touch_freq = len(self._touch_history) / elapsed_min

        speeds = [e.velocity for e in self._touch_history]
        state.avg_speed = sum(speeds) / len(speeds) if speeds else 0.0

        # Dominant region (divide screen into quadrants)
        xs = [e.x for e in self._touch_history]
        ys = [e.y for e in self._touch_history]
        avg_x = sum(xs) / len(xs)
        avg_y = sum(ys) / len(ys)
        if avg_x < 0.33:
            region_x = "left"
        elif avg_x > 0.66:
            region_x = "right"
        else:
            region_x = "center"
        if avg_y < 0.33:
            region_y = "lower"
        elif avg_y > 0.66:
            region_y = "upper"
        else:
            region_y = "center"
        state.dominant_region = (
            f"{region_y}-{region_x}"
            if region_y != "center" or region_x != "center"
            else "center"
        )

        # Circularity: detect circular patterns from position variance
        if len(self._touch_history) >= 5:
            dx = [
                self._touch_history[i + 1].x - self._touch_history[i].x
                for i in range(len(self._touch_history) - 1)
            ]
            dy = [
                self._touch_history[i + 1].y - self._touch_history[i].y
                for i in range(len(self._touch_history) - 1)
            ]
            if dx and dy:
                import numpy as np

                angles = np.arctan2(dy, dx)
                angle_diffs = np.diff(angles)
                state.circularity = float(min(abs(np.mean(angle_diffs)) * 2.0, 1.0))
                state.linearity = 1.0 - state.circularity

        # Pattern type
        if state.circularity > 0.5:
            state.pattern_type = "circular"
        elif state.linearity > 0.6:
            state.pattern_type = "linear"
        elif len(self._touch_history) > 10:
            state.pattern_type = "radial"
        else:
            state.pattern_type = "none"

        # Texture based on adaptation
        if n_pairs < 5:
            state.texture = "ambient sparse"
        elif n_pairs < 20:
            state.texture = "building texture"
        else:
            state.texture = "layered harmonic motion"

        return state

    def _template_narrative(self, state: SessionState) -> str:
        adaptation = self._adaptation_tag(state.n_pairs)
        personality = self._personality_tag(state)
        return (
            f"[VISITOR PROFILE] {adaptation} organism"
            f" — {personality}, freq={state.touch_freq:.1f}/min\n"
            f"[ORGANISM STATE] Adaptation: {state.n_pairs}/50 pairs"
            f" | Region: {state.dominant_region} | Pattern: {state.pattern_type}\n"
            f"[MUSIC CUE] {state.texture}"
            f" — {state.bpm}bpm, {self._instruments(state)}"
        )

    def _adaptation_tag(self, n_pairs: int) -> str:
        if n_pairs < 5:
            return "virgin"
        if n_pairs < 15:
            return "awakening"
        if n_pairs < 30:
            return "learning"
        return "evolved"

    def _personality_tag(self, state: SessionState) -> str:
        if state.avg_speed > 0.7 and state.linearity > 0.6:
            return "driven explorer"
        if state.avg_speed < 0.3 and state.circularity > 0.5:
            return "meditative wanderer"
        return "restless seeker"

    def _instruments(self, state: SessionState) -> str:
        if state.n_pairs < 5:
            return "open space, anticipation, no rhythm"
        if state.n_pairs < 20:
            return "sparse piano, building texture"
        return "layered strings, circular harmonic motion"

    def _ghost_overlay(self, ghost_state: str, ghost_value: float | None) -> str:
        if ghost_state == "ACTIVE" and ghost_value is not None:
            remaining = max(0, ghost_value)
            return (
                f"[GHOST REPLAY ACTIVE] Echo dissolving in {remaining:.0f}s\n"
                f"[MUSIC CUE] Ghost melody over present rhythm, fade over {remaining:.0f}s"
            )
        if ghost_state == "IMMINENT" and ghost_value is not None:
            return (
                f"[GHOST REPLAY IMMINENT] Memory surfacing in {ghost_value:.0f}s\n"
                f"[MUSIC CUE] Liminal — prepare echo texture, suspend rhythm"
            )
        return ""

    def _initial_narrative(self) -> str:
        return (
            "[VISITOR PROFILE] virgin organism — awaiting first contact\n"
            "[ORGANISM STATE] Adaptation: 0/50 | Region: none | Pattern: none\n"
            "[MUSIC CUE] Ambient sparse — open space, anticipation, no rhythm"
        )
