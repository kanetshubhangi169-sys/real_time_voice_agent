from app.services.llm_service import LLMService


def main():
    service = LLMService()

    print("=" * 60)
    print("LLM CONVERSATION TEST")
    print("=" * 60)

    history = [
        {
            "role": "user",
            "content": "My name is Shubhangi."
        },
        {
            "role": "assistant",
            "content": "Nice to meet you, Shubhangi."
        }
    ]

    message = "What is my name?"

    print(f"\nUser:\n{message}")

    response = service.generate_response(
        message=message,
        history=history
    )

    print(f"\nAssistant:\n{response}")

    print("=" * 60)


if __name__ == "__main__":
    main()