"""The FastAPI app with POST /ask.

Start it from `backend/`:

    uv run uvicorn compliance_search.api.app:app --port 8000
"""
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from compliance_search.answer.placeholder import answer_question
from compliance_search.models import AskRequest, AskResponse

logger = logging.getLogger(__name__)

app = FastAPI(title="Compliance Search")


@app.exception_handler(Exception)
async def internal_error(request: Request, exc: Exception) -> JSONResponse:
    """Answer with JSON instead of crashing. The details go to the log, not to the client."""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.post("/ask")
def ask(request: AskRequest) -> AskResponse:
    return answer_question(request.question)
