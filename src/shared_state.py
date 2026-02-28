import queue
import threading
from dataclasses import dataclass, field


@dataclass
class SharedState:
    """Thread-safe state shared between main thread (GGUI) and async daemon thread."""

    # --- Main -> Async (written by main thread, read by async thread) ---
    boids_density: float = 0.5
    physarum_connectivity: float = 0.5
    agent_activity: float = 0.5
    latest_jpeg_frame: bytes = b""
    touch_events: queue.Queue = field(default_factory=queue.Queue)

    # Ghost state
    ghost_active: bool = False
    ghost_state: str = "IDLE"  # "IDLE", "IMMINENT", "ACTIVE"
    ghost_elapsed: float = 0.0

    # IML state
    iml_n_pairs: int = 0

    # --- Async -> Main (written by async thread, read by main thread) ---
    audio_queue: queue.Queue = field(default_factory=lambda: queue.Queue(maxsize=50))
    audio_rms: float = 0.0
    audio_spectral_centroid: float = 0.0
    audio_spectral_flux: float = 0.0
    gemini_action: queue.Queue = field(default_factory=queue.Queue)

    # Connection status
    lyria_connected: bool = False
    gemini_connected: bool = False

    # Lock for grouped non-atomic field updates
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def update_visual_metrics(
        self, density: float, connectivity: float, activity: float
    ) -> None:
        with self._lock:
            self.boids_density = density
            self.physarum_connectivity = connectivity
            self.agent_activity = activity

    def get_visual_metrics(self) -> tuple[float, float, float]:
        with self._lock:
            return self.boids_density, self.physarum_connectivity, self.agent_activity

    def update_audio_features(self, rms: float, centroid: float, flux: float) -> None:
        with self._lock:
            self.audio_rms = rms
            self.audio_spectral_centroid = centroid
            self.audio_spectral_flux = flux

    def get_audio_features(self) -> tuple[float, float, float]:
        with self._lock:
            return (
                self.audio_rms,
                self.audio_spectral_centroid,
                self.audio_spectral_flux,
            )

    def update_ghost_state(self, state: str, active: bool, elapsed: float) -> None:
        with self._lock:
            self.ghost_state = state
            self.ghost_active = active
            self.ghost_elapsed = elapsed

    def get_ghost_info(self) -> tuple[str, bool, float]:
        with self._lock:
            return self.ghost_state, self.ghost_active, self.ghost_elapsed
