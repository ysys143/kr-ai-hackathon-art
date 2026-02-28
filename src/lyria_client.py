import asyncio
import logging
import queue
import time

import numpy as np

from src.config import (
    GOOGLE_API_KEY,
    LYRIA_MODEL,
    DEFAULT_DENSITY,
    DEFAULT_BRIGHTNESS,
    DEFAULT_TEMPERATURE,
    DEFAULT_GUIDANCE,
    LYRIA_SESSION_TIMEOUT,
    AUDIO_CHANNELS,
)
from src.shared_state import SharedState

logger = logging.getLogger(__name__)


class LyriaClient:
    """Manages a persistent Lyria RealTime music generation session."""

    def __init__(self, shared_state: SharedState):
        import google.genai as genai
        from google.genai import types

        self._types = types
        self.client = genai.Client(
            api_key=GOOGLE_API_KEY,
            http_options={"api_version": "v1alpha"},
        )
        self.session = None
        self.connected = False
        self.session_start_time = None
        self.shared_state = shared_state
        self._latest_audio_chunk: bytes = b""

        # Track current config — must send ALL fields every time
        self._density = DEFAULT_DENSITY
        self._brightness = DEFAULT_BRIGHTNESS
        self._temperature = DEFAULT_TEMPERATURE
        self._guidance = DEFAULT_GUIDANCE
        self._mute_drums = True
        self._mute_bass = True

        # Track current prompts for reconnect
        self._current_prompts = [{"text": "Ethereal Ambience", "weight": 1.0}]

    async def connect(self):
        """Establish Lyria session and start playback."""
        try:
            self.session = await self.client.aio.live.music.connect(
                model=LYRIA_MODEL
            ).__aenter__()
            await self.session.set_weighted_prompts(
                prompts=[
                    self._types.WeightedPrompt(text=p["text"], weight=p["weight"])
                    for p in self._current_prompts
                ]
            )
            await self.session.set_music_generation_config(
                density=self._density,
                brightness=self._brightness,
                temperature=self._temperature,
                guidance=self._guidance,
                mute_drums=self._mute_drums,
                mute_bass=self._mute_bass,
            )
            await self.session.play()
            self.session_start_time = time.monotonic()
            self.connected = True
            self.shared_state.lyria_connected = True
            logger.info("Lyria session connected.")
        except Exception as e:
            logger.error("Failed to connect Lyria session: %s", e)
            self.connected = False
            self.shared_state.lyria_connected = False
            raise

    async def receive_audio(self):
        """Background task — receive PCM chunks from Lyria and enqueue them."""
        try:
            async for message in self.session.receive():
                try:
                    chunks = message.server_content.audio_chunks
                    if chunks:
                        for chunk in chunks:
                            raw = chunk.data if hasattr(chunk, "data") else chunk
                            self._latest_audio_chunk = raw
                            # Convert raw PCM int16 bytes to float32 interleaved array
                            pcm = (
                                np.frombuffer(raw, dtype=np.int16).astype(np.float32)
                                / 32768.0
                            )
                            # Reshape to (frames, channels); pad if needed
                            total_samples = pcm.shape[0]
                            frames = total_samples // AUDIO_CHANNELS
                            pcm = pcm[: frames * AUDIO_CHANNELS].reshape(
                                frames, AUDIO_CHANNELS
                            )
                            try:
                                self.shared_state.audio_queue.put_nowait(pcm)
                            except queue.Full:
                                try:
                                    self.shared_state.audio_queue.get_nowait()
                                except queue.Empty:
                                    pass
                                self.shared_state.audio_queue.put_nowait(pcm)
                except Exception as e:
                    logger.warning("Error processing audio message: %s", e)
        except Exception as e:
            logger.error("receive_audio loop terminated: %s", e)
            self.connected = False
            self.shared_state.lyria_connected = False

    async def set_params(
        self,
        density=None,
        brightness=None,
        mute_drums=None,
        mute_bass=None,
        temperature=None,
        guidance=None,
    ):
        """Update music generation config. Always sends all params to avoid API resets."""
        if density is not None:
            self._density = density
        if brightness is not None:
            self._brightness = brightness
        if temperature is not None:
            self._temperature = temperature
        if guidance is not None:
            self._guidance = guidance
        if mute_drums is not None:
            self._mute_drums = mute_drums
        if mute_bass is not None:
            self._mute_bass = mute_bass

        try:
            await self.session.set_music_generation_config(
                density=self._density,
                brightness=self._brightness,
                temperature=self._temperature,
                guidance=self._guidance,
                mute_drums=self._mute_drums,
                mute_bass=self._mute_bass,
            )
        except Exception as e:
            logger.error("set_params failed: %s", e)

    async def set_prompts(self, prompts: list[dict]):
        """Update weighted prompts. Requires at least 1 prompt."""
        if not prompts:
            logger.warning("set_prompts called with empty list — ignoring.")
            return
        self._current_prompts = prompts
        try:
            await self.session.set_weighted_prompts(
                prompts=[
                    self._types.WeightedPrompt(text=p["text"], weight=p["weight"])
                    for p in prompts
                ]
            )
        except Exception as e:
            logger.error("set_prompts failed: %s", e)

    async def reconnect_watchdog(self):
        """Periodically checks session age and reconnects before timeout."""
        while True:
            await asyncio.sleep(30)
            if self.connected and self.session_start_time is not None:
                elapsed = time.monotonic() - self.session_start_time
                if elapsed > LYRIA_SESSION_TIMEOUT:
                    logger.info(
                        "Session timeout approaching (%.0fs) — reconnecting.", elapsed
                    )
                    await self._reconnect()

    async def _reconnect(self):
        """Close and re-establish the session with the same params and prompts."""
        try:
            await self.close()
        except Exception as e:
            logger.warning("Error closing session during reconnect: %s", e)
        try:
            await self.connect()
            logger.info("Lyria reconnected successfully.")
        except Exception as e:
            logger.error("Reconnect failed: %s", e)

    def get_latest_audio_chunk(self) -> bytes:
        """Return the most recent raw PCM bytes received from Lyria."""
        return self._latest_audio_chunk

    async def close(self):
        """Gracefully close the Lyria session."""
        self.connected = False
        self.shared_state.lyria_connected = False
        if self.session is not None:
            try:
                await self.session.__aexit__(None, None, None)
            except Exception as e:
                logger.warning("Error closing Lyria session: %s", e)
            self.session = None
        logger.info("Lyria session closed.")
