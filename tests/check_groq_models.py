from app.config import settings
from groq import Groq


def main():
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY is not configured.")

    client = Groq(
        api_key=settings.groq_api_key
    )

    print("=" * 70)
    print("GROQ AVAILABLE MODELS")
    print("=" * 70)

    models = client.models.list()

    for model in models.data:
        print(model.id)

    print("=" * 70)


if __name__ == "__main__":
    main()