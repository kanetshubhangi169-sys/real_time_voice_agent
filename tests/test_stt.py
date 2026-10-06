from pathlib import Path

import pytest

from app.services.stt_service import STTService


def test_audio_file_not_found():
    service = STTService()

    with pytest.raises(FileNotFoundError):
        service.transcribe(
            "does_not_exist.wav"
        )


def test_empty_audio_file(tmp_path: Path):
    audio_file = tmp_path / "empty.wav"

    audio_file.write_bytes(b"")

    service = STTService()

    with pytest.raises(ValueError):
        service.transcribe(
            str(audio_file)
        )