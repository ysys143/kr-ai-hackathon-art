import time
import logging

from src.config import IML_INTERVAL, IML_DELTA_THRESHOLD, IML_MAX_PAIRS

logger = logging.getLogger(__name__)


def _l2_distance(a: list[float], b: list[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


class IMLManager:
    def __init__(self, tolvera_engine):
        self.tv = tolvera_engine.tv
        self._last_add_time: float = 0.0
        self._last_touch_vec: list[float] | None = None
        self._n_pairs: int = 0
        self._interpolation: str = "Ripple"

        try:
            # VERIFY: Tolvera IML API — exact syntax may differ
            # touch2boids: 4D input (x, y, velocity, dwell) → 3D output (separation, alignment, cohesion)
            self.tv.iml.map("touch2boids", size=(4, 3), randomise=True, lag=0.4)
            # touch2physarum: 4D input → 3D output (sense_angle, sense_dist, move_dist)
            self.tv.iml.map("touch2physarum", size=(4, 3), randomise=True, lag=0.5)
            logger.info("IML mappings created: touch2boids, touch2physarum")
        except Exception as e:
            logger.warning(f"IML setup failed (expected if Tolvera API differs): {e}")

    def update(self, touch_vec: list[float]):
        # Check interval
        if time.monotonic() - self._last_add_time < IML_INTERVAL:
            return

        # Check delta
        if self._last_touch_vec is not None:
            if _l2_distance(touch_vec, self._last_touch_vec) < IML_DELTA_THRESHOLD:
                return

        try:
            # VERIFY: exact Tolvera IML API for adding training pairs
            self.tv.iml.add("touch2boids", input=touch_vec)
            self.tv.iml.add("touch2physarum", input=touch_vec)
            self._n_pairs += 1
            self._last_add_time = time.monotonic()
            self._last_touch_vec = touch_vec[:]

            # Sliding window: remove oldest pairs when exceeding max
            if self._n_pairs > IML_MAX_PAIRS:
                self.tv.iml.remove_oldest("touch2boids", count=5)  # VERIFY
                self.tv.iml.remove_oldest("touch2physarum", count=5)  # VERIFY
                self._n_pairs -= 5

            # Switch interpolation strategy at 20 pairs
            if self._n_pairs >= 20 and self._interpolation == "Ripple":
                self._interpolation = "Softmax"
                self.tv.iml.set_interpolation("touch2boids", "Softmax")  # VERIFY
                self.tv.iml.set_interpolation("touch2physarum", "Softmax")  # VERIFY
                logger.info(
                    "IML interpolation switched to Softmax at %d pairs", self._n_pairs
                )

        except Exception as e:
            logger.debug(f"IML update failed: {e}")

    def apply(self, tolvera_engine):
        try:
            # VERIFY: how to read IML output
            boids_out = self.tv.iml.get(
                "touch2boids"
            )  # VERIFY: returns [separation, alignment, cohesion]?
            if boids_out is not None:
                tolvera_engine.set_boids_params(*boids_out[:3])

            physarum_out = self.tv.iml.get("touch2physarum")  # VERIFY
            if physarum_out is not None:
                tolvera_engine.set_physarum_params(*physarum_out[:3])
        except Exception as e:
            logger.debug(f"IML apply failed: {e}")

    def get_n_pairs(self) -> int:
        return self._n_pairs

    def clear(self):
        try:
            self.tv.iml.clear("touch2boids")  # VERIFY
            self.tv.iml.clear("touch2physarum")  # VERIFY
        except Exception:
            pass
        self._n_pairs = 0
        self._last_touch_vec = None
        self._interpolation = "Ripple"
        logger.info("IML cleared")
