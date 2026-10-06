import sounddevice as sd
import soundfile as sf


SAMPLE_RATE = 16000
CHANNELS = 1
DURATION = 5

OUTPUT_FILE = "test_audio/microphone_test.wav"


def main():
    print("=" * 60)
    print("MICROPHONE TEST")
    print("=" * 60)

    print()
    print(f"Recording for {DURATION} seconds...")
    print("Speak into your microphone!")
    print()

    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32"
    )

    sd.wait()

    sf.write(
        OUTPUT_FILE,
        audio,
        SAMPLE_RATE
    )

    print()
    print("Recording completed.")
    print(f"Audio saved to: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()