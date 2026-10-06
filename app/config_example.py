# from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):
#     app_name: str = "Real-Time AI Voice Agent"
#     app_env: str = "development"
#     log_level: str = "INFO"

#     groq_api_key: str = "enter groq api key"
#     elevenlabs_api_key: str = "enter_elevenlabs_api_key"

#     stt_model: str = "whisper-large-v3-turbo"
#     llm_model: str = "openai/gpt-oss-20b"

#     tts_voice_id: str = "enter_voice_id_from_elevenlabs"
#     tts_model_id: str = "eleven_flash_v2_5"

#     database_url: str = "sqlite:///./voice_agent.db"

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         extra="ignore"
#     )


# settings = Settings()