"""First answer flow using the question embedding API."""

from compliance_search.models import AskResponse, Citation, RetrievedPassage
from compliance_search.question.question_retrieval import retrieve_question
from compliance_search.clients.embedding_api import (
    createEmbedding,
    startEmbeddingClient,
)


def answer_question(question: str) -> AskResponse:
    """Create an embedding for a question and return the first answer response.

    The question is supplied by the caller so this function can be used by both
    the API and the terminal interface.
    """
    client = startEmbeddingClient()
    vector = createEmbedding(client, question)

    return AskResponse(
        answer=f"Embedding für die Frage wurde erstellt und lautet {vector} ({len(vector)} Dimensionen).",
        citations=[
            Citation(
                document_id="32022R2554_EN",
                version="2022-12-14",
                article="Article 26(1)",
                page=46,
                quote="shall carry out at least every 3 years advanced testing by means of TLPT",
            )
        ],
        retrieved=[RetrievedPassage(document_id="32022R2554_EN", article="Article 26")],
    )


def answer_from_terminal() -> tuple[str, AskResponse]:
    """Read a question from the terminal and create its first answer response."""
    language, request = retrieve_question()
    return language, answer_question(request.question)


if __name__ == "__main__":
    language, response = answer_from_terminal()
    print(f"\nLanguage: {language}")
    print(f"Answer: {response.answer}")
