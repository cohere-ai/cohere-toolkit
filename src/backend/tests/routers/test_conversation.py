import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.config.deployments import ModelDeploymentName
from backend.database_models import Citation, Conversation, Document, File, Message
from backend.tests.factories import get_factory


# CONVERSATIONS
def test_list_conversations_empty(session_client: TestClient) -> None:
    response = session_client.get("/v1/conversations", headers={"User-Id": "123"})
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 0


def test_list_conversations(session_client: TestClient, session: Session) -> None:
    conversation = get_factory("Conversation", session).create()
    response = session_client.get(
        "/v1/conversations", headers={"User-Id": conversation.user_id}
    )
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 1


def test_list_conversations_with_agent(
    session_client: TestClient, session: Session
) -> None:
    agent = get_factory("Agent", session).create(
        id="agent_id", name="test agent", user_id="123"
    )
    conversation1 = get_factory("Conversation", session).create(
        agent_id="agent_id", user_id="123"
    )
    _ = get_factory("Conversation", session).create(user_id="123")

    response = session_client.get(
        "/v1/conversations", headers={"User-Id": "123"}, params={"agent_id": "agent_id"}
    )
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 1

    conversation = results[0]
    assert conversation["id"] == conversation1.id


def test_list_conversation_with_deleted_agent(
    session_client: TestClient, session: Session
) -> None:
    agent = get_factory("Agent", session).create(
        id="agent_id", name="test agent", user_id="123"
    )
    conversation = get_factory("Conversation", session).create(
        agent_id="agent_id", user_id="123"
    )

    response = session_client.get(
        "/v1/conversations", headers={"User-Id": "123"}, params={"agent_id": "agent_id"}
    )
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 1
    assert results[0]["id"] == conversation.id

    # Delete agent and check that conversation is also deleted
    response = session_client.delete(
        f"/v1/agents/{agent.id}", headers={"User-Id": "123"}
    )
    assert response.status_code == 200

    response = session_client.get(
        "/v1/conversations", headers={"User-Id": "123"}, params={"agent_id": "agent_id"}
    )
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 0


def test_list_conversations_missing_user_id(
    session_client: TestClient, session: Session
) -> None:
    _ = get_factory("Conversation", session).create()
    response = session_client.get("/v1/conversations")
    results = response.json()

    assert response.status_code == 401
    assert results == {"detail": "User-Id required in request headers."}


def test_get_conversation(session_client: TestClient, session: Session) -> None:
    conversation = get_factory("Conversation", session).create()
    response = session_client.get(
        f"/v1/conversations/{conversation.id}",
        headers={"User-Id": conversation.user_id},
    )
    response_conversation = response.json()

    assert response.status_code == 200
    assert response_conversation["id"] == conversation.id
    assert response_conversation["title"] == conversation.title


def test_get_conversation_lists_message_files(
    session_client: TestClient, session: Session
) -> None:
    user = get_factory("User", session).create()
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    message = get_factory("Message", session).create(
        conversation_id=conversation.id,
        user_id=user.id,
        position=0,
        is_active=True,
        text="hello",
    )
    file = get_factory("File", session).create(
        conversation_id=conversation.id, user_id=user.id, message_id=message.id
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
    session_client: TestClient, session: Session
) -> None:
    response = session_client.get("/v1/conversations/123", headers={"User-Id": "123"})

    assert response.status_code == 404
    assert response.json() == {"detail": f"Conversation with ID: 123 not found."}


def test_update_conversation_title(
    session_client: TestClient, session: Session
) -> None:
    conversation = get_factory("Conversation", session).create(title="test title")
    response = session_client.put(
        f"/v1/conversations/{conversation.id}",
        json={"title": "new title"},
        headers={"User-Id": conversation.user_id},
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
    session_client: TestClient, session: Session
) -> None:
    conversation = get_factory("Conversation", session).create(
        description="test description"
    )
    response = session_client.put(
        f"/v1/conversations/{conversation.id}",
        json={"description": "new description"},
        headers={"User-Id": conversation.user_id},
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
    session_client: TestClient, session: Session
) -> None:
    response = session_client.put(
        "/v1/conversations/123", json={"title": "new title"}, headers={"User-Id": "123"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"Conversation with ID: 123 not found."}


def test_update_conversations_missing_user_id(
    session_client: TestClient, session: Session
) -> None:
    conversation = get_factory("Conversation", session).create()
    response = session_client.get("/v1/conversations")
    results = response.json()

    assert response.status_code == 401
    assert results == {"detail": "User-Id required in request headers."}


def test_delete_conversation(session_client: TestClient, session: Session) -> None:
    conversation = get_factory("Conversation", session).create(title="test title")
    response = session_client.delete(
        f"/v1/conversations/{conversation.id}",
        headers={"User-Id": conversation.user_id},
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
    session_client: TestClient, session: Session
) -> None:
    response = session_client.delete(
        "/v1/conversations/123", headers={"User-Id": "123"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"Conversation with ID: 123 not found."}


def test_delete_conversation_with_files(
    session_client: TestClient, session: Session
) -> None:
    conversation = get_factory("Conversation", session).create(title="test title")
    _ = get_factory("File", session).create(
        file_name="test_file.txt",
        conversation_id=conversation.id,
        user_id=conversation.user_id,
    )

    response = session_client.delete(
        f"/v1/conversations/{conversation.id}",
        headers={"User-Id": conversation.user_id},
    )

    assert response.status_code == 200
    assert response.json() == {}

    # Check if the files were deleted
    file = session.query(File).filter(File.conversation_id == conversation.id).first()
    assert file is None

    # Check if the conversation was deleted
    conversation = (
        session.query(Conversation)
        .filter_by(id=conversation.id, user_id=conversation.user_id)
        .first()
    )
    assert conversation is None


def test_delete_conversation_with_messages(
    session_client: TestClient, session: Session
) -> None:
    conversation = get_factory("Conversation", session).create(title="test title")
    _ = get_factory("Message", session).create(
        text="test message",
        conversation_id=conversation.id,
        user_id=conversation.user_id,
    )

    response = session_client.delete(
        f"/v1/conversations/{conversation.id}",
        headers={"User-Id": conversation.user_id},
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


def test_delete_conversation_with_children_cascades_delete(
    session_client: TestClient, session: Session
) -> None:
    conversation = get_factory("Conversation", session).create(title="test title")
    _ = get_factory("File", session).create(
        file_name="test_file.txt",
        conversation_id=conversation.id,
        user_id=conversation.user_id,
    )
    message = get_factory("Message", session).create(
        text="test message",
        conversation_id=conversation.id,
        user_id=conversation.user_id,
    )
    message_id = message.id
    _ = get_factory("Citation", session).create(
        message_id=message.id, user_id=conversation.user_id
    )
    _ = get_factory("Document", session).create(
        conversation_id=conversation.id,
        message_id=message.id,
        user_id=conversation.user_id,
    )

    response = session_client.delete(
        f"/v1/conversations/{conversation.id}",
        headers={"User-Id": conversation.user_id},
    )

    assert response.status_code == 200
    assert response.json() == {}

    # Check if the files were deleted
    db_files = (
        session.query(File)
        .filter(
            File.conversation_id == conversation.id,
            File.user_id == conversation.user_id,
        )
        .all()
    )
    assert not db_files

    # Check all children deleted
    messages = (
        session.query(Message)
        .filter(
            Message.conversation_id == conversation.id,
            Message.user_id == conversation.user_id,
        )
        .all()
    )
    citations = (
        session.query(Citation)
        .filter(
            Citation.message_id == message_id, Citation.user_id == conversation.user_id
        )
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
            Conversation.id == conversation.id,
            Conversation.user_id == conversation.user_id,
        )
        .first()
    )
    assert conversation is None


def test_delete_conversation_missing_user_id(
    session_client: TestClient, session: Session
) -> None:
    conversation = get_factory("Conversation", session).create(title="test title")
    response = session_client.delete(f"/v1/conversations/{conversation.id}")

    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


def test_search_conversations(session_client: TestClient, session: Session) -> None:
    conversation = get_factory("Conversation", session).create(title="test title")
    response = session_client.get(
        "/v1/conversations:search",
        headers={"User-Id": conversation.user_id},
        params={"query": "test"},
    )
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 1
    assert results[0]["id"] == conversation.id


@pytest.mark.skipif(
    os.environ.get("COHERE_API_KEY") is None,
    reason="Cohere API key not set, skipping test",
)
def test_search_conversations_with_reranking(
    session_client: TestClient, session: Session
) -> None:
    conversation1 = get_factory("Conversation", session).create(
        title="Roses are red, violets are blue", text_messages=[]
    )
    conversation2 = get_factory("Conversation", session).create(
        title="There are are seven colors in the rainbow",
        text_messages=[],
        user_id=conversation1.user_id,
    )
    response = session_client.get(
        "/v1/conversations:search",
        headers={
            "User-Id": conversation1.user_id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
        params={"query": "color"},
    )
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 2


def test_search_conversations_missing_user_id(
    session_client: TestClient, session: Session
) -> None:
    conversation = get_factory("Conversation", session).create(title="test title")
    response = session_client.get("/v1/conversations:search", params={"query": "test"})
    results = response.json()

    assert response.status_code == 401
    assert results == {"detail": "User-Id required in request headers."}


def test_search_conversations_no_conversations(
    session_client: TestClient, session: Session
) -> None:
    _ = get_factory("Conversation", session).create(title="test title", user_id="1")
    response = session_client.get(
        "/v1/conversations:search", headers={"User-Id": "123"}, params={"query": "test"}
    )

    assert response.status_code == 200
    assert response.json() == []


# FILES
def test_list_files(session_client: TestClient, session: Session) -> None:
    conversation = get_factory("Conversation", session).create()
    file = get_factory("File", session).create(
        file_name="test_file.txt",
        conversation_id=conversation.id,
        user_id=conversation.user_id,
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


def test_list_files_no_files(session_client: TestClient, session: Session) -> None:
    conversation = get_factory("Conversation", session).create()
    response = session_client.get(
        f"/v1/conversations/{conversation.id}/files",
        headers={"User-Id": conversation.user_id},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_list_files_missing_user_id(
    session_client: TestClient, session: Session
) -> None:
    conversation = get_factory("Conversation", session).create()
    response = session_client.get(f"/v1/conversations/{conversation.id}/files")

    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


def test_upload_file_existing_conversation(
    session_client: TestClient, session: Session
) -> None:
    file_path = "src/backend/tests/test_data/Mariana_Trench.pdf"
    saved_file_path = "src/backend/data/Mariana_Trench.pdf"
    conversation = get_factory("Conversation", session).create()
    file_doc = {"file": open(file_path, "rb")}

    response = session_client.post(
        "/v1/conversations/upload_file",
        headers={"User-Id": conversation.user_id},
        files=file_doc,
        data={"conversation_id": conversation.id},
    )

    file = response.json()

    assert response.status_code == 200
    assert "Mariana_Trench" in file["file_name"]
    assert file["conversation_id"] == conversation.id
    assert file["user_id"] == conversation.user_id

    # File should not exist in the directory
    assert not os.path.exists(saved_file_path)


def test_upload_file_nonexistent_conversation_creates_new_conversation(
    session_client: TestClient, session: Session
) -> None:
    file_path = "src/backend/tests/test_data/Mariana_Trench.pdf"
    saved_file_path = "src/backend/data/Mariana_Trench.pdf"
    file_doc = {"file": open(file_path, "rb")}

    response = session_client.post(
        "/v1/conversations/upload_file", files=file_doc, headers={"User-Id": "testuser"}
    )

    file = response.json()

    created_conversation = (
        session.query(Conversation).filter_by(id=file["conversation_id"]).first()
    )

    assert response.status_code == 200
    assert created_conversation is not None
    assert created_conversation.user_id == "testuser"
    assert file["conversation_id"] == created_conversation.id
    assert "Mariana_Trench" in file["file_name"]
    assert file["conversation_id"] == created_conversation.id

    # File should not exist in the directory
    assert not os.path.exists(saved_file_path)


def test_upload_file_nonexistent_conversation_fails_if_user_id_not_provided(
    session_client: TestClient, session: Session
) -> None:
    file_path = "src/backend/tests/test_data/Mariana_Trench.pdf"
    file_doc = {"file": open(file_path, "rb")}

    response = session_client.post("/v1/conversations/upload_file", files=file_doc)

    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


def test_update_file_name(session_client: TestClient, session: Session) -> None:
    conversation = get_factory("Conversation", session).create()
    file = get_factory("File", session).create(
        file_name="test_file.txt",
        conversation_id=conversation.id,
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
    session_client: TestClient, session: Session
) -> None:
    conversation = get_factory("Conversation", session).create()
    response = session_client.put(
        f"/v1/conversations/{conversation.id}/files/123",
        json={"file_name": "new name"},
        headers={"User-Id": conversation.user_id},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"File with ID: 123 not found."}


def test_fail_update_nonexistent_conversation(
    session_client: TestClient, session: Session
) -> None:
    response = session_client.put(
        f"/v1/conversations/123/files/123",
        json={"file_name": "new name"},
        headers={"User-Id": "testuser"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"Conversation with ID: 123 not found."}


def test_fail_update_file_missing_user_id(
    session_client: TestClient, session: Session
) -> None:
    conversation = get_factory("Conversation", session).create()
    file = get_factory("File", session).create(
        file_name="test_file.txt",
        conversation_id=conversation.id,
        user_id=conversation.user_id,
    )

    response = session_client.put(
        f"/v1/conversations/{conversation.id}/files/{file.id}",
        json={"file_name": "new name"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


def test_delete_file(session_client: TestClient, session: Session) -> None:
    conversation = get_factory("Conversation", session).create()
    file = get_factory("File", session).create(
        file_name="test_file.txt",
        conversation_id=conversation.id,
        user_id=conversation.user_id,
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
        .filter(File.id == file.id, File.user_id == file.user_id)
        .first()
    )
    assert db_file is None


def test_fail_delete_nonexistent_file(
    session_client: TestClient, session: Session
) -> None:
    conversation = get_factory("Conversation", session).create()
    response = session_client.delete(
        f"/v1/conversations/{conversation.id}/files/123",
        headers={"User-Id": conversation.user_id},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"File with ID: 123 not found."}


def test_fail_delete_file_missing_user_id(
    session_client: TestClient, session: Session
) -> None:
    conversation = get_factory("Conversation", session).create()
    file = get_factory("File", session).create(
        file_name="test_file.txt",
        conversation_id=conversation.id,
        user_id=conversation.user_id,
    )

    response = session_client.delete(
        f"/v1/conversations/{conversation.id}/files/{file.id}"
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


# MISC
def test_generate_title(session_client: TestClient, session: Session) -> None:
    conversation = get_factory("Conversation", session).create()
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
    session_client: TestClient, session: Session
) -> None:
    conversation = get_factory("Conversation", session).create()
    response = session_client.post(
        f"/v1/conversations/{conversation.id}/generate-title"
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


def test_fail_generate_title_nonexistent_conversation(
    session_client: TestClient, session: Session
) -> None:
    response = session_client.post(
        "/v1/conversations/123/generate-title", headers={"User-Id": "123"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": f"Conversation with ID: 123 not found."}
