import soundfile as sf
import numpy as np
from typing import Tuple

class AudioIO:
    @staticmethod
    def read(path: str) -> Tuple[np.ndarray, int]:
        audio, sr = sf.read(path)
        if audio.ndim == 1:
            audio = audio[:, np.newaxis]
        return audio, sr

    @staticmethod
    def write(path: str, audio: np.ndarray, sr: int):
        sf.write(path, audio, sr)
