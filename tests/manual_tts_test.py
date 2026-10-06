from pathlib import Path

from app.services.tts_service import TTSService


def main():
    output_dir = Path("test_audio")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "tts_response.mp3"

    text = (
        "I can help you with general questions "
        "and information."
    )

    print("=" * 60)
    print("TTS TEST")
    print("=" * 60)

    print("\nText:")
    print(text)

    service = TTSService()

    print("\nGenerating speech...")

    audio = service.synthesize(text)

    output_path.write_bytes(audio)

    print("\nTTS completed successfully.")
    print(f"Audio saved to: {output_path}")
    print(f"Audio size: {len(audio)} bytes")

    print("=" * 60)


if __name__ == "__main__":
    main()