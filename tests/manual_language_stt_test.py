import sys
import time
import wave
from pathlib import Path

import sounddevice as sd

from app.services.stt_service import STTService


AUDIO_FILE = Path("test_audio/manual_language_test.wav")

SAMPLE_RATE = 16000
CHANNELS = 1


def record_audio():

    print()
    print("🎤 Recording...")
    print("Speak in Hindi, Gujarati, Marathi, or another Indian language.")
    print("Press ENTER to stop recording.")
    print()

    recording = []

    def callback(indata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)

        recording.append(indata.copy())

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        callback=callback
    ):
        input()

    if not recording:
        raise RuntimeError("No audio was recorded.")

    import numpy as np

    audio = np.concatenate(recording, axis=0)

    AUDIO_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with wave.open(
        str(AUDIO_FILE),
        "wb"
    ) as wav_file:

        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio.tobytes())

    print()
    print(f"🛑 Recording stopped.")
    print(f"Audio saved to: {AUDIO_FILE}")
    print(f"Audio size: {AUDIO_FILE.stat().st_size} bytes")


def main():

    print("=" * 60)
    print("MULTILINGUAL STT TEST")
    print("=" * 60)

    print()
    print("This test records NEW microphone audio.")
    print()

    input("Press ENTER to start recording...")

    record_audio()

    print()
    print("Transcribing...")
    print()

    service = STTService()

    result = service.transcribe_with_language(
        str(AUDIO_FILE)
    )

    print()
    print("Transcription:")
    print(result["text"])

    print()
    print("Detected language:")
    print(result["language"])

    print()
    print("=" * 60)
    print("MULTILINGUAL STT TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()