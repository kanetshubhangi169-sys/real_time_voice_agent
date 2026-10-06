import pytest

from app.services.conversation_service import ConversationService


def test_create_session():
    service = ConversationService()

    service.create_session("session-1")

    assert service.get_history("session-1") == []


def test_add_message():
    service = ConversationService()

    service.add_message(
        "session-1",
        "user",
        "My name is Shubhangi."
    )

    history = service.get_history("session-1")

    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "My name is Shubhangi."


def test_multiple_messages():
    service = ConversationService()

    service.add_message(
        "session-1",
        "user",
        "My name is Shubhangi."
    )

    service.add_message(
        "session-1",
        "assistant",
        "Nice to meet you, Shubhangi."
    )

    history = service.get_history("session-1")

    assert len(history) == 2


def test_unknown_session():
    service = ConversationService()

    history = service.get_history(
        "unknown-session"
    )

    assert history == []


def test_invalid_role():
    service = ConversationService()

    with pytest.raises(ValueError):
        service.add_message(
            "session-1",
            "system",
            "Invalid message"
        )


def test_empty_content():
    service = ConversationService()

    with pytest.raises(ValueError):
        service.add_message(
            "session-1",
            "user",
            ""
        )


def test_clear_session():
    service = ConversationService()

    service.add_message(
        "session-1",
        "user",
        "Hello"
    )

    service.clear_session(
        "session-1"
    )

    assert service.get_history(
        "session-1"
    ) == []