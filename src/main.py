import argparse
import asyncio
import logging
import threading
import time

import taichi as ti

from src.config import SCREEN_W, SCREEN_H, GHOST_DURATION, GHOST_IMMINENT_DURATION
from src.shared_state import SharedState
from src.tolvera_engine import TolveraEngine
from src.lyria_client import LyriaClient
from src.gemini_client import GeminiClient
from src.audio_bridge import AudioBridge
from src.audio_analyzer import AudioAnalyzer
from src.feedback_loop import FeedbackLoop
from src.ghost_replay import GhostReplay
from src.iml_manager import IMLManager
from src.narrative_manager import SessionNarrativeManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Self-Evolution Interactive Art")
    parser.add_argument("--no-lyria", action="store_true", help="Run without Lyria")
    parser.add_argument("--no-gemini", action="store_true", help="Run without Gemini")
    parser.add_argument("--smoke-test", action="store_true", help="Run 10s then exit")
    return parser.parse_args()


async def _start_async_subsystems(
    loop, shared, lyria, gemini, feedback, narrative, args
):
    """Initialize and start all async subsystems."""
    if not args.no_lyria:
        try:
            await lyria.connect()
            asyncio.ensure_future(lyria.receive_audio())
            asyncio.ensure_future(lyria.reconnect_watchdog())
            logger.info("Lyria subsystem started")
        except Exception as e:
            logger.error(f"Lyria failed to start: {e}")

    asyncio.ensure_future(feedback.run())
    asyncio.ensure_future(feedback.run_narrative_updater())

    if not args.no_gemini:
        try:
            await feedback.start_gemini()
            logger.info("Gemini subsystem started")
        except Exception as e:
            logger.error(f"Gemini failed to start: {e}")


def main():
    args = parse_args()

    # 1. Initialize shared state
    shared = SharedState()

    # 2. Initialize Tolvera (MUST be on main thread for macOS GGUI)
    engine = TolveraEngine()
    ghost = GhostReplay()
    iml = IMLManager(engine)
    analyzer = AudioAnalyzer()
    narrative = SessionNarrativeManager()

    # 3. Create async event loop in daemon thread
    loop = asyncio.new_event_loop()

    def run_async_loop():
        asyncio.set_event_loop(loop)
        loop.run_forever()

    async_thread = threading.Thread(target=run_async_loop, daemon=True)
    async_thread.start()

    # 4. Create async clients
    lyria = LyriaClient(shared)
    gemini = GeminiClient(shared)
    feedback = FeedbackLoop(shared, lyria, gemini, narrative)

    # 5. Start audio bridge
    audio_bridge = None
    if not args.no_lyria:
        try:
            audio_bridge = AudioBridge(shared)
            audio_bridge.start()
        except Exception as e:
            logger.warning(f"AudioBridge failed to start: {e}")

    # 6. Schedule async subsystem initialization
    asyncio.run_coroutine_threadsafe(
        _start_async_subsystems(loop, shared, lyria, gemini, feedback, narrative, args),
        loop,
    )

    # 7. Main thread: GGUI render loop
    window = engine.get_window()
    start_time = time.monotonic()
    frame_skip_counter = 0

    try:
        while window.running:
            # Smoke test: exit after 10 seconds
            if args.smoke_test and (time.monotonic() - start_time) > 10:
                logger.info("Smoke test complete — exiting")
                break

            # Handle keyboard
            try:
                if window.get_event(ti.GUI.PRESS):
                    key = window.event.key
                    if key == "g":
                        ghost.trigger()
                        asyncio.run_coroutine_threadsafe(
                            lyria.set_params(mute_drums=False), loop
                        )
                        logger.info("Ghost Replay triggered (G key)")
                    elif key == "r":
                        ghost.reset()
                        engine.reset()
                        iml.clear()
                        narrative.reset()
                        asyncio.run_coroutine_threadsafe(lyria._reconnect(), loop)
                        logger.info("Full reset (R key)")
                    elif key == ti.GUI.ESCAPE:
                        break
            except Exception:
                pass  # GGUI event API may differ

            # Handle mouse
            try:
                cx, cy = window.get_cursor_pos()
                pressed = window.is_pressed(ti.GUI.LMB)
                engine.update_cursor(cx, cy, pressed)

                if pressed:
                    engine.on_touch(cx, cy)
                    ghost.record_touch(int(cx * SCREEN_W), int(cy * SCREEN_H))
                    touch_vec = engine.get_touch_vec()
                    iml.update(touch_vec)
                    iml.apply(engine)
                    narrative.record_touch(
                        cx, cy, time.time(), engine.get_cursor_velocity()
                    )
                    shared.touch_events.put_nowait(
                        (cx, cy, engine.get_cursor_velocity(), engine.get_dwell())
                    )
            except Exception:
                pass  # GGUI mouse API may differ

            # Update visual metrics in shared state
            shared.update_visual_metrics(
                engine.get_boids_density(),
                engine.get_physarum_connectivity(),
                engine.get_agent_activity(),
            )

            # Capture frame for Gemini (every 4th frame to reduce overhead)
            frame_skip_counter += 1
            if frame_skip_counter >= 4:
                frame_skip_counter = 0
                try:
                    shared.latest_jpeg_frame = engine.capture_frame_jpeg()
                except Exception:
                    pass

            # Apply audio feedback from Lyria
            try:
                audio_chunk = lyria.get_latest_audio_chunk()
                if audio_chunk:
                    analyzer.feed(audio_chunk)
                    features = analyzer.analyze()
                    engine.apply_audio_feedback(features)
                    shared.update_audio_features(
                        features["rms"],
                        features["spectral_centroid"],
                        features["spectral_flux"],
                    )
            except Exception:
                pass

            # Update ghost state — call tick() ONCE and store result
            ghost_state, ghost_value = ghost.tick()
            # For narrative: pass remaining time (GHOST_DURATION - elapsed), not brightness
            ghost_elapsed = 0.0
            if ghost_state == "ACTIVE" and hasattr(ghost, "start_time"):
                ghost_elapsed = max(
                    0, GHOST_DURATION - (time.time() - ghost.start_time)
                )
            elif ghost_state == "IMMINENT" and hasattr(ghost, "imminent_start_time"):
                ghost_elapsed = max(
                    0,
                    GHOST_IMMINENT_DURATION - (time.time() - ghost.imminent_start_time),
                )
            shared.update_ghost_state(
                ghost_state,
                ghost_state == "ACTIVE",
                ghost_elapsed,
            )
            shared.iml_n_pairs = iml.get_n_pairs()

            if ghost_state == "ACTIVE" and ghost_value is not None:
                engine.set_brightness_multiplier(ghost_value)
            elif ghost_state == "IMMINENT":
                asyncio.run_coroutine_threadsafe(
                    lyria.set_params(mute_drums=True), loop
                )
            else:
                engine.set_brightness_multiplier(1.0)

            # Render frame
            engine.render_frame()
            window.show()

    except KeyboardInterrupt:
        logger.info("Interrupted by user")

    # 8. Cleanup
    logger.info("Shutting down...")
    if audio_bridge:
        audio_bridge.stop()
    asyncio.run_coroutine_threadsafe(lyria.close(), loop)
    asyncio.run_coroutine_threadsafe(gemini.close(), loop)
    loop.call_soon_threadsafe(loop.stop)
    async_thread.join(timeout=5)
    logger.info("Shutdown complete")


if __name__ == "__main__":
    main()
