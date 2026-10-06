import logging
import time

from app.services.stt_service import STTService
from app.services.llm_service import LLMService
from app.services.tts_service import TTSService
from app.services.conversation_service import ConversationService


logger = logging.getLogger(__name__)


class VoiceService:
    """
    Orchestrates the complete multilingual voice-agent pipeline.

    Audio
      -> STT
      -> Language Detection
      -> Conversation History
      -> LLM
      -> TTS
      -> Audio
    """

    def __init__(
        self,
        stt_service=None,
        llm_service=None,
        tts_service=None,
        conversation_service=None
    ):
        self.stt_service = (
            stt_service or STTService()
        )

        self.llm_service = (
            llm_service or LLMService()
        )

        self.tts_service = (
            tts_service or TTSService()
        )

        self.conversation_service = (
            conversation_service
            or ConversationService()
        )

    def process_audio(
        self,
        audio_path: str,
        session_id: str
    ) -> dict:
        """
        Process user audio through the complete
        multilingual voice pipeline.
        """

        start_time = time.perf_counter()

        logger.info(
            "Voice processing started | session=%s",
            session_id
        )

        try:

            # ==================================================
            # 1. STT + LANGUAGE DETECTION
            # ==================================================

            stt_start = time.perf_counter()

            logger.info(
                "STT started | session=%s",
                session_id
            )

            stt_result = (
                self.stt_service
                .transcribe_with_language(
                    audio_path
                )
            )

            user_text = stt_result["text"]
            detected_language = stt_result["language"]

            stt_duration = (
                time.perf_counter() - stt_start
            )

            logger.info(
                "STT completed | "
                "session=%s | language=%s | duration=%.2fs",
                session_id,
                detected_language,
                stt_duration
            )

            # ==================================================
            # 2. CONVERSATION HISTORY
            # ==================================================

            history = (
                self.conversation_service.get_history(
                    session_id
                )
            )

            logger.info(
                "Conversation history loaded | "
                "session=%s | messages=%d",
                session_id,
                len(history)
            )

            # ==================================================
            # 3. LLM
            # ==================================================

            llm_start = time.perf_counter()

            logger.info(
                "LLM started | "
                "session=%s | language=%s",
                session_id,
                detected_language
            )

            assistant_text = (
                self.llm_service.generate_response(
                    message=user_text,
                    history=history,
                    language=detected_language
                )
            )

            llm_duration = (
                time.perf_counter() - llm_start
            )

            logger.info(
                "LLM completed | "
                "session=%s | duration=%.2fs",
                session_id,
                llm_duration
            )

            # ==================================================
            # 4. STORE USER MESSAGE
            # ==================================================

            self.conversation_service.add_message(
                session_id=session_id,
                role="user",
                content=user_text
            )

            # ==================================================
            # 5. STORE ASSISTANT MESSAGE
            # ==================================================

            self.conversation_service.add_message(
                session_id=session_id,
                role="assistant",
                content=assistant_text
            )

            logger.info(
                "Conversation history updated | session=%s",
                session_id
            )

            # ==================================================
            # 6. TEXT-TO-SPEECH
            # ==================================================

            tts_start = time.perf_counter()

            logger.info(
                "TTS started | "
                "session=%s | language=%s",
                session_id,
                detected_language
            )

            # --------------------------------------------------
            # IMPORTANT:
            #
            # Keep the original one-argument call here for
            # backward compatibility with the existing tests.
            #
            # TTSService itself can determine/use the language
            # when appropriate.
            # --------------------------------------------------

            audio = self.tts_service.synthesize(
                assistant_text,
                language=detected_language
            )

            tts_duration = (
                time.perf_counter() - tts_start
            )

            logger.info(
                "TTS completed | "
                "session=%s | duration=%.2fs",
                session_id,
                tts_duration
            )

            # ==================================================
            # 7. TOTAL PROCESSING TIME
            # ==================================================

            total_duration = (
                time.perf_counter() - start_time
            )

            logger.info(
                "Voice processing completed | "
                "session=%s | language=%s | total_duration=%.2fs",
                session_id,
                detected_language,
                total_duration
            )

            # ==================================================
            # 8. RETURN RESULT
            # ==================================================

            return {
                "session_id": session_id,
                "transcription": user_text,
                "language": detected_language,
                "response": assistant_text,
                "audio": audio
            }

        except Exception:

            total_duration = (
                time.perf_counter() - start_time
            )

            logger.exception(
                "Voice processing failed | "
                "session=%s | duration=%.2fs",
                session_id,
                total_duration
            )

            raise