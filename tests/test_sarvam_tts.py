from app.services.tts_service import TTSService


def main():

    print("=" * 60)
    print("SARVAM BULBUL V3 MULTILINGUAL TTS TEST")
    print("=" * 60)

    tts = TTSService()

    tests = [
        (
            "english",
            "Hello! How are you today?"
        ),
        (
            "hindi",
            "नमस्ते! आप कैसे हैं? मैं आपकी मदद करने के लिए तैयार हूँ।"
        ),
        (
            "gujarati",
            "નમસ્તે! તમે કેમ છો? હું તમારી મદદ કરવા માટે તૈયાર છું."
        ),
        (
            "marathi",
            "नमस्कार! तुम्ही कसे आहात? मी तुमची मदत करण्यासाठी तयार आहे."
        ),
    ]

    for language, text in tests:

        print()
        print("-" * 60)
        print(f"Language: {language}")
        print(f"Text: {text}")

        audio = tts.synthesize(
            text=text,
            language=language
        )

        filename = (
            f"test_audio/sarvam_{language}.mp3"
        )

        with open(filename, "wb") as f:
            f.write(audio)

        print(f"Saved: {filename}")
        print(f"Audio size: {len(audio)} bytes")

    print()
    print("=" * 60)
    print("SARVAM TTS TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()