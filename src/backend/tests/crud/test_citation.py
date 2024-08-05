import pytest

from backend.crud import citation as citation_crud
from backend.database_models.citation import Citation
from backend.tests.factories import get_factory


@pytest.fixture(autouse=True)
def conversation(session, user):
    return get_factory("Conversation", session).create(id="1", user_id=user.id)


@pytest.fixture(autouse=True)
def message(session, conversation, user):
    return get_factory("Message", session).create(
        id="1", conversation_id=conversation.id, user_id=user.id
    )


@pytest.fixture(autouse=True)
def document(session, conversation, message, user):
    return get_factory("Document", session).create(
        id="1",
        conversation_id=conversation.id,
        message_id=message.id,
        user_id=user.id,
        document_id="hello",
    )


def test_create_citation(session, document, user):
    citation_data = Citation(
        text="Hello, World!",
        user_id=user.id,
        start=1,
        end=2,
        message_id="1",
    )

    citation = citation_crud.create_citation(session, citation_data)
    assert citation.text == citation_data.text
    assert citation.user_id == citation_data.user_id
    assert citation.start == citation_data.start
    assert citation.end == citation_data.end
    assert citation.message_id == citation_data.message_id

    get_factory("CitationDocuments", session).create(
        left_id=document.id, right_id=citation.id
    )

    citation = citation_crud.get_citation(session, citation.id)
    assert citation.text == citation_data.text
    assert citation.user_id == citation_data.user_id
    assert citation.start == citation_data.start
    assert citation.end == citation_data.end
    assert citation.message_id == citation_data.message_id
    assert citation.document_ids == ["hello"]


def test_get_citation(session, user):
    _ = get_factory("Citation", session).create(
        id="1",
        text="Hello, World!",
        user_id=user.id,
        message_id="1",
    )

    citation = citation_crud.get_citation(session, "1")
    assert citation.text == "Hello, World!"
    assert citation.id == "1"


def test_fail_get_nonexistent_citation(session):
    citation = citation_crud.get_citation(session, "123")
    assert citation is None


def test_list_citations(session, user):
    _ = get_factory("Citation", session).create(
        text="Hello, World!", user_id=user.id, message_id="1"
    )

    citations = citation_crud.get_citations(session)
    assert len(citations) == 1
    assert citations[0].text == "Hello, World!"


def test_list_citations_empty(session):
    citations = citation_crud.get_citations(session)
    assert len(citations) == 0


def test_list_citations_with_pagination(session, user):
    for i in range(10):
        get_factory("Citation", session).create(
            text=f"Citation {i}", user_id=user.id, message_id="1"
        )

    citations = citation_crud.get_citations(session, offset=5, limit=5)
    assert len(citations) == 5

    for i, citation in enumerate(citations):
        assert citation.text == f"Citation {i + 5}"


def test_list_citations_by_message_id(session, user):
    for i in range(10):
        get_factory("Citation", session).create(
            text=f"Citation {i}", user_id=user.id, message_id="1"
        )

    citations = citation_crud.get_citations_by_message_id(session, "1")
    assert len(citations) == 10

    for i, citation in enumerate(citations):
        assert citation.text == f"Citation {i}"


def test_list_citations_by_message_id_empty(session):
    citations = citation_crud.get_citations_by_message_id(session, "1")
    assert len(citations) == 0


def test_delete_citation(session, user):
    citation = get_factory("Citation", session).create(
        id="1", text="Hello, World!", user_id=user.id, message_id="1"
    )

    citation_crud.delete_citation(session, "1")

    citation = citation_crud.get_citation(session, "1")
    assert citation is None


def test_delete_citation_nonexistent(session):
    citation = citation_crud.delete_citation(session, "1")
    assert citation is None
