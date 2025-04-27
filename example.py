#!/usr/bin/env python3
import sys
from audio_upsampler import main

if __name__ == "__main__":
    sys.argv = [
        "example_run.py",
        "input.wav",  
        "output.wav",  
        "96000",                      
        "--numtaps", "2048",          
        "--beta", "8.0"
    ]
    main.main()
