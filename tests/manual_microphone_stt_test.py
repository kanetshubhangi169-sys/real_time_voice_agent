from pathlib import Path

from app.services.stt_service import STTService


AUDIO_FILE = Path("test_audio/microphone_test.wav")


def main():
    print("=" * 60)
    print("MICROPHONE → STT TEST")
    print("=" * 60)

    if not AUDIO_FILE.exists():
        print(f"Audio file not found: {AUDIO_FILE}")
        return

    print()
    print(f"Audio file: {AUDIO_FILE}")
    print(f"Audio size: {AUDIO_FILE.stat().st_size} bytes")
    print()
    print("Transcribing...")

    service = STTService()

    text = service.transcribe(
        str(AUDIO_FILE)
    )

    print()
    print("Transcription:")
    print(text)

    print("=" * 60)


if __name__ == "__main__":
    main()