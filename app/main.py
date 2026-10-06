from fastapi import FastAPI, WebSocket

from app.api.routes import router, voice_service
from app.api.websocket import voice_websocket
from app.config import settings
from app.utils.logger import setup_logging
from app.core.exceptions import VoiceAgentError
from app.core.error_handlers import (
    voice_agent_exception_handler,
)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Real-Time AI Voice Agent API"
)

app.add_exception_handler(
    VoiceAgentError,
    voice_agent_exception_handler,
)


app.include_router(router)


@app.websocket("/api/v1/ws/voice/{session_id}")
async def websocket_voice(
    websocket: WebSocket,
    session_id: str
):
    await voice_websocket(
        websocket=websocket,
        session_id=session_id,
        voice_service=voice_service
    )


@app.get("/")
async def root():
    return {
        "message": "Real-Time AI Voice Agent is running"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }