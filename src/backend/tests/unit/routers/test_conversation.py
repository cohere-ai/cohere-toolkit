from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.database_models import (
    Citation,
    Conversation,
    ConversationFileAssociation,
    Document,
    File,
    Message,
)
from backend.schemas.user import User
from backend.services.file import MAX_FILE_SIZE, MAX_TOTAL_FILE_SIZE, get_file_service
from backend.tests.unit.factories import get_factory


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
        title="test title", user_id=user.id, id="conversation_id"
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
        .filter_by(id="conversation_id", user_id=user.id)
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
        title="test title", user_id=user.id, id="conversation_id"
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
        .filter_by(id="conversation_id", user_id=user.id)
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


# FILES
def test_list_files(
    session_client: TestClient, session: Session, user: User, mock_compass_settings
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    files = [
        (
            "files",
            (
                "Mariana_Trench.pdf",
                open("src/backend/tests/unit/test_data/Mariana_Trench.pdf", "rb"),
            ),
        )
    ]
    response = session_client.post(
        "/v1/conversations/batch_upload_file",
        headers={"User-Id": conversation.user_id},
        files=files,
        data={"conversation_id": conversation.id},
    )
    assert response.status_code == 200
    files = response.json()
    uploaded_file = files[0]

    response = session_client.get(
        f"/v1/conversations/{conversation.id}/files",
        headers={"User-Id": conversation.user_id},
    )

    assert response.status_code == 200
    response = response.json()
    assert len(response) == 1
    response_file = response[0]
    assert response_file["id"] == uploaded_file["id"]
    assert response_file["file_name"] == uploaded_file["file_name"]


def test_list_files_no_files(
    session_client: TestClient, session: Session, user: User, mock_compass_settings
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    response = session_client.get(
        f"/v1/conversations/{conversation.id}/files",
        headers={"User-Id": conversation.user_id},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_list_files_missing_user_id(
    session_client: TestClient, session: Session, user: User, mock_compass_settings
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    response = session_client.get(f"/v1/conversations/{conversation.id}/files")

    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


def test_upload_file_existing_conversation(
    session_client: TestClient, session: Session, user: User, mock_compass_settings
) -> None:
    file_path = "src/backend/tests/unit/test_data/Mariana_Trench.pdf"
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    file_doc = {"file": open(file_path, "rb")}

    response = session_client.post(
        "/v1/conversations/upload_file",
        headers={"User-Id": conversation.user_id},
        files=file_doc,
        data={"conversation_id": conversation.id},
    )

    file = response.json()
    assert response.status_code == 200
    files = get_file_service().get_files_by_conversation_id(
        session, conversation.user_id, conversation.id, MagicMock()
    )
    assert len(files) == 1
    assert "Mariana_Trench" in file["file_name"]
    assert conversation.file_ids == [file["id"]]


def test_upload_file_nonexistent_conversation_creates_new_conversation(
    session_client: TestClient, session: Session, user: User, mock_compass_settings
) -> None:
    file_path = "src/backend/tests/unit/test_data/Mariana_Trench.pdf"
    file_doc = {"file": open(file_path, "rb")}

    response = session_client.post(
        "/v1/conversations/upload_file", files=file_doc, headers={"User-Id": user.id}
    )
    assert response.status_code == 200

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

    files = get_file_service().get_files_by_conversation_id(
        session, created_conversation.user_id, created_conversation.id, MagicMock()
    )
    assert len(files) == 1
    assert "Mariana_Trench" in file["file_name"]
    assert created_conversation.file_ids == [file["id"]]
    assert created_conversation is not None
    assert created_conversation.user_id == user.id
    assert conversation_file_association is not None


def test_upload_file_nonexistent_conversation_fails_if_user_id_not_provided(
    session_client: TestClient, session: Session, user: User, mock_compass_settings
) -> None:
    file_path = "src/backend/tests/unit/test_data/Mariana_Trench.pdf"
    file_doc = {"file": open(file_path, "rb")}

    response = session_client.post("/v1/conversations/upload_file", files=file_doc)

    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


def test_batch_upload_file_existing_conversation(
    session_client: TestClient, session: Session, user, mock_compass_settings
) -> None:
    file_paths = {
        "Mariana_Trench.pdf": "src/backend/tests/unit/test_data/Mariana_Trench.pdf",
        "Cardistry.pdf": "src/backend/tests/unit/test_data/Cardistry.pdf",
    }
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

    files_stored = get_file_service().get_files_by_conversation_id(
        session, conversation.user_id, conversation.id, MagicMock()
    )
    assert len(files_stored) == len(file_paths)


def test_batch_upload_total_files_exceeds_limit(
    session_client: TestClient, session: Session, user, mock_compass_settings
) -> None:
    _ = get_factory("Conversation", session).create(user_id=user.id)
    file_paths = {
        "Mariana_Trench.pdf": "src/backend/tests/unit/test_data/Mariana_Trench.pdf",
        "Cardistry.pdf": "src/backend/tests/unit/test_data/Cardistry.pdf",
        "Tapas.pdf": "src/backend/tests/unit/test_data/Tapas.pdf",
        "Mount_Everest.pdf": "src/backend/tests/unit/test_data/Mount_Everest.pdf",
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
    session_client: TestClient, session: Session, user, mock_compass_settings
) -> None:
    _ = get_factory("Conversation", session).create(user_id=user.id)
    file_paths = {
        "Mariana_Trench.pdf": "src/backend/tests/unit/test_data/Mariana_Trench.pdf",
        "Cardistry.pdf": "src/backend/tests/unit/test_data/Cardistry.pdf",
        "26mb.pdf": "src/backend/tests/unit/test_data/26mb.pdf",
        "Tapas.pdf": "src/backend/tests/unit/test_data/Tapas.pdf",
        "Mount_Everest.pdf": "src/backend/tests/unit/test_data/Mount_Everest.pdf",
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
    session_client: TestClient, session: Session, user, mock_compass_settings
) -> None:
    file_paths = {
        "Mariana_Trench.pdf": "src/backend/tests/unit/test_data/Mariana_Trench.pdf",
        "Cardistry.pdf": "src/backend/tests/unit/test_data/Cardistry.pdf",
        "Tapas.pdf": "src/backend/tests/unit/test_data/Tapas.pdf",
        "Mount_Everest.pdf": "src/backend/tests/unit/test_data/Mount_Everest.pdf",
    }
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

    files_stored = get_file_service().get_files_by_conversation_id(
        session, created_conversation.user_id, created_conversation.id, MagicMock()
    )
    assert len(files_stored) == len(file_paths)


def test_batch_upload_file_nonexistent_conversation_fails_if_user_id_not_provided(
    session_client: TestClient, session: Session, user: User, mock_compass_settings
) -> None:
    file_paths = {
        "Mariana_Trench.pdf": "src/backend/tests/unit/test_data/Mariana_Trench.pdf",
        "Cardistry.pdf": "src/backend/tests/unit/test_data/Cardistry.pdf",
        "Tapas.pdf": "src/backend/tests/unit/test_data/Tapas.pdf",
        "Mount_Everest.pdf": "src/backend/tests/unit/test_data/Mount_Everest.pdf",
    }
    files = [
        ("files", (file_name, open(file_path, "rb")))
        for file_name, file_path in file_paths.items()
    ]

    response = session_client.post("/v1/conversations/upload_file", files=files)

    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


def test_delete_file(
    session_client: TestClient,
    session: Session,
    user: User,
    mock_compass_settings,
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    files = [
        (
            "files",
            (
                "Mariana_Trench.pdf",
                open("src/backend/tests/unit/test_data/Mariana_Trench.pdf", "rb"),
            ),
        )
    ]

    response = session_client.post(
        "/v1/conversations/batch_upload_file",
        headers={"User-Id": conversation.user_id},
        files=files,
        data={"conversation_id": conversation.id},
    )
    assert response.status_code == 200
    files = response.json()
    uploaded_file = files[0]

    response = session_client.delete(
        f"/v1/conversations/{conversation.id}/files/{uploaded_file['id']}",
        headers={"User-Id": conversation.user_id},
    )
    assert response.status_code == 200
    assert response.json() == {}

    # Check if File
    files = get_file_service().get_files_by_conversation_id(
        session, conversation.user_id, conversation.id, MagicMock()
    )
    assert files == []

    conversation_file_association = (
        session.query(ConversationFileAssociation)
        .filter(File.id == uploaded_file["id"], File.user_id == user.id)
        .first()
    )
    assert conversation_file_association is None

    conversation = (
        session.query(Conversation).filter(Conversation.id == conversation.id).first()
    )
    assert conversation.file_ids == []


def test_fail_delete_nonexistent_file(
    session_client: TestClient, session: Session, user: User, mock_compass_settings
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    response = session_client.delete(
        f"/v1/conversations/{conversation.id}/files/123",
        headers={"User-Id": conversation.user_id},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"File with ID: 123 not found."}


def test_fail_delete_file_missing_user_id(
    session_client: TestClient, session: Session, user: User, mock_compass_settings
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
