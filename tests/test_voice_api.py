from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_voice_chat_without_file():
    response = client.post(
        "/api/v1/voice/chat",
        data={
            "session_id": "test-session"
        }
    )

    assert response.status_code == 422


def test_voice_chat_without_session_id():
    response = client.post(
        "/api/v1/voice/chat",
        files={
            "file": (
                "test.wav",
                b"fake-audio",
                "audio/wav"
            )
        }
    )

    assert response.status_code == 422


def test_voice_chat_empty_file():
    response = client.post(
        "/api/v1/voice/chat",
        data={
            "session_id": "test-session"
        },
        files={
            "file": (
                "test.wav",
                b"",
                "audio/wav"
            )
        }
    )

    assert response.status_code == 400


def test_voice_chat_unsupported_file():
    response = client.post(
        "/api/v1/voice/chat",
        data={
            "session_id": "test-session"
        },
        files={
            "file": (
                "test.txt",
                b"hello",
                "text/plain"
            )
        }
    )

    assert response.status_code == 400


@patch("app.api.routes.voice_service")
def test_voice_chat_success(mock_voice_service):

    mock_voice_service.process_audio.return_value = {
        "session_id": "test-session",
        "transcription": (
            "Hello, what can you help me with?"
        ),
        "response": (
            "I can help you with general questions "
            "and information."
        ),
        "audio": b"fake-mp3-audio"
    }

    response = client.post(
        "/api/v1/voice/chat",
        data={
            "session_id": "test-session"
        },
        files={
            "file": (
                "test.wav",
                b"fake-audio",
                "audio/wav"
            )
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["session_id"] == "test-session"

    assert data["transcription"] == (
        "Hello, what can you help me with?"
    )

    assert data["response"] == (
        "I can help you with general questions "
        "and information."
    )

    assert data["audio"]["format"] == "mp3"
    assert data["audio"]["data"]


@patch("app.api.routes.voice_service")
def test_voice_chat_missing_session_id_value(
    mock_voice_service
):

    response = client.post(
        "/api/v1/voice/chat",
        data={
            "session_id": "   "
        },
        files={
            "file": (
                "test.wav",
                b"fake-audio",
                "audio/wav"
            )
        }
    )

    assert response.status_code == 400

    mock_voice_service.process_audio.assert_not_called()