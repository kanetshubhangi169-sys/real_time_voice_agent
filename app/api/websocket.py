import base64
import json
import tempfile
from pathlib import Path

from fastapi import WebSocket, WebSocketDisconnect

from app.services.voice_service import VoiceService


ALLOWED_AUDIO_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".ogg",
    ".webm",
}


async def voice_websocket(
    websocket: WebSocket,
    session_id: str,
    voice_service: VoiceService,
):
    """
    Handle real-time voice communication over WebSocket.

    Client sends:
        1. JSON metadata:
           {
               "filename": "hello.wav"
           }

        2. Binary audio data.

    Server sends:
        1. transcription event
        2. response event
        3. audio event
    """

    await websocket.accept()

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "session_id": session_id,
                "message": "Voice WebSocket connected."
            }
        )

        while True:
            message = await websocket.receive()

            # -------------------------------------------------
            # Client disconnected
            # -------------------------------------------------

            if message.get("type") == "websocket.disconnect":
                break

            # -------------------------------------------------
            # Receive metadata
            # -------------------------------------------------

            text_data = message.get("text")

            if text_data is None:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": (
                            "Expected JSON metadata before audio."
                        )
                    }
                )
                continue

            try:
                metadata = json.loads(text_data)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": "Invalid JSON metadata."
                    }
                )
                continue

            filename = metadata.get(
                "filename",
                "audio.wav"
            )

            extension = (
                Path(filename).suffix.lower()
            )

            if extension not in ALLOWED_AUDIO_EXTENSIONS:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": (
                            "Unsupported audio format. "
                            f"Allowed formats: "
                            f"{', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}"
                        )
                    }
                )
                continue

            # -------------------------------------------------
            # Receive binary audio
            # -------------------------------------------------

            audio_message = await websocket.receive()

            if audio_message.get("type") == "websocket.disconnect":
                break

            audio_data = audio_message.get("bytes")

            if not audio_data:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": "Audio data is empty."
                    }
                )
                continue

            temp_path = None

            try:
                # ---------------------------------------------
                # Save temporary audio
                # ---------------------------------------------

                with tempfile.NamedTemporaryFile(
                    suffix=extension,
                    delete=False
                ) as temp_file:

                    temp_file.write(audio_data)
                    temp_path = Path(temp_file.name)

                # ---------------------------------------------
                # Processing status
                # ---------------------------------------------

                await websocket.send_json(
                    {
                        "type": "processing",
                        "message": "Processing audio..."
                    }
                )

                # ---------------------------------------------
                # Complete STT → LLM → TTS pipeline
                # ---------------------------------------------

                result = voice_service.process_audio(
                    audio_path=str(temp_path),
                    session_id=session_id
                )

                # ---------------------------------------------
                # Send transcription
                # ---------------------------------------------

                await websocket.send_json(
                    {
                        "type": "transcription",
                        "text": result["transcription"]
                    }
                )

                # ---------------------------------------------
                # Send LLM response
                # ---------------------------------------------

                await websocket.send_json(
                    {
                        "type": "response",
                        "text": result["response"]
                    }
                )

                # ---------------------------------------------
                # Encode generated audio
                # ---------------------------------------------

                audio_base64 = base64.b64encode(
                    result["audio"]
                ).decode("utf-8")

                await websocket.send_json(
                    {
                        "type": "audio",
                        "format": "mp3",
                        "data": audio_base64
                    }
                )

                # ---------------------------------------------
                # Completion event
                # ---------------------------------------------

                await websocket.send_json(
                    {
                        "type": "complete",
                        "session_id": session_id
                    }
                )

            except Exception as exc:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": (
                            f"Voice processing failed: {exc}"
                        )
                    }
                )

            finally:
                if temp_path is not None:
                    temp_path.unlink(
                        missing_ok=True
                    )

    except WebSocketDisconnect:
        pass

    except Exception:
        # Connection-level failure.
        # At this point the client may already be disconnected,
        # so don't attempt to send another message.
        pass