import logging
import queue

import numpy as np
import sounddevice as sd

from src.config import (
    AUDIO_SAMPLE_RATE,
    AUDIO_CHANNELS,
    AUDIO_BLOCK_SIZE,
    AUDIO_PREFILL_BLOCKS,
)
from src.shared_state import SharedState

logger = logging.getLogger(__name__)


class AudioBridge:
    """Routes PCM audio from shared_state.audio_queue to a sounddevice output stream."""

    def __init__(self, shared_state: SharedState):
        self.shared_state = shared_state

        silence = np.zeros((AUDIO_BLOCK_SIZE, AUDIO_CHANNELS), dtype=np.float32)
        for _ in range(AUDIO_PREFILL_BLOCKS):
            shared_state.audio_queue.put(silence)

        self.stream = sd.OutputStream(
            samplerate=AUDIO_SAMPLE_RATE,
            channels=AUDIO_CHANNELS,
            callback=self._audio_callback,
            blocksize=AUDIO_BLOCK_SIZE,
            dtype="float32",
        )

    def _audio_callback(self, outdata, frames, time_info, status):
        """Non-blocking audio callback — fills outdata from queue or outputs silence."""
        if status:
            logger.debug("Audio stream status: %s", status)
        try:
            data = self.shared_state.audio_queue.get_nowait()
            if data.shape[0] < frames:
                outdata[: data.shape[0]] = data
                outdata[data.shape[0] :] = 0
            else:
                outdata[:] = data[:frames]
        except queue.Empty:
            outdata[:] = 0

    def start(self):
        """Start the audio output stream."""
        self.stream.start()
        logger.info("AudioBridge stream started.")

    def stop(self):
        """Stop and close the audio output stream."""
        self.stream.stop()
        self.stream.close()
        logger.info("AudioBridge stream stopped.")
