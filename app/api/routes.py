import base64
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.stt_service import STTService
from app.services.voice_service import VoiceService
from app.services.conversation_service import ConversationService


router = APIRouter(
    prefix="/api/v1",
    tags=["Voice"]
)


conversation_service = ConversationService()

voice_service = VoiceService(
    conversation_service=conversation_service
)


ALLOWED_AUDIO_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".ogg",
    ".webm"
}


def get_audio_extension(filename: str) -> str:
    """Extract audio file extension."""

    if not filename or "." not in filename:
        return ""

    return "." + filename.rsplit(".", 1)[1].lower()


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...)
):
    """
    Convert uploaded audio into text using STT.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Audio file is required."
        )

    extension = get_audio_extension(
        file.filename
    )

    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported audio format. "
                f"Allowed formats: "
                f"{', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}"
            )
        )

    temp_path = None

    try:
        audio_data = await file.read()

        if not audio_data:
            raise HTTPException(
                status_code=400,
                detail="Uploaded audio file is empty."
            )

        with tempfile.NamedTemporaryFile(
            suffix=extension,
            delete=False
        ) as temp_file:

            temp_file.write(audio_data)
            temp_path = Path(temp_file.name)

        service = STTService()

        text = service.transcribe(
            str(temp_path)
        )

        return {
            "success": True,
            "filename": file.filename,
            "text": text
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Speech-to-text service failed: {exc}"
        ) from exc

    finally:
        if temp_path is not None:
            temp_path.unlink(
                missing_ok=True
            )


@router.post("/voice/chat")
async def voice_chat(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    """
    Process audio through the complete voice pipeline.

    Audio
      ↓
    STT
      ↓
    Conversation History
      ↓
    LLM
      ↓
    TTS
      ↓
    Audio Response
    """

    # ---------------------------------------------------------
    # 1. Validate session ID
    # ---------------------------------------------------------

    if not session_id or not session_id.strip():
        raise HTTPException(
            status_code=400,
            detail="Session ID is required."
        )

    session_id = session_id.strip()

    # ---------------------------------------------------------
    # 2. Validate filename
    # ---------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Audio file is required."
        )

    extension = get_audio_extension(
        file.filename
    )

    # ---------------------------------------------------------
    # 3. Validate audio format
    # ---------------------------------------------------------

    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported audio format. "
                f"Allowed formats: "
                f"{', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}"
            )
        )

    temp_path = None

    try:
        # -----------------------------------------------------
        # 4. Read uploaded audio
        # -----------------------------------------------------

        audio_data = await file.read()

        if not audio_data:
            raise HTTPException(
                status_code=400,
                detail="Uploaded audio file is empty."
            )

        # -----------------------------------------------------
        # 5. Save temporary audio
        # -----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            suffix=extension,
            delete=False
        ) as temp_file:

            temp_file.write(audio_data)
            temp_path = Path(temp_file.name)

        # -----------------------------------------------------
        # 6. Run complete pipeline
        # -----------------------------------------------------

        result = voice_service.process_audio(
            audio_path=str(temp_path),
            session_id=session_id
        )

        # -----------------------------------------------------
        # 7. Convert generated audio to Base64
        # -----------------------------------------------------

        audio_bytes = result["audio"]

        audio_base64 = base64.b64encode(
            audio_bytes
        ).decode("utf-8")

        # -----------------------------------------------------
        # 8. Return complete response
        # -----------------------------------------------------

        return {
            "success": True,
            "session_id": result["session_id"],
            "transcription": result["transcription"],
            "response": result["response"],
            "audio": {
                "format": "mp3",
                "data": audio_base64
            }
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Voice processing failed: {exc}"
        ) from exc

    finally:
        # -----------------------------------------------------
        # 9. Always remove temporary file
        # -----------------------------------------------------

        if temp_path is not None:
            temp_path.unlink(
                missing_ok=True
            )