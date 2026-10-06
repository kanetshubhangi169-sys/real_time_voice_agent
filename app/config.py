from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class Settings(BaseSettings):

    app_name: str = "Real-Time AI Voice Agent"

    app_env: str = "development"

    log_level: str = "INFO"

    # --------------------------------------------------
    # API Keys
    # --------------------------------------------------

    groq_api_key: str = ""

    sarvam_api_key: str = ""

    # --------------------------------------------------
    # Models
    # --------------------------------------------------

    stt_model: str = (
        "whisper-large-v3-turbo"
    )

    llm_model: str = (
        "openai/gpt-oss-20b"
    )

    # --------------------------------------------------
    # Sarvam TTS
    # --------------------------------------------------

    tts_model_id: str = (
        "bulbul:v3"
    )

    tts_speaker: str = "shubh"

    tts_sample_rate: int = 24000

    tts_codec: str = "mp3"

    # --------------------------------------------------
    # Database
    # --------------------------------------------------

    database_url: str = (
        "sqlite:///./voice_agent.db"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()