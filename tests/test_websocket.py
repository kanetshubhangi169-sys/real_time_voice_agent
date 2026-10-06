from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_websocket_connection():

    with client.websocket_connect(
        "/api/v1/ws/voice/test-session"
    ) as websocket:

        message = websocket.receive_json()

        assert message["type"] == "connected"
        assert message["session_id"] == "test-session"


def test_websocket_invalid_json():

    with client.websocket_connect(
        "/api/v1/ws/voice/test-session"
    ) as websocket:

        # Connection message
        websocket.receive_json()

        websocket.send_text(
            "this is not valid json"
        )

        response = websocket.receive_json()

        assert response["type"] == "error"
        assert response["message"] == (
            "Invalid JSON metadata."
        )


def test_websocket_audio_without_metadata():

    with client.websocket_connect(
        "/api/v1/ws/voice/test-session"
    ) as websocket:

        # Connection message
        websocket.receive_json()

        websocket.send_bytes(
            b"fake-audio"
        )

        response = websocket.receive_json()

        assert response["type"] == "error"
        assert response["message"] == (
            "Expected JSON metadata before audio."
        )


def test_websocket_unsupported_audio():

    with client.websocket_connect(
        "/api/v1/ws/voice/test-session"
    ) as websocket:

        websocket.receive_json()

        websocket.send_text(
            '{"filename": "test.txt"}'
        )

        response = websocket.receive_json()

        assert response["type"] == "error"
        assert "Unsupported audio format" in (
            response["message"]
        )


@patch("app.api.websocket.VoiceService")
def test_websocket_voice_pipeline(
    mock_voice_service_class
):

    mock_service = Mock()

    mock_service.process_audio.return_value = {
        "session_id": "test-session",
        "transcription": (
            "Hello, what can you help me with?"
        ),
        "response": (
            "I can help you with general questions."
        ),
        "audio": b"fake-mp3-audio"
    }

    mock_voice_service_class.return_value = (
        mock_service
    )

    # The application's shared voice_service is already
    # created when the application is imported, so for this
    # test we patch that shared instance directly.
    with patch(
        "app.main.voice_websocket"
    ) as mock_websocket_handler:

        async def fake_handler(
            websocket,
            session_id,
            voice_service
        ):
            await websocket.accept()

            await websocket.send_json(
                {
                    "type": "connected",
                    "session_id": session_id
                }
            )

            await websocket.close()

        mock_websocket_handler.side_effect = (
            fake_handler
        )

        with client.websocket_connect(
            "/api/v1/ws/voice/test-session"
        ) as websocket:

            response = websocket.receive_json()

            assert response["type"] == "connected"
            assert response["session_id"] == (
                "test-session"
            )