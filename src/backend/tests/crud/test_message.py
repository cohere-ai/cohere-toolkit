import pytest

from backend.crud import citation as citation_crud
from backend.crud import document as document_crud
from backend.crud import message as message_crud
from backend.database_models.message import Message, MessageFileAssociation
from backend.schemas.message import UpdateMessage
from backend.tests.factories import get_factory


@pytest.fixture(autouse=True)
def conversation(session, user):
    return get_factory("Conversation", session).create(id="1", user_id=user.id)


def test_create_message(session, conversation, user):
    message_data = Message(
        text="Hello, World!",
        user_id=user.id,
        conversation_id=conversation.id,
        position=1,
        agent="USER",
    )

    message = message_crud.create_message(session, message_data)
    assert message.text == message_data.text
    assert message.user_id == message_data.user_id
    assert message.conversation_id == message_data.conversation_id

    message = message_crud.get_message(session, message.id, user.id)
    assert message.text == message_data.text
    assert message.user_id == message_data.user_id
    assert message.conversation_id == message_data.conversation_id


def test_get_message(session, conversation, user):
    _ = get_factory("Message", session).create(
        id="1", text="Hello, World!", conversation_id=conversation.id, user_id=user.id
    )

    message = message_crud.get_message(session, "1", user.id)
    assert message.text == "Hello, World!"
    assert message.id == "1"


def test_fail_get_nonexistent_message(session, user):
    message = message_crud.get_message(session, "123", user.id)
    assert message is None


def test_list_messages(session, conversation, user):
    _ = get_factory("Message", session).create(
        text="Hello, World!", conversation_id=conversation.id, user_id=user.id
    )

    messages = message_crud.get_messages(session, user.id)
    assert len(messages) == 1
    assert messages[0].text == "Hello, World!"


def test_list_messages_empty(session, user):
    messages = message_crud.get_messages(session, user.id)
    assert len(messages) == 0


def test_list_messages_with_pagination(session, conversation, user):
    for i in range(10):
        _ = get_factory("Message", session).create(
            text=f"Hello, World! {i}", conversation_id=conversation.id, user_id=user.id
        )

    messages = message_crud.get_messages(session, offset=5, limit=5, user_id=user.id)
    assert len(messages) == 5
    messages.sort(key=lambda x: x.text)
    for i, message in enumerate(messages):
        assert message.text == f"Hello, World! {i + 5}"


def test_list_messages_by_conversation_id(session, conversation, user):
    for i in range(10):
        _ = get_factory("Message", session).create(
            text=f"Hello, World! {i}", conversation_id=conversation.id, user_id=user.id
        )

    messages = message_crud.get_messages_by_conversation_id(session, "1", user.id)
    messages.sort(key=lambda x: x.text)
    assert len(messages) == 10

    for i, message in enumerate(messages):
        assert message.text == f"Hello, World! {i}"
        assert message.conversation_id == "1"


def test_list_messages_by_conversation_id_empty(session, conversation, user):
    messages = message_crud.get_messages_by_conversation_id(session, "1", user.id)
    assert len(messages) == 0


def test_update_message(session, conversation, user):
    message = get_factory("Message", session).create(
        text="Hello, World!", conversation_id=conversation.id, user_id=user.id
    )

    new_message_data = UpdateMessage(
        text="Hello, Universe!",
    )

    updated_message = message_crud.update_message(session, message, new_message_data)
    assert updated_message.text == new_message_data.text
    assert updated_message.conversation_id == message.conversation_id
    assert updated_message.position == message.position
    assert updated_message.agent == message.agent


def test_delete_message(session, conversation, user):
    message = get_factory("Message", session).create(
        text="Hello, World!", conversation_id=conversation.id, user_id=user.id
    )

    message_crud.delete_message(session, message.id, user.id)

    message = message_crud.get_message(session, message.id, user.id)
    assert message is None


def test_delete_message_cascade(session, conversation, user):
    message = get_factory("Message", session).create(
        text="Hello, World!", conversation_id=conversation.id, user_id=user.id
    )
    citation = get_factory("Citation", session).create(
        message_id=message.id, user_id=user.id
    )
    citation_id = citation.id
    document = get_factory("Document", session).create(
        message_id=message.id, conversation_id=conversation.id, user_id=user.id
    )
    document_id = document.id
    message_crud.delete_message(session, message.id, user.id)

    message = message_crud.get_message(session, message.id, user.id)
    assert message is None
    assert message_crud.get_messages(session, user.id) == []
    assert (
        message_crud.get_messages_by_conversation_id(session, conversation.id, user.id)
        == []
    )

    citation = citation_crud.get_citation(session, citation_id)
    assert citation is None
    assert citation_crud.get_citations(session) == []

    document = document_crud.get_document(session, document_id)
    assert document is None
    assert document_crud.get_documents(session) == []


def test_create_message_file_association(session, conversation, user):
    message = get_factory("Message", session).create(
        text="Hello, World!", conversation_id=conversation.id, user_id=user.id
    )
    file = get_factory("File", session).create(user_id=user.id)

    message_file_association = message_crud.create_message_file_association(
        session,
        MessageFileAssociation(message_id=message.id, file_id=file.id, user_id=user.id),
    )
    assert message_file_association.message_id == message.id
    assert message_file_association.file_id == file.id
    assert message_file_association.user_id == user.id

    message = message_crud.get_message(session, message.id, user.id)
    assert message.file_ids == [file.id]


def test_get_message_file_association_by_file_id(session, conversation, user):
    message = get_factory("Message", session).create(
        text="Hello, World!", conversation_id=conversation.id, user_id=user.id
    )
    file = get_factory("File", session).create(user_id=user.id)
    _ = get_factory("MessageFileAssociation", session).create(
        message_id=message.id, file_id=file.id, user_id=user.id
    )

    message_file_association = message_crud.get_message_file_association_by_file_id(
        session, file.id, user.id
    )
    assert message_file_association.message_id == message.id
    assert message_file_association.file_id == file.id
    assert message_file_association.user_id == user.id


def test_delete_message_file_association(session, conversation, user):
    message = get_factory("Message", session).create(
        text="Hello, World!", conversation_id=conversation.id, user_id=user.id
    )
    file = get_factory("File", session).create(user_id=user.id)
    _ = get_factory("MessageFileAssociation", session).create(
        message_id=message.id, file_id=file.id, user_id=user.id
    )

    message_crud.delete_message_file_association(session, message.id, file.id, user.id)

    message_file_association = message_crud.get_message_file_association_by_file_id(
        session, file.id, user.id
    )
    assert message_file_association is None

    message = message_crud.get_message(session, message.id, user.id)
    assert message.file_ids == []
