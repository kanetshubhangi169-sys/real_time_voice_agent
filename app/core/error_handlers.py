import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import VoiceAgentError


logger = logging.getLogger(__name__)


async def voice_agent_exception_handler(
    request: Request,
    exc: VoiceAgentError,
):
    """
    Convert expected application exceptions into
    consistent API responses.
    """

    logger.error(
        "Application error | "
        "path=%s | code=%s | message=%s",
        request.url.path,
        exc.code,
        exc.message,
    )

    return JSONResponse(
        status_code=502,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        },
    )