import numpy as np
from scipy.signal import firwin

class FIRFilterDesigner:
    def __init__(self, numtaps: int, upsample_factor: int, beta: float = 9.0):
        self.numtaps = numtaps
        self.upsample_factor = upsample_factor
        self.beta = beta

    def design(self) -> np.ndarray:
        cutoff = 1.0 / self.upsample_factor
        return firwin(self.numtaps, cutoff, window=('kaiser', self.beta))
