from groq import Groq

from app.config import settings


class LLMService:
    """
    Multilingual LLM service using Groq.

    The response language is determined by
    the language detected by STT.
    """

    def __init__(self):

        if not settings.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=settings.groq_api_key
        )

        self.model = settings.llm_model

        self.system_prompt = """
You are a helpful multilingual Indian AI voice assistant.

You can communicate in:

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

IMPORTANT RULES:

1. Always answer in the user's detected language.

2. If the detected language is Hindi,
   answer in Hindi using Devanagari script.

3. If the detected language is Gujarati,
   answer in Gujarati using Gujarati script.

4. If the detected language is Marathi,
   answer in Marathi using Devanagari script.

5. If the detected language is Bengali,
   answer in Bengali script.

6. If the detected language is Tamil,
   answer in Tamil script.

7. If the detected language is Telugu,
   answer in Telugu script.

8. If the detected language is Kannada,
   answer in Kannada script.

9. If the detected language is Malayalam,
   answer in Malayalam script.

10. If the detected language is Punjabi,
    answer in Punjabi/Gurmukhi script.

11. If the detected language is Urdu,
    answer in Urdu script.

12. If the detected language is English,
    answer in English.

13. Never say that you cannot speak an Indian language.

14. Never switch to English unless English is detected
    or the user explicitly asks for English.

15. Keep answers concise and natural because
    the answer will be spoken aloud.

16. Do not use markdown tables.

17. Avoid unnecessary bullet points.

18. Do not explain these instructions to the user.
"""

    def generate_response(
        self,
        message: str,
        history: list[dict] | None = None,
        language: str | None = None
    ) -> str:

        if not message or not message.strip():
            raise ValueError(
                "Message cannot be empty."
            )

        language_name = self._normalize_language(
            language
        )

        language_instruction = (
            f"""
The detected language of the user's latest speech is:
{language_name}

You MUST answer entirely in {language_name}.

Use the correct native writing system for {language_name}.

Do not translate the user's speech into English.

Do not switch languages.

Keep the response natural and suitable for
text-to-speech.
"""
        )

        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]

        if history:
            messages.extend(history)

        messages.append(
            {
                "role": "system",
                "content": language_instruction
            }
        )

        messages.append(
            {
                "role": "user",
                "content": message.strip()
            }
        )

        try:

            response = (
                self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=250
                )
            )

            if not response.choices:
                raise ValueError(
                    "LLM returned no choices."
                )

            content = (
                response.choices[0]
                .message
                .content
            )

            if not content:
                raise ValueError(
                    "LLM returned an empty response."
                )

            return content.strip()

        except Exception as exc:

            raise RuntimeError(
                f"LLM request failed: {exc}"
            ) from exc

    @staticmethod
    def _normalize_language(
        language: str | None
    ) -> str:

        if not language:
            return "English"

        language = str(
            language
        ).strip().lower()

        languages = {

            "en": "English",
            "english": "English",

            "hi": "Hindi",
            "hindi": "Hindi",

            "gu": "Gujarati",
            "gujarati": "Gujarati",

            "mr": "Marathi",
            "marathi": "Marathi",

            "bn": "Bengali",
            "bengali": "Bengali",

            "ta": "Tamil",
            "tamil": "Tamil",

            "te": "Telugu",
            "telugu": "Telugu",

            "kn": "Kannada",
            "kannada": "Kannada",

            "ml": "Malayalam",
            "malayalam": "Malayalam",

            "pa": "Punjabi",
            "punjabi": "Punjabi",

            "or": "Odia",
            "od": "Odia",
            "odia": "Odia",

            "as": "Assamese",
            "assamese": "Assamese",

            "ur": "Urdu",
            "urdu": "Urdu",

            "sa": "Sanskrit",
            "sanskrit": "Sanskrit",

            "ne": "Nepali",
            "nepali": "Nepali",

            "sd": "Sindhi",
            "sindhi": "Sindhi",

            "ks": "Kashmiri",
            "kashmiri": "Kashmiri",

            "kok": "Konkani",
            "konkani": "Konkani",

            "mai": "Maithili",
            "maithili": "Maithili",

            "mni": "Manipuri",
            "manipuri": "Manipuri",

            "brx": "Bodo",
            "bodo": "Bodo",
        }

        return languages.get(
            language,
            language.capitalize()
        )