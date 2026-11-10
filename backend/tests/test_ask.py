"""Tests for POST /ask: the response format from handbook/01-task.md and the error cases."""
import pytest
from fastapi.testclient import TestClient

from compliance_search.api import app as app_module
from compliance_search.api.app import app

CITATION_FIELDS = {"document_id", "version", "article", "page", "quote"}
RETRIEVED_FIELDS = {"document_id", "article"}


@pytest.fixture
def client():
    return TestClient(app)


def test_ask_answers_in_the_handbook_format(client):
    response = client.post("/ask", json={"question": "How often must TLPT run?"})

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"answer", "citations", "retrieved"}
    assert isinstance(body["answer"], str) and body["answer"]
    assert body["citations"], "the placeholder answer cites at least one source"
    for citation in body["citations"]:
        assert set(citation) == CITATION_FIELDS
    for passage in body["retrieved"]:
        assert set(passage) == RETRIEVED_FIELDS


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"question": ""},
        {"question": "   "},
        {"question": None},
        {"question": 42},
    ],
)
def test_ask_rejects_an_invalid_question(client, payload):
    response = client.post("/ask", json=payload)

    assert response.status_code == 422
    assert "detail" in response.json()


def test_ask_rejects_a_body_that_is_not_json(client):
    response = client.post("/ask", content="not json", headers={"content-type": "application/json"})

    assert response.status_code == 422
    assert "detail" in response.json()


def test_ask_turns_an_internal_error_into_a_500_response(monkeypatch):
    def broken(question):
        raise RuntimeError("search is down")

    monkeypatch.setattr(app_module, "answer_question", broken)
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post("/ask", json={"question": "How often must TLPT run?"})

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
