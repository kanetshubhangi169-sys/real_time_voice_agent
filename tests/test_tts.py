import pytest

from app.services.tts_service import TTSService


def test_empty_text():
    service = TTSService()

    with pytest.raises(ValueError):
        service.synthesize("")


def test_whitespace_text():
    service = TTSService()

    with pytest.raises(ValueError):
        service.synthesize("   ")