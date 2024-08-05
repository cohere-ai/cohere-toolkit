import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.config.deployments import ModelDeploymentName
from backend.database_models import (
    Citation,
    Conversation,
    ConversationFileAssociation,
    Document,
    File,
    Message,
)
from backend.schemas.metrics import MetricsData, MetricsMessageType
from backend.schemas.user import User
from backend.services.file import MAX_FILE_SIZE, MAX_TOTAL_FILE_SIZE
from backend.tests.factories import get_factory


# CONVERSATIONS
def test_list_conversations_empty(session_client: TestClient, user) -> None:
    response = session_client.get("/v1/conversations", headers={"User-Id": user.id})
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 0


def test_list_conversations(session_client: TestClient, session: Session, user) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    response = session_client.get("/v1/conversations", headers={"User-Id": user.id})
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 1


def test_list_conversations_with_agent(
    session_client: TestClient, session: Session, user
) -> None:
    agent = get_factory("Agent", session).create(
        id="agent_id", name="test agent", user=user
    )
    conversation1 = get_factory("Conversation", session).create(
        agent_id=agent.id, user_id=user.id
    )
    _ = get_factory("Conversation", session).create(user_id=user.id)

    response = session_client.get(
        "/v1/conversations", headers={"User-Id": user.id}, params={"agent_id": agent.id}
    )
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 1

    conversation = results[0]
    assert conversation["id"] == conversation1.id


def test_list_conversation_with_deleted_agent(
    session_client: TestClient, session: Session, user
) -> None:
    agent = get_factory("Agent", session).create(
        id="agent_id", name="test agent", user=user
    )
    conversation = get_factory("Conversation", session).create(
        agent_id=agent.id, user_id=user.id
    )

    response = session_client.get(
        "/v1/conversations", headers={"User-Id": user.id}, params={"agent_id": agent.id}
    )
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 1
    assert results[0]["id"] == conversation.id

    # Delete agent and check that conversation is also deleted
    response = session_client.delete(
        f"/v1/agents/{agent.id}", headers={"User-Id": user.id}
    )
    assert response.status_code == 200

    response = session_client.get(
        "/v1/conversations", headers={"User-Id": user.id}, params={"agent_id": agent.id}
    )
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 0


def test_list_conversations_missing_user_id(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    _ = get_factory("Conversation", session).create(user_id=user.id)
    response = session_client.get("/v1/conversations")
    results = response.json()

    assert response.status_code == 401
    assert results == {"detail": "User-Id required in request headers."}


def test_get_conversation(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    response = session_client.get(
        f"/v1/conversations/{conversation.id}",
        headers={"User-Id": conversation.user_id},
    )
    response_conversation = response.json()

    assert response.status_code == 200
    assert response_conversation["id"] == conversation.id
    assert response_conversation["title"] == conversation.title


def test_get_conversation_lists_message_files(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    user = get_factory("User", session).create()
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    file = get_factory("File", session).create(
        user_id=user.id,
    )
    message = get_factory("Message", session).create(
        conversation_id=conversation.id,
        user_id=user.id,
        position=0,
        is_active=True,
        text="hello",
    )

    # Create conversation,message<>file relations
    _ = get_factory("ConversationFileAssociation", session).create(
        conversation_id=conversation.id, user_id=user.id, file_id=file.id
    )
    _ = get_factory("MessageFileAssociation", session).create(
        message_id=message.id, user_id=user.id, file_id=file.id
    )

    session.refresh(conversation)

    response = session_client.get(
        f"/v1/conversations/{conversation.id}",
        headers={"User-Id": conversation.user_id},
    )
    response_conversation = response.json()

    assert response.status_code == 200
    assert response_conversation["id"] == conversation.id
    assert response_conversation["title"] == conversation.title
    assert response_conversation["messages"][0]["files"][0]["id"] == file.id


def test_fail_get_nonexistent_conversation(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    response = session_client.get("/v1/conversations/123", headers={"User-Id": user.id})

    assert response.status_code == 404
    assert response.json() == {"detail": f"Conversation with ID: 123 not found."}


def test_update_conversation_title(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(
        title="test title", user_id=user.id
    )
    response = session_client.put(
        f"/v1/conversations/{conversation.id}",
        json={"title": "new title"},
        headers={"User-Id": user.id},
    )
    response_conversation = response.json()

    assert response.status_code == 200
    assert response_conversation["title"] == "new title"

    # Check if the conversation was updated
    conversation = (
        session.query(Conversation)
        .filter_by(id=conversation.id, user_id=conversation.user_id)
        .first()
    )
    assert conversation is not None
    assert conversation.title == "new title"


def test_update_conversation_description(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(
        description="test description", user_id=user.id
    )
    response = session_client.put(
        f"/v1/conversations/{conversation.id}",
        json={"description": "new description"},
        headers={"User-Id": user.id},
    )
    response_conversation = response.json()

    assert response.status_code == 200
    assert response_conversation["description"] == "new description"

    # Check if the conversation was updated
    conversation = (
        session.query(Conversation)
        .filter_by(id=conversation.id, user_id=conversation.user_id)
        .first()
    )
    assert conversation is not None
    assert conversation.description == "new description"


def test_fail_update_nonexistent_conversation(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    response = session_client.put(
        "/v1/conversations/123",
        json={"title": "new title"},
        headers={"User-Id": user.id},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"Conversation with ID: 123 not found."}


def test_update_conversations_missing_user_id(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    response = session_client.get("/v1/conversations")
    results = response.json()

    assert response.status_code == 401
    assert results == {"detail": "User-Id required in request headers."}


def test_delete_conversation(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(
        title="test title", user_id=user.id
    )
    response = session_client.delete(
        f"/v1/conversations/{conversation.id}",
        headers={"User-Id": user.id},
    )

    assert response.status_code == 200
    assert response.json() == {}

    # Check if the conversation was deleted
    conversation = (
        session.query(Conversation)
        .filter_by(id=conversation.id, user_id=conversation.user_id)
        .first()
    )
    assert conversation is None


def test_fail_delete_nonexistent_conversation(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    response = session_client.delete(
        "/v1/conversations/123", headers={"User-Id": user.id}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"Conversation with ID: 123 not found."}


def test_delete_conversation_with_files(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    file = get_factory("File", session).create(
        id="file_id",
        file_name="test_file.txt",
        user_id=user.id,
    )
    conversation = get_factory("Conversation", session).create(
        id="conversation_id", title="test title", user_id=user.id
    )

    _ = get_factory("ConversationFileAssociation", session).create(
        conversation_id=conversation.id, user_id=user.id, file_id=file.id
    )

    response = session_client.delete(
        f"/v1/conversations/{conversation.id}",
        headers={"User-Id": conversation.user_id},
    )

    assert response.status_code == 200
    assert response.json() == {}

    # Check if the files were deleted
    file = session.query(File).filter(File.id == "file_id").first()
    assert file is None

    # Check if the conversation was deleted
    conversation = (
        session.query(Conversation)
        .filter_by(id="conversation.id", user_id=user.id)
        .first()
    )
    assert conversation is None


def test_delete_conversation_with_messages(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(
        title="test title", user_id=user.id
    )
    _ = get_factory("Message", session).create(
        text="test message",
        conversation_id=conversation.id,
        user_id=user.id,
    )

    response = session_client.delete(
        f"/v1/conversations/{conversation.id}",
        headers={"User-Id": user.id},
    )

    assert response.status_code == 200
    assert response.json() == {}

    # Check if the conversation was deleted
    conversation = (
        session.query(Conversation)
        .filter_by(id=conversation.id, user_id=user.id)
        .first()
    )
    assert conversation is None


def test_delete_conversation_with_children_cascades_delete(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    file = get_factory("File", session).create(
        id="file_id",
        file_name="test_file.txt",
        user_id=user.id,
    )
    conversation = get_factory("Conversation", session).create(
        id="converastion_id", title="test title", user_id=user.id
    )
    message = get_factory("Message", session).create(
        text="test message",
        conversation_id=conversation.id,
        user_id=user.id,
    )
    message_id = message.id
    _ = get_factory("Citation", session).create(message_id=message.id, user_id=user.id)
    _ = get_factory("Document", session).create(
        conversation_id=conversation.id,
        message_id=message.id,
        user_id=user.id,
    )
    _ = get_factory("ConversationFileAssociation", session).create(
        conversation_id=conversation.id, user_id=user.id, file_id=file.id
    )

    response = session_client.delete(
        f"/v1/conversations/{conversation.id}",
        headers={"User-Id": user.id},
    )

    assert response.status_code == 200
    assert response.json() == {}

    # Check if the files were deleted
    db_files = session.query(File).filter(File.id == "file_id").all()
    assert not db_files

    # Check all children deleted
    messages = (
        session.query(Message)
        .filter(
            Message.conversation_id == "converastion_id",
            Message.user_id == user.id,
        )
        .all()
    )
    citations = (
        session.query(Citation)
        .filter(Citation.message_id == message_id, Citation.user_id == user.id)
        .all()
    )
    documents = session.query(Document).filter(Document.message_id == message_id).all()

    assert not messages
    assert not citations
    assert not documents

    # Check if the conversation was deleted
    conversation = (
        session.query(Conversation)
        .filter(
            Conversation.id == "converastion_id",
            Conversation.user_id == user.id,
        )
        .first()
    )
    assert conversation is None


def test_delete_conversation_missing_user_id(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(
        title="test title", user_id=user.id
    )
    response = session_client.delete(f"/v1/conversations/{conversation.id}")

    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


def test_search_conversations(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(
        title="test title", user_id=user.id
    )
    response = session_client.get(
        "/v1/conversations:search",
        headers={"User-Id": user.id},
        params={"query": "test"},
    )
    print("here")
    print(response.json)
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 1
    assert results[0]["id"] == conversation.id


@pytest.mark.skipif(
    os.environ.get("COHERE_API_KEY") is None,
    reason="Cohere API key not set, skipping test",
)
def test_search_conversations_with_reranking(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation1 = get_factory("Conversation", session).create(
        title="Hello, how are you?", text_messages=[], user_id=user.id
    )
    conversation2 = get_factory("Conversation", session).create(
        title="There are are seven colors in the rainbow",
        text_messages=[],
        user_id=user.id,
    )
    response = session_client.get(
        "/v1/conversations:search",
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
        params={"query": "color"},
    )
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 1
    assert results[0]["id"] == conversation2.id


@pytest.mark.skipif(
    os.environ.get("COHERE_API_KEY") is None,
    reason="Cohere API key not set, skipping test",
)
def test_search_conversations_with_reranking_sends_metrics(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation1 = get_factory("Conversation", session).create(
        title="Hello, how are you?", text_messages=[], user_id=user.id
    )
    conversation2 = get_factory("Conversation", session).create(
        title="There are are seven colors in the rainbow",
        text_messages=[],
        user_id=user.id,
    )
    with patch(
        "backend.services.metrics.report_metrics",
        return_value=None,
    ) as mock_metrics:
        response = session_client.get(
            "/v1/conversations:search",
            headers={
                "User-Id": user.id,
                "Deployment-Name": ModelDeploymentName.CoherePlatform,
            },
            params={"query": "color"},
        )
        results = response.json()
        assert response.status_code == 200
        m_args: MetricsData = mock_metrics.await_args.args[0].signal
        assert m_args.user_id == user.id
        assert m_args.model == "rerank-english-v2.0"

        assert m_args.message_type == MetricsMessageType.RERANK_API_SUCCESS
        assert m_args.duration_ms is not None and m_args.duration_ms > 0
        assert m_args.assistant_id is not None
        assert m_args.assistant.name is not None
        assert m_args.model is not None
        assert m_args.search_units > 0


def test_search_conversations_missing_user_id(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(
        title="test title", user_id=user.id
    )
    response = session_client.get("/v1/conversations:search", params={"query": "test"})
    results = response.json()

    assert response.status_code == 401
    assert results == {"detail": "User-Id required in request headers."}


def test_search_conversations_no_conversations(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    _ = get_factory("Conversation", session).create(title="test title", user_id=user.id)
    user2 = get_factory("User", session).create()

    response = session_client.get(
        "/v1/conversations:search",
        headers={"User-Id": user2.id},
        params={"query": "test"},
    )

    assert response.status_code == 200
    assert response.json() == []


# FILES
def test_list_files(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    file = get_factory("File", session).create(
        file_name="test_file.txt",
        user_id=user.id,
    )
    conversation = get_factory("Conversation", session).create(
        user_id=user.id,
    )
    _ = get_factory("ConversationFileAssociation", session).create(
        conversation_id=conversation.id, user_id=user.id, file_id=file.id
    )

    response = session_client.get(
        f"/v1/conversations/{conversation.id}/files",
        headers={"User-Id": conversation.user_id},
    )

    assert response.status_code == 200
    response = response.json()
    assert len(response) == 1
    response_file = response[0]
    assert response_file["id"] == file.id
    assert response_file["file_name"] == "test_file.txt"


def test_list_files_no_files(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    response = session_client.get(
        f"/v1/conversations/{conversation.id}/files",
        headers={"User-Id": conversation.user_id},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_list_files_missing_user_id(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    response = session_client.get(f"/v1/conversations/{conversation.id}/files")

    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


def test_upload_file_existing_conversation(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    file_path = "src/backend/tests/test_data/Mariana_Trench.pdf"
    saved_file_path = "src/backend/data/Mariana_Trench.pdf"
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    file_doc = {"file": open(file_path, "rb")}

    response = session_client.post(
        "/v1/conversations/upload_file",
        headers={"User-Id": conversation.user_id},
        files=file_doc,
        data={"conversation_id": conversation.id},
    )

    file = response.json()

    file_in_db = session.get(File, file.get("id"))
    assert file_in_db is not None
    assert response.status_code == 200
    assert "Mariana_Trench" in file["file_name"]
    assert conversation.file_ids == [file_in_db.id]

    # File should not exist in the directory
    assert not os.path.exists(saved_file_path)


def test_upload_file_nonexistent_conversation_creates_new_conversation(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    file_path = "src/backend/tests/test_data/Mariana_Trench.pdf"
    saved_file_path = "src/backend/data/Mariana_Trench.pdf"
    file_doc = {"file": open(file_path, "rb")}

    response = session_client.post(
        "/v1/conversations/upload_file", files=file_doc, headers={"User-Id": user.id}
    )

    file = response.json()

    conversation_file_association = (
        session.query(ConversationFileAssociation)
        .filter_by(file_id=file.get("id"))
        .first()
    )
    created_conversation = (
        session.query(Conversation)
        .filter_by(id=conversation_file_association.conversation_id)
        .first()
    )
    file_in_db = session.get(File, file.get("id"))
    assert file_in_db is not None
    assert response.status_code == 200
    assert created_conversation is not None
    assert created_conversation.user_id == user.id
    assert conversation_file_association is not None
    assert "Mariana_Trench" in file.get("file_name")

    # File should not exist in the directory
    assert not os.path.exists(saved_file_path)


def test_upload_file_nonexistent_conversation_fails_if_user_id_not_provided(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    file_path = "src/backend/tests/test_data/Mariana_Trench.pdf"
    file_doc = {"file": open(file_path, "rb")}

    response = session_client.post("/v1/conversations/upload_file", files=file_doc)

    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


def test_batch_upload_file_existing_conversation(
    session_client: TestClient, session: Session, user
) -> None:
    file_paths = {
        "Mariana_Trench.pdf": "src/backend/tests/test_data/Mariana_Trench.pdf",
        "Cardistry.pdf": "src/backend/tests/test_data/Cardistry.pdf",
        "Tapas.pdf": "src/backend/tests/test_data/Tapas.pdf",
        "Mount_Everest.pdf": "src/backend/tests/test_data/Mount_Everest.pdf",
    }
    saved_file_paths = [
        "src/backend/data/Mariana_Trench.pdf",
        "src/backend/data/Cardistry.pdf",
        "src/backend/data/Tapas.pdf",
        "src/backend/data/Mount_Everest.pdf",
    ]
    files = [
        ("files", (file_name, open(file_path, "rb")))
        for file_name, file_path in file_paths.items()
    ]

    conversation = get_factory("Conversation", session).create(user_id=user.id)

    response = session_client.post(
        "/v1/conversations/batch_upload_file",
        headers={"User-Id": conversation.user_id},
        files=files,
        data={"conversation_id": conversation.id},
    )

    files = response.json()

    assert response.status_code == 200
    assert len(files) == len(file_paths)
    uploaded_file_names = [file["file_name"] for file in files]
    assert (
        all(file_name in uploaded_file_names for file_name in file_paths.keys()) == True
    )
    for file in files:
        conversation_file_association = (
            session.query(ConversationFileAssociation)
            .filter_by(conversation_id=conversation.id, file_id=file.get("id"))
            .first()
        )
        assert conversation_file_association is not None

    # File should not exist in the directory
    for saved_file_path in saved_file_paths:
        assert not os.path.exists(saved_file_path)


def test_batch_upload_total_files_exceeds_limit(
    session_client: TestClient, session: Session, user
) -> None:
    _ = get_factory("Conversation", session).create(user_id=user.id)
    file_paths = {
        "Mariana_Trench.pdf": "src/backend/tests/test_data/Mariana_Trench.pdf",
        "Cardistry.pdf": "src/backend/tests/test_data/Cardistry.pdf",
        "Tapas.pdf": "src/backend/tests/test_data/Tapas.pdf",
        "Mount_Everest.pdf": "src/backend/tests/test_data/Mount_Everest.pdf",
    }
    files = [
        ("files", (file_name, open(file_path, "rb")))
        for file_name, file_path in file_paths.items()
    ]

    conversation = get_factory("Conversation", session).create(user_id=user.id)
    file = get_factory("File", session).create(
        file_name="test_file.txt",
        user_id=conversation.user_id,
        file_size=1000000000,
    )
    _ = get_factory("ConversationFileAssociation", session).create(
        conversation_id=conversation.id, user_id=user.id, file_id=file.id
    )

    response = session_client.post(
        "/v1/conversations/batch_upload_file",
        files=files,
        headers={"User-Id": conversation.user_id},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": f"Total file size exceeds the maximum allowed size of {MAX_TOTAL_FILE_SIZE} bytes."
    }


def test_batch_upload_single_file_exceeds_limit(
    session_client: TestClient, session: Session, user
) -> None:
    _ = get_factory("Conversation", session).create(user_id=user.id)
    file_paths = {
        "Mariana_Trench.pdf": "src/backend/tests/test_data/Mariana_Trench.pdf",
        "Cardistry.pdf": "src/backend/tests/test_data/Cardistry.pdf",
        "26mb.pdf": "src/backend/tests/test_data/26mb.pdf",
        "Tapas.pdf": "src/backend/tests/test_data/Tapas.pdf",
        "Mount_Everest.pdf": "src/backend/tests/test_data/Mount_Everest.pdf",
    }
    files = [
        ("files", (file_name, open(file_path, "rb")))
        for file_name, file_path in file_paths.items()
    ]

    conversation = get_factory("Conversation", session).create(user_id=user.id)

    response = session_client.post(
        "/v1/conversations/batch_upload_file",
        files=files,
        headers={"User-Id": conversation.user_id},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": f"26mb.pdf exceeds the maximum allowed size of {MAX_FILE_SIZE} bytes."
    }


def test_batch_upload_file_nonexistent_conversation_creates_new_conversation(
    session_client: TestClient, session: Session, user
) -> None:
    file_paths = {
        "Mariana_Trench.pdf": "src/backend/tests/test_data/Mariana_Trench.pdf",
        "Cardistry.pdf": "src/backend/tests/test_data/Cardistry.pdf",
        "Tapas.pdf": "src/backend/tests/test_data/Tapas.pdf",
        "Mount_Everest.pdf": "src/backend/tests/test_data/Mount_Everest.pdf",
    }
    saved_file_paths = [
        "src/backend/data/Mariana_Trench.pdf",
        "src/backend/data/Cardistry.pdf",
        "src/backend/data/Tapas.pdf",
        "src/backend/data/Mount_Everest.pdf",
    ]
    files = [
        ("files", (file_name, open(file_path, "rb")))
        for file_name, file_path in file_paths.items()
    ]

    response = session_client.post(
        "/v1/conversations/batch_upload_file",
        files=files,
        headers={"User-Id": user.id},
    )

    uploaded_files = response.json()

    conversation_file_association = (
        session.query(ConversationFileAssociation)
        .filter_by(file_id=uploaded_files[0].get("id"))
        .first()
    )
    created_conversation = (
        session.query(Conversation)
        .filter_by(id=conversation_file_association.conversation_id)
        .first()
    )

    assert conversation_file_association is not None
    assert response.status_code == 200
    assert created_conversation is not None
    assert len(files) == len(file_paths)
    uploaded_file_names = [file["file_name"] for file in uploaded_files]
    assert (
        all(file_name in uploaded_file_names for file_name in file_paths.keys()) == True
    )

    for file in uploaded_files:
        conversation_file_association = (
            session.query(ConversationFileAssociation)
            .filter_by(file_id=file.get("id"), conversation_id=created_conversation.id)
            .first()
        )
        assert conversation_file_association is not None

    # File should not exist in the directory
    for saved_file_path in saved_file_paths:
        assert not os.path.exists(saved_file_path)


def test_batch_upload_file_nonexistent_conversation_fails_if_user_id_not_provided(
    session_client: TestClient, session: Session, user
) -> None:
    file_paths = {
        "Mariana_Trench.pdf": "src/backend/tests/test_data/Mariana_Trench.pdf",
        "Cardistry.pdf": "src/backend/tests/test_data/Cardistry.pdf",
        "Tapas.pdf": "src/backend/tests/test_data/Tapas.pdf",
        "Mount_Everest.pdf": "src/backend/tests/test_data/Mount_Everest.pdf",
    }
    saved_file_paths = [
        "src/backend/data/Mariana_Trench.pdf",
        "src/backend/data/Cardistry.pdf",
        "src/backend/data/Tapas.pdf",
        "src/backend/data/Mount_Everest.pdf",
    ]
    files = [
        ("files", (file_name, open(file_path, "rb")))
        for file_name, file_path in file_paths.items()
    ]

    response = session_client.post("/v1/conversations/upload_file", files=files)

    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


def test_update_file_name(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    file = get_factory("File", session).create(
        file_name="test_file.txt",
        user_id=conversation.user_id,
    )
    response = session_client.put(
        f"/v1/conversations/{conversation.id}/files/{file.id}",
        headers={"User-Id": conversation.user_id},
        json={"file_name": "new name"},
    )
    response_file = response.json()

    assert response.status_code == 200
    assert response_file["file_name"] == "new name"

    # Check if the file was updated
    file = (
        session.query(File).filter_by(id=file.id, user_id=conversation.user_id).first()
    )
    assert file is not None
    assert file.file_name == "new name"


def test_fail_update_nonexistent_file(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    response = session_client.put(
        f"/v1/conversations/{conversation.id}/files/123",
        json={"file_name": "new name"},
        headers={"User-Id": conversation.user_id},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"File with ID: 123 not found."}


def test_fail_update_nonexistent_file(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    response = session_client.put(
        f"/v1/conversations/123/files/123",
        json={"file_name": "new name"},
        headers={"User-Id": user.id},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"Conversation with ID: 123 not found."}


def test_fail_update_file_missing_user_id(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    file = get_factory("File", session).create(
        file_name="test_file.txt",
        user_id=conversation.user_id,
    )

    response = session_client.put(
        f"/v1/conversations/{conversation.id}/files/{file.id}",
        json={"file_name": "new name"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


def test_delete_file(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    file = get_factory("File", session).create(
        id="file_id",
        file_name="test_file.txt",
        user_id=conversation.user_id,
    )
    _ = get_factory("ConversationFileAssociation", session).create(
        conversation_id=conversation.id, user_id=user.id, file_id=file.id
    )

    response = session_client.delete(
        f"/v1/conversations/{conversation.id}/files/{file.id}",
        headers={"User-Id": conversation.user_id},
    )

    assert response.status_code == 200
    assert response.json() == {}

    # Check if File
    db_file = (
        session.query(File)
        .filter(File.id == "file_id", File.user_id == user.id)
        .first()
    )
    assert db_file is None

    conversation_file_association = (
        session.query(ConversationFileAssociation)
        .filter(File.id == "file_id", File.user_id == user.id)
        .first()
    )
    assert conversation_file_association is None

    conversation = (
        session.query(Conversation).filter(Conversation.id == conversation.id).first()
    )
    assert conversation.file_ids == []


def test_fail_delete_nonexistent_file(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    response = session_client.delete(
        f"/v1/conversations/{conversation.id}/files/123",
        headers={"User-Id": conversation.user_id},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"File with ID: 123 not found."}


def test_fail_delete_file_missing_user_id(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    file = get_factory("File", session).create(
        file_name="test_file.txt",
        user_id=conversation.user_id,
    )

    response = session_client.delete(
        f"/v1/conversations/{conversation.id}/files/{file.id}"
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


# MISC
def test_generate_title(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    response = session_client.post(
        f"/v1/conversations/{conversation.id}/generate-title",
        headers={"User-Id": conversation.user_id},
    )
    title = response.json()

    assert response.status_code == 200
    assert title["title"] is not None

    # Check if the conversation was updated
    conversation = (
        session.query(Conversation)
        .filter_by(id=conversation.id, user_id=conversation.user_id)
        .first()
    )
    assert conversation is not None
    assert conversation.title == title["title"]


def test_fail_generate_title_missing_user_id(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    response = session_client.post(
        f"/v1/conversations/{conversation.id}/generate-title"
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


def test_fail_generate_title_nonexistent_conversation(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    response = session_client.post(
        "/v1/conversations/123/generate-title", headers={"User-Id": user.id}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": f"Conversation with ID: 123 not found."}
