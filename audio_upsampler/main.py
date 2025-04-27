import argparse
from audio_upsampler.io import AudioIO
from audio_upsampler.upsampler import AudioUpsampler

def main():
    parser = argparse.ArgumentParser(description="High-quality audio upsampler")
    parser.add_argument("input", help="Path to the source audio file")
    parser.add_argument("output", help="Path where the upsampled audio will be saved")
    parser.add_argument("target_sr", type=int, help="Target sample rate in Hz")
    parser.add_argument("--numtaps", type=int, default=4096, help="Number of filter taps")
    parser.add_argument("--beta", type=float, default=9.0, help="Kaiser window beta parameter")
    args = parser.parse_args()

    audio, sr = AudioIO.read(args.input)
    print(f"Loaded {args.input} ({sr} Hz)")

    upsampler = AudioUpsampler(args.numtaps, args.beta)
    result = upsampler.upsample(audio, sr, args.target_sr)

    AudioIO.write(args.output, result, args.target_sr)
    print(f"Saved {args.output} ({args.target_sr} Hz)")

if __name__ == "__main__":
    main()
