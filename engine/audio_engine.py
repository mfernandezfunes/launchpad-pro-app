from __future__ import annotations
import logging
import threading
from typing import Callable, Optional

import numpy as np
import sounddevice as sd
import soundfile as sf

logger = logging.getLogger(__name__)


class AudioEngine:
    def __init__(self) -> None:
        self._active: dict[int, threading.Thread] = {}
        self._stop_flags: dict[int, threading.Event] = {}

    def play(
        self,
        audio_file: str,
        volume: float,
        mode: str,
        pad_id: int,
        on_complete: Optional[Callable[[int], None]],
        device: Optional[str] = None,
    ) -> None:
        """Reproduce audio para un pad. mode: 'oneshot' | 'loop' | 'toggle'"""
        if mode == "toggle" and pad_id in self._active:
            self.stop(pad_id)
            return

        self.stop(pad_id)
        flag = threading.Event()
        self._stop_flags[pad_id] = flag

        thread = threading.Thread(
            target=self._play_thread,
            args=(audio_file, volume, mode, pad_id, flag, on_complete, device),
            daemon=True,
        )
        self._active[pad_id] = thread
        thread.start()

    def _play_thread(
        self,
        audio_file: str,
        volume: float,
        mode: str,
        pad_id: int,
        flag: threading.Event,
        on_complete: Optional[Callable[[int], None]],
        device: Optional[str],
    ) -> None:
        try:
            data, samplerate = sf.read(audio_file, dtype="float32")
            data = data * volume
            kwargs: dict = {"samplerate": samplerate}
            if device:
                kwargs["device"] = device
            while not flag.is_set():
                sd.play(data, **kwargs)
                sd.wait()
                if mode != "loop" or flag.is_set():
                    break
        except FileNotFoundError:
            logger.warning("Archivo de audio no encontrado: %s", audio_file)
        except Exception as e:
            logger.error("Error reproduciendo %s: %s", audio_file, e)
        finally:
            self._active.pop(pad_id, None)
            self._stop_flags.pop(pad_id, None)
            if on_complete:
                on_complete(pad_id)

    def stop(self, pad_id: int) -> None:
        flag = self._stop_flags.get(pad_id)
        if flag:
            flag.set()
            sd.stop()

    def stop_all(self) -> None:
        for pad_id in list(self._stop_flags):
            self.stop(pad_id)

    def is_playing(self, pad_id: int) -> bool:
        return pad_id in self._active
