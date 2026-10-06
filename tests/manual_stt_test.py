from app.services.stt_service import STTService


def main():
    audio_path = "test_audio/hello.wav"

    service = STTService()

    print("=" * 60)
    print("STT TEST")
    print("=" * 60)

    text = service.transcribe(audio_path)

    print("\nTranscription:")
    print(text)

    print("=" * 60)


if __name__ == "__main__":
    main()