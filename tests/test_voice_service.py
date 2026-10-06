from unittest.mock import Mock

from app.services.voice_service import VoiceService


def test_voice_pipeline():
    # --------------------------------------------------
    # Mock STT
    # --------------------------------------------------

    stt = Mock()

    stt.transcribe_with_language.return_value = {
        "text": "Hello, what can you help me with?",
        "language": "english",
    }

    # --------------------------------------------------
    # Mock LLM
    # --------------------------------------------------

    llm = Mock()

    llm.generate_response.return_value = (
        "I can help you with general questions "
        "and information."
    )

    # --------------------------------------------------
    # Mock TTS
    # --------------------------------------------------

    tts = Mock()

    tts.synthesize.return_value = b"fake-audio-data"

    # --------------------------------------------------
    # Mock conversation service
    # --------------------------------------------------

    conversation = Mock()

    conversation.get_history.return_value = []

    # --------------------------------------------------
    # Create voice service
    # --------------------------------------------------

    voice_service = VoiceService(
        stt_service=stt,
        llm_service=llm,
        tts_service=tts,
        conversation_service=conversation
    )

    # --------------------------------------------------
    # Run pipeline
    # --------------------------------------------------

    result = voice_service.process_audio(
        audio_path="test_audio/hello.wav",
        session_id="test-session"
    )

    # --------------------------------------------------
    # Assertions
    # --------------------------------------------------

    assert result["session_id"] == "test-session"

    assert (
        result["transcription"]
        == "Hello, what can you help me with?"
    )

    assert (
        result["response"]
        == "I can help you with general questions "
           "and information."
    )

    assert result["audio"] == b"fake-audio-data"

    assert result["language"] == "english"

    # --------------------------------------------------
    # Verify service calls
    # --------------------------------------------------

    stt.transcribe_with_language.assert_called_once_with(
        "test_audio/hello.wav"
    )

    llm.generate_response.assert_called_once()

    tts.synthesize.assert_called_once_with(
        "I can help you with general questions "
        "and information.",
        language="english"
)