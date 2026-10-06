from pathlib import Path

from groq import Groq

from app.config import settings


class STTService:
    """
    Multilingual Speech-to-Text service using
    Groq Whisper.

    Whisper automatically detects the spoken language.

    Supported Indian languages include:
        Hindi
        Gujarati
        Marathi
        Bengali
        Tamil
        Telugu
        Kannada
        Malayalam
        Punjabi
        Odia
        Assamese
        Urdu
        Sanskrit
        Nepali
        Sindhi
        Kashmiri
        English
    """

    def __init__(self):
        if not settings.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=settings.groq_api_key
        )

        self.model = settings.stt_model

    def transcribe(
        self,
        audio_path: str
    ) -> str:
        """
        Backward-compatible transcription method.

        Returns only the recognized text.
        """

        result = self.transcribe_with_language(
            audio_path
        )

        return result["text"]

        def transcribe_with_language(
        self,
        audio_path: str
    ) -> dict:
        """
        Transcribe audio using automatic Whisper
        language detection.

        Returns:
            {
                "text": "...",
                "language": "hi"
            }
        """

        path = Path(audio_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        if path.stat().st_size == 0:
            raise ValueError(
                "Audio file is empty."
            )

        try:
            with path.open("rb") as audio_file:
                transcription = (
                    self.client.audio.transcriptions.create(
                        file=audio_file,
                        model=self.model,
                        response_format="verbose_json",
                        temperature=0.0
                    )
                )

            text = getattr(
                transcription,
                "text",
                ""
            )

            text = str(
                text or ""
            ).strip()

            if not text:
                raise ValueError(
                    "Speech-to-text returned empty text."
                )

            detected_language = getattr(
                transcription,
                "language",
                None
            )

            language = self._normalize_language(
                detected_language
            )

            print(
                f"Whisper automatic language: {language}"
            )

            print(
                f"Whisper automatic text: {text}"
            )

            return {
                "text": text,
                "language": language
            }

        except (
            FileNotFoundError,
            ValueError
        ):
            raise

        except Exception as exc:
            raise RuntimeError(
                f"Speech-to-text failed: {exc}"
            ) from exc