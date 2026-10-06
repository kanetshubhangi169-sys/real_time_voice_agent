from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_transcribe_without_file():
    response = client.post(
        "/api/v1/transcribe"
    )

    assert response.status_code == 422


def test_transcribe_unsupported_file():
    response = client.post(
        "/api/v1/transcribe",
        files={
            "file": (
                "test.txt",
                b"hello",
                "text/plain"
            )
        }
    )

    assert response.status_code == 400

    data = response.json()

    assert "Unsupported audio format" in data["detail"]


def test_transcribe_empty_file():
    response = client.post(
        "/api/v1/transcribe",
        files={
            "file": (
                "empty.wav",
                b"",
                "audio/wav"
            )
        }
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"] == "Uploaded audio file is empty."