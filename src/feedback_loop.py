import asyncio
import logging
import queue

from src.config import (
    DEFAULT_DENSITY,
    DEFAULT_BRIGHTNESS,
    FEEDBACK_INTERVAL,
    FEEDBACK_GAIN,
    FEEDBACK_MAX_DELTA,
)
from src.shared_state import SharedState
from src.prompts import get_system_prompt

logger = logging.getLogger(__name__)


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


class FeedbackLoop:
    def __init__(self, shared_state: SharedState, lyria, gemini, narrative):
        self.shared_state = shared_state
        self.lyria = lyria
        self.gemini = gemini
        self.narrative = narrative
        self._current_density = DEFAULT_DENSITY
        self._current_brightness = DEFAULT_BRIGHTNESS

    async def update_lyria_from_tolvera(self):
        boids_density, physarum_conn, _ = self.shared_state.get_visual_metrics()

        raw_density = self._current_density + (boids_density - 0.5) * FEEDBACK_GAIN
        delta_density = _clamp(
            raw_density - self._current_density, -FEEDBACK_MAX_DELTA, FEEDBACK_MAX_DELTA
        )
        new_density = _clamp(self._current_density + delta_density)

        raw_brightness = (
            self._current_brightness + (physarum_conn - 0.5) * FEEDBACK_GAIN
        )
        delta_brightness = _clamp(
            raw_brightness - self._current_brightness,
            -FEEDBACK_MAX_DELTA,
            FEEDBACK_MAX_DELTA,
        )
        new_brightness = _clamp(self._current_brightness + delta_brightness)

        self._current_density = new_density
        self._current_brightness = new_brightness

        await self.lyria.set_params(density=new_density, brightness=new_brightness)

    def update_prompts_from_state(self) -> list[dict]:
        boids_density, physarum_conn, _ = self.shared_state.get_visual_metrics()

        prompts = [{"text": "Ethereal Ambience", "weight": 1.0}]

        if boids_density > 0.7:
            prompts.append({"text": "Warm pulse, rhythmic heartbeat", "weight": 0.8})
        elif boids_density < 0.3:
            prompts.append({"text": "Scattered rain, sparse piano", "weight": 0.7})

        if physarum_conn > 0.6:
            prompts.append(
                {"text": "Dense forest texture, interwoven strings", "weight": 0.6}
            )

        return prompts[:3]

    async def update_mute_from_activity(self):
        _, _, activity = self.shared_state.get_visual_metrics()

        if activity < 0.2:
            await self.lyria.set_params(mute_drums=True, mute_bass=True)
        elif activity < 0.5:
            await self.lyria.set_params(mute_drums=True, mute_bass=False)
        else:
            await self.lyria.set_params(mute_drums=False, mute_bass=False)

    async def _apply_gemini_actions(self):
        try:
            action = self.shared_state.gemini_action.get_nowait()
        except queue.Empty:
            return

        if "lyria_prompts" in action:
            await self.lyria.set_prompts(action["lyria_prompts"])
        if "density" in action:
            await self.lyria.set_params(density=action["density"])
        if "brightness" in action:
            await self.lyria.set_params(brightness=action["brightness"])
        if "reasoning" in action:
            logger.info(f"Gemini reasoning: {action['reasoning']}")

    async def run(self):
        while True:
            try:
                await self.update_lyria_from_tolvera()
                await self.update_mute_from_activity()
                await self._apply_gemini_actions()

                prompts = self.update_prompts_from_state()
                await self.lyria.set_prompts(prompts)
            except Exception as e:
                logger.warning(f"Feedback loop error: {e}")

            await asyncio.sleep(FEEDBACK_INTERVAL)

    async def run_narrative_updater(self):
        while True:
            await asyncio.sleep(30)
            try:
                n_pairs = self.shared_state.iml_n_pairs
                self.narrative.update(n_pairs=n_pairs)
            except Exception as e:
                logger.warning(f"Narrative update error: {e}")

    async def start_gemini(self):
        system_prompt = get_system_prompt(self.narrative.get())
        await self.gemini.connect(system_prompt)
        asyncio.create_task(
            self.gemini.gemini_loop(self.narrative, self.lyria.get_latest_audio_chunk)
        )
