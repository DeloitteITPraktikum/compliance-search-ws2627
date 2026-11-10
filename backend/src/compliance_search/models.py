"""Request and response models for POST /ask. The format is fixed by handbook/01-task.md."""
from typing import Annotated

from pydantic import BaseModel, StringConstraints

Question = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class AskRequest(BaseModel):
    question: Question


class Citation(BaseModel):
    """One source the answer rests on."""

    document_id: str  # `id` from the document API
    version: str  # `version_date` from the document API
    article: str
    page: int | None = None
    quote: str


class RetrievedPassage(BaseModel):
    """One passage the search found."""

    document_id: str
    article: str


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    retrieved: list[RetrievedPassage] = []  # the top 10 passages, best first
