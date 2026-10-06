class VoiceAgentError(Exception):
    """Base exception for expected voice-agent errors."""

    def __init__(
        self,
        message: str,
        code: str = "VOICE_AGENT_ERROR",
    ):
        self.message = message
        self.code = code

        super().__init__(message)


class STTError(VoiceAgentError):
    """Speech-to-text service error."""

    def __init__(
        self,
        message: str = "Speech-to-text service failed.",
    ):
        super().__init__(
            message=message,
            code="STT_SERVICE_ERROR",
        )


class LLMError(VoiceAgentError):
    """LLM service error."""

    def __init__(
        self,
        message: str = "Language model service failed.",
    ):
        super().__init__(
            message=message,
            code="LLM_SERVICE_ERROR",
        )


class TTSError(VoiceAgentError):
    """Text-to-speech service error."""

    def __init__(
        self,
        message: str = "Text-to-speech service failed.",
    ):
        super().__init__(
            message=message,
            code="TTS_SERVICE_ERROR",
        )


class VoiceProcessingError(VoiceAgentError):
    """Complete voice pipeline error."""

    def __init__(
        self,
        message: str = "Voice processing failed.",
    ):
        super().__init__(
            message=message,
            code="VOICE_PROCESSING_ERROR",
        )