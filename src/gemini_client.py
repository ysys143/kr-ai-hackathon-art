import asyncio
import json
import logging
import re

import numpy as np

from src.config import (
    GEMINI_AUDIO_RATE,
    GEMINI_LOOP_INTERVAL,
    GEMINI_MODEL,
    GOOGLE_API_KEY,
)
from src.shared_state import SharedState

logger = logging.getLogger(__name__)


class GeminiClient:
    """Gemini Live API client for visual + audio observation and JSON action output."""

    def __init__(self, shared_state: SharedState):
        import google.genai as genai
        from google.genai import types

        self._genai = genai
        self._types = types
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.session = None
        self.connected = False
        self.shared_state = shared_state

    async def connect(self, system_prompt: str):
        types = self._types
        config = types.LiveConnectConfig(
            response_modalities=["TEXT"],
            system_instruction=system_prompt,
        )
        self.session = await self.client.aio.live.connect(
            model=GEMINI_MODEL, config=config
        ).__aenter__()
        self.connected = True
        self.shared_state.gemini_connected = True
        logger.info("Gemini session connected.")

    async def send_frame(self, jpeg_bytes: bytes):
        types = self._types
        await self.session.send_realtime_input(
            media=types.Blob(data=jpeg_bytes, mime_type="image/jpeg")
        )

    async def send_audio(self, pcm_48k: bytes):
        types = self._types
        samples = np.frombuffer(pcm_48k, dtype=np.int16)
        downsampled = samples[::3]  # 48000/3 = 16000 Hz
        pcm_16k = downsampled.tobytes()
        await self.session.send_realtime_input(
            media=types.Blob(
                data=pcm_16k, mime_type=f"audio/pcm;rate={GEMINI_AUDIO_RATE}"
            )
        )

    async def receive_action(self) -> dict | None:
        try:
            response = await self.session.receive()
            text = None
            if hasattr(response, "text") and response.text:
                text = response.text
            elif (
                hasattr(response, "server_content")
                and response.server_content
                and hasattr(response.server_content, "model_turn")
                and response.server_content.model_turn
            ):
                parts = response.server_content.model_turn.parts
                if parts:
                    text = parts[0].text
            if not text:
                return None

            # PRIMARY: direct json.loads
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                # FALLBACK: regex extract first {...} block
                match = re.search(r"\{.*\}", text, re.DOTALL)
                if match:
                    try:
                        parsed = json.loads(match.group())
                    except json.JSONDecodeError:
                        logger.warning("Gemini: JSON regex fallback failed.")
                        return None
                else:
                    logger.warning("Gemini: no JSON found in response.")
                    return None

            # Validate expected keys
            expected = {"lyria_prompts", "density", "brightness", "reasoning"}
            if not expected.issubset(parsed.keys()):
                logger.warning(f"Gemini: missing keys in response: {parsed.keys()}")
                return None

            return parsed

        except Exception as e:
            logger.warning(f"Gemini receive_action error: {e}")
            return None

    async def send_text(self, text: str):
        types = self._types
        await self.session.send_client_content(
            turns=[types.Content(parts=[types.Part(text=text)])]
        )

    async def gemini_loop(self, narrative_manager, get_latest_audio_fn):
        types = self._types
        iteration = 0
        while True:
            try:
                frame = self.shared_state.latest_jpeg_frame
                if frame:
                    await self.send_frame(frame)

                audio = get_latest_audio_fn()
                if audio:
                    await self.send_audio(audio)

                # Update narrative context every ~30s (every 8 iterations at 3.5s)
                iteration += 1
                if iteration % 8 == 0:
                    try:
                        ghost_state, _, ghost_elapsed = (
                            self.shared_state.get_ghost_info()
                        )
                        context = narrative_manager.get(
                            ghost_state=ghost_state, ghost_value=ghost_elapsed
                        )
                        await self.send_text(f"Updated session context:\n{context}")
                    except Exception as e:
                        logger.debug(f"Narrative update to Gemini failed: {e}")

                await self.session.send_client_content(
                    turns=[
                        types.Content(
                            parts=[types.Part(text="Observe and respond with JSON.")]
                        )
                    ]
                )
                action = await self.receive_action()

                if action:
                    self.shared_state.gemini_action.put_nowait(action)

            except Exception as e:
                logger.warning(f"Gemini loop error: {e}")

            await asyncio.sleep(GEMINI_LOOP_INTERVAL)

    async def close(self):
        if self.session:
            try:
                await self.session.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Gemini close error: {e}")
        self.connected = False
        self.shared_state.gemini_connected = False
        logger.info("Gemini session closed.")
