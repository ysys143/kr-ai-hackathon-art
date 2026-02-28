import io
import logging
import math
import time

import numpy as np
from PIL import Image

from src.config import (
    DIST_SCALE,
    FLUX_THRESHOLD,
    PARTICLES,
    SCREEN_H,
    SCREEN_W,
    SPEED_SCALE,
)

logger = logging.getLogger(__name__)


class TolveraEngine:
    """Wraps Tolvera for the Boids+Physarum visual simulation."""

    def __init__(self) -> None:
        from tolvera import Tolvera  # VERIFY: correct import path

        # VERIFY: Tolvera constructor signature — may accept name, x, y, fps, headless, etc.
        self.tv = Tolvera(x=SCREEN_W, y=SCREEN_H)  # VERIFY: exact kwargs

        # VERIFY: how to configure particle count — may be tv.n or a Species constructor arg
        # self.tv.n = PARTICLES

        # VERIFY: how to set background color — may be tv.ctx.background or tv.bg
        # self.tv.ctx.background = BG_COLOR

        # Cursor / interaction state
        self._prev_cursor: tuple[float, float] = (0.5, 0.5)
        self._cursor_velocity: float = 0.0
        self._press_start: float = 0.0
        self._is_pressed: bool = False
        self._frame_count: int = 0

        # Ghost Replay brightness multiplier (set externally from ghost state machine)
        self._brightness_mult: float = 1.0

        # Touch positions accumulated for Physarum nutrient deposit and ghost evaporate mask
        self._touch_positions: list[tuple[float, float]] = []

        # Timestamp of last frame for dt calculation
        self._last_frame_time: float = time.monotonic()

        logger.info(
            "TolveraEngine initialised (%dx%d, %d particles)",
            SCREEN_W,
            SCREEN_H,
            PARTICLES,
        )

    # ------------------------------------------------------------------
    # Core render loop
    # ------------------------------------------------------------------

    def render_frame(self) -> None:
        # VERIFY: exact Tolvera step API — may be tv.step(), tv.render(), tv.update(),
        #         or this is called automatically inside tv.run() and not needed separately.
        self.tv.step()  # VERIFY

        if self._brightness_mult != 1.0:
            self._apply_brightness(self._brightness_mult)

        self._frame_count += 1
        self._last_frame_time = time.monotonic()

    def _apply_brightness(self, mult: float) -> None:
        # VERIFY: how to access and mutate the pixel/trail buffer directly.
        # Approach below assumes tv.px is a Taichi field of shape (H, W, 4) with float32.
        try:
            pixels = self.tv.px  # VERIFY: attribute name
            # Taichi field — apply multiplier in kernel or via numpy round-trip
            arr = pixels.to_numpy()  # VERIFY: returns ndarray
            arr = np.clip(arr * mult, 0.0, 1.0)
            pixels.from_numpy(arr)  # VERIFY: write-back method
        except Exception:
            logger.debug(
                "_apply_brightness: pixel buffer access failed — skipping",
                exc_info=True,
            )

    # ------------------------------------------------------------------
    # Visual metrics
    # ------------------------------------------------------------------

    def get_boids_density(self) -> float:
        """Boids clustering metric, 0 (dispersed) → 1 (clustered)."""
        try:
            # VERIFY: how to access boids particle positions —
            #   may be tv.s.boids.field, tv.species[0].pos, tv.boids.pos, etc.
            pos_field = self.tv.s.boids.field  # VERIFY
            positions = pos_field.to_numpy()  # VERIFY: shape (N, 2) float32 in [0,1]

            if positions.shape[0] < 2:
                return 0.5

            # Average distance of each particle to the swarm centroid (cheap proxy for density)
            centroid = positions.mean(axis=0)
            dists = np.linalg.norm(positions - centroid, axis=1)
            avg_dist = float(dists.mean())

            # max possible distance on a unit square is sqrt(2)/2 ≈ 0.707
            density = 1.0 - min(avg_dist / 0.707, 1.0)
            return float(np.clip(density, 0.0, 1.0))
        except Exception:
            logger.debug("get_boids_density: fallback to 0.5", exc_info=True)
            return 0.5

    def get_physarum_connectivity(self) -> float:
        """Physarum trail network density, 0 (sparse) → 1 (dense)."""
        try:
            # VERIFY: how to access the Physarum trail/pheromone buffer —
            #   may be tv.s.slime, tv.trail, tv.physarum.trail, tv.px, etc.
            trail = self.tv.s.slime  # VERIFY
            arr = trail.to_numpy()  # VERIFY: shape (H, W) or (H, W, C) float32

            if arr.ndim == 3:
                brightness = arr.mean(axis=2)  # flatten channels
            else:
                brightness = arr

            # Fraction of pixels above a low threshold indicates network density
            active_fraction = float((brightness > 0.05).mean())
            return float(np.clip(active_fraction, 0.0, 1.0))
        except Exception:
            logger.debug("get_physarum_connectivity: fallback to 0.5", exc_info=True)
            return 0.5

    def get_agent_activity(self) -> float:
        """Combined activity metric: mean of boids density and physarum connectivity."""
        return (self.get_boids_density() + self.get_physarum_connectivity()) / 2.0

    # ------------------------------------------------------------------
    # Frame capture for Gemini
    # ------------------------------------------------------------------

    def capture_frame_jpeg(self) -> bytes:
        pixels = (
            self.tv.px.to_numpy()
        )  # VERIFY: returns float32 RGBA or RGB, shape (H, W, C)
        img_array = (np.clip(pixels, 0.0, 1.0) * 255).astype(np.uint8)

        # Drop alpha channel if present
        if img_array.ndim == 3 and img_array.shape[2] == 4:
            img_array = img_array[:, :, :3]

        img = Image.fromarray(img_array)
        img = img.resize((480, 270), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=60)
        return buf.getvalue()

    # ------------------------------------------------------------------
    # Window accessor
    # ------------------------------------------------------------------

    def get_window(self):
        return self.tv.ctx.window  # VERIFY: exact accessor — may be tv.window or tv.gui

    # ------------------------------------------------------------------
    # Touch / cursor interaction
    # ------------------------------------------------------------------

    def on_touch(self, x: float, y: float) -> None:
        """x, y are normalised (0-1) from GGUI cursor position."""
        self._touch_positions.append((x, y))

        # VERIFY: Tolvera API for applying an attraction force to nearby Boids.
        # Possible approaches:
        #   tv.s.boids.attract(x, y, radius=0.1, strength=0.5)
        #   tv.boids.apply_force(x, y, ...)
        #   Directly mutate boid velocity fields via Taichi kernel
        try:
            self.tv.s.boids.attract(x, y, radius=0.1, strength=0.5)  # VERIFY
        except Exception:
            logger.debug("on_touch: boids attract not available — skipping")

        # VERIFY: Physarum nutrient deposit at cursor position.
        # Possible approaches:
        #   tv.s.slime.deposit(x, y, amount=1.0, radius=0.05)
        #   tv.physarum.add_nutrient(x, y, ...)
        try:
            self.tv.s.slime.deposit(x, y, amount=1.0, radius=0.05)  # VERIFY
        except Exception:
            logger.debug("on_touch: slime deposit not available — skipping")

    def get_touch_vec(self) -> list[float]:
        """Return [x_norm, y_norm, velocity, dwell] for IML input."""
        x, y = self._prev_cursor
        return [x, y, self._cursor_velocity, self.get_dwell()]

    def get_cursor_velocity(self) -> float:
        return self._cursor_velocity

    def get_dwell(self) -> float:
        """Seconds held normalised to [0, 1] where 1.0 = 5 seconds."""
        if not self._is_pressed:
            return 0.0
        elapsed = time.monotonic() - self._press_start
        return min(elapsed / 5.0, 1.0)

    def update_cursor(self, x: float, y: float, pressed: bool) -> None:
        px, py = self._prev_cursor
        dx = x - px
        dy = y - py
        dist = math.sqrt(dx * dx + dy * dy)

        # Approximate dt from frame counter; use small fallback to avoid divide-by-zero
        now = time.monotonic()
        dt = now - self._last_frame_time
        if dt < 1e-6:
            dt = 1e-6

        self._cursor_velocity = dist / dt

        if pressed and not self._is_pressed:
            self._press_start = now
        self._is_pressed = pressed

        self._prev_cursor = (x, y)

    # ------------------------------------------------------------------
    # Brightness (Ghost Replay integration)
    # ------------------------------------------------------------------

    def set_brightness_multiplier(self, mult: float) -> None:
        self._brightness_mult = mult

    # ------------------------------------------------------------------
    # Audio feedback
    # ------------------------------------------------------------------

    def apply_audio_feedback(self, features: dict) -> None:
        rms: float = features.get("rms", 0.0)
        centroid: float = features.get("spectral_centroid", 0.0)
        flux: float = features.get("spectral_flux", 0.0)

        target_speed = rms * SPEED_SCALE
        # VERIFY: how to set boids speed — may be tv.s.boids.max_speed, tv.boids.speed, etc.
        try:
            self.tv.s.boids.max_speed = target_speed  # VERIFY
        except Exception:
            logger.debug("apply_audio_feedback: cannot set boids speed")

        sense = centroid * DIST_SCALE
        # VERIFY: how to set physarum sense_dist — may be tv.s.physarum.sense_dist, tv.physarum.p.sense_dist, etc.
        try:
            self.tv.s.physarum.sense_dist = sense  # VERIFY
        except Exception:
            logger.debug("apply_audio_feedback: cannot set physarum sense_dist")

        if flux > FLUX_THRESHOLD:
            # VERIFY: how to trigger Physarum branching — may be a method, a flag, or a parameter nudge.
            try:
                self.tv.s.physarum.branch()  # VERIFY
            except Exception:
                logger.debug("apply_audio_feedback: physarum branch() not available")

    # ------------------------------------------------------------------
    # IML parameter setters
    # ------------------------------------------------------------------

    def set_boids_params(
        self, separation: float, alignment: float, cohesion: float
    ) -> None:
        # VERIFY: exact Tolvera API for setting boids steering weights.
        # Possible approaches:
        #   tv.s.boids.separation = separation
        #   tv.boids.p.separation = separation
        #   tv.species[0].separation = separation
        try:
            self.tv.s.boids.separation = separation  # VERIFY
            self.tv.s.boids.alignment = alignment  # VERIFY
            self.tv.s.boids.cohesion = cohesion  # VERIFY
        except Exception:
            logger.debug("set_boids_params: setter not available — using defaults")

    def set_physarum_params(
        self, sense_angle: float, sense_dist: float, move_dist: float
    ) -> None:
        # VERIFY: exact Tolvera API for setting physarum parameters.
        # Possible approaches:
        #   tv.s.physarum.sense_angle = sense_angle
        #   tv.physarum.p.sense_angle = sense_angle
        try:
            self.tv.s.physarum.sense_angle = sense_angle  # VERIFY
            self.tv.s.physarum.sense_dist = sense_dist  # VERIFY
            self.tv.s.physarum.move_dist = move_dist  # VERIFY
        except Exception:
            logger.debug("set_physarum_params: setter not available — using defaults")

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self) -> None:
        # VERIFY: Tolvera reset API — may be tv.reset(), tv.randomise(), tv.init(), etc.
        try:
            self.tv.reset()  # VERIFY
        except Exception:
            logger.debug("reset: tv.reset() not available — skipping Tolvera reset")

        self._touch_positions.clear()
        self._brightness_mult = 1.0
        self._cursor_velocity = 0.0
        self._is_pressed = False
        self._frame_count = 0
        logger.info("TolveraEngine reset")
