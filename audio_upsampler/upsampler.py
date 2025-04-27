import numpy as np
from scipy.signal import upfirdn
from .filter import FIRFilterDesigner

class AudioUpsampler:
    def __init__(self, numtaps: int = 4096, beta: float = 9.0):
        self.numtaps = numtaps
        self.beta = beta

    def upsample(self, audio: np.ndarray, sr: int, target_sr: int) -> np.ndarray:
        if target_sr % sr != 0:
            raise ValueError("Target sample rate must be a multiple of the input rate")
        upsample_factor = target_sr // sr
        designer = FIRFilterDesigner(self.numtaps, upsample_factor, self.beta)
        fir_filter = designer.design()
        delay = (self.numtaps - 1) // 2
        channels = []
        for ch in range(audio.shape[1]):
            up = upfirdn(fir_filter, audio[:, ch], up=upsample_factor)
            up = up[delay:]
            channels.append(up)
        min_len = min(len(ch) for ch in channels)
        return np.stack([ch[:min_len] for ch in channels], axis=1)
