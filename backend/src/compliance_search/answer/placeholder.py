"""A fixed answer, so that POST /ask works before search and answer generation exist."""
from compliance_search.models import AskResponse, Citation, RetrievedPassage


def answer_question(question: str) -> AskResponse:
    """Return the example answer from handbook/01-task.md, whatever the question is.

    Replace this function with the real retrieval and answer step. The route in
    `compliance_search.api.app` only needs an `AskResponse` back.
    """
    return AskResponse(
        answer="At least every 3 years.",
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
