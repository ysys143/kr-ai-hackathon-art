import time
from src.config import (
    GHOST_DURATION,
    GHOST_PEAK_BRIGHTNESS,
    GHOST_IMMINENT_THRESHOLD,
    GHOST_IMMINENT_DURATION,
)


class GhostReplay:
    """Ghost Replay state machine.

    States: IDLE → IMMINENT → ACTIVE → IDLE

    IMMINENT triggers automatically after GHOST_IMMINENT_THRESHOLD touches.
    After GHOST_IMMINENT_DURATION seconds in IMMINENT, auto-triggers to ACTIVE.
    Presenter can press G at any time to jump to ACTIVE.

    ACTIVE: brightness pulse sequence
      - 0-3s: ramp up 1.0 → GHOST_PEAK_BRIGHTNESS (2.5)
      - 3-8s: hold at peak
      - 8-20s: ramp down to 1.0
    """

    def __init__(self) -> None:
        self.state: str = "IDLE"
        self.start_time: float = 0.0
        self.imminent_start_time: float = 0.0
        self.duration: float = GHOST_DURATION
        self.touch_count: int = 0
        self.touch_paths: list[tuple[int, int]] = []

    def record_touch(self, x: int, y: int, radius: int = 5) -> None:
        """Record touch position for evaporate_mask and track touch count."""
        self.touch_paths.append((x, y))
        self.touch_count += 1
        if self.touch_count >= GHOST_IMMINENT_THRESHOLD and self.state == "IDLE":
            self.state = "IMMINENT"
            self.imminent_start_time = time.time()

    def trigger(self) -> None:
        """Force transition to ACTIVE (G key or auto-trigger from IMMINENT)."""
        self.state = "ACTIVE"
        self.start_time = time.time()

    def tick(self) -> tuple[str, float | None]:
        """Update state machine. Returns (state, value).

        Returns:
            ("IDLE", None) - no effect
            ("IMMINENT", seconds_remaining) - countdown to auto-trigger
            ("ACTIVE", brightness_multiplier) - brightness pulse value
        """
        if self.state == "IDLE":
            return ("IDLE", None)

        if self.state == "IMMINENT":
            elapsed = time.time() - self.imminent_start_time
            if elapsed >= GHOST_IMMINENT_DURATION:
                self.trigger()
                return self.tick()  # recurse into ACTIVE
            remaining = GHOST_IMMINENT_DURATION - elapsed
            return ("IMMINENT", remaining)

        if self.state == "ACTIVE":
            elapsed = time.time() - self.start_time
            if elapsed >= self.duration:
                self.state = "IDLE"
                self.touch_count = 0
                return ("IDLE", None)

            # Brightness pulse: 3s rise, 5s hold, 12s fade
            if elapsed < 3.0:
                factor = elapsed / 3.0
            elif elapsed < 8.0:
                factor = 1.0
            else:
                factor = 1.0 - (elapsed - 8.0) / 12.0

            brightness = 1.0 + (GHOST_PEAK_BRIGHTNESS - 1.0) * max(0.0, factor)
            return ("ACTIVE", brightness)

        return ("IDLE", None)

    def reset(self) -> None:
        """Full reset: clear all state."""
        self.state = "IDLE"
        self.start_time = 0.0
        self.imminent_start_time = 0.0
        self.touch_count = 0
        self.touch_paths.clear()

    @property
    def has_paths(self) -> bool:
        return len(self.touch_paths) > 0
