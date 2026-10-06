import pytest

from app.services.llm_service import LLMService


def test_empty_message():
    service = LLMService()

    with pytest.raises(ValueError):
        service.generate_response("")


def test_whitespace_message():
    service = LLMService()

    with pytest.raises(ValueError):
        service.generate_response("   ")