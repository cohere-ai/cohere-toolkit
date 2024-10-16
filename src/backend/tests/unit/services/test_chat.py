import datetime
from typing import Any
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import Request

from backend.chat.collate import to_dict
from backend.chat.enums import StreamEvent
from backend.crud import document as document_crud
from backend.crud import message as message_crud
from backend.crud import tool_call as tool_call_crud
from backend.database_models.conversation import Conversation
from backend.database_models.database import DBSessionDep
from backend.database_models.document import Document
from backend.database_models.message import Message, MessageAgent
from backend.database_models.tool_call import ToolCall
from backend.database_models.user import User
from backend.schemas.chat import BaseChatRequest, EventState
from backend.schemas.context import Context
from backend.services.chat import (
    DEATHLOOP_SIMILARITY_THRESHOLDS,
    are_previous_actions_similar,
    check_death_loop,
    check_similarity,
    create_chat_history,
    handle_stream_search_results,
    process_preamble,
    should_take_last_message,
)
from backend.tests.unit.factories import get_factory
from backend.tools.google_drive.tool import GOOGLE_DRIVE_TOOL_ID


@pytest.fixture(autouse=True)
def conversation(session: DBSessionDep, user: User) -> Conversation:
    return get_factory("Conversation", session).create(id="1", user_id=user.id)


def test_should_take_last_message_previous_message(
    session: DBSessionDep, user: User, conversation: Conversation
) -> None:
    message = get_factory("Message", session).create(
        text="plan", conversation_id=conversation.id, user_id=user.id
    )
    message_crud.create_message(session, message)
    chat_request = BaseChatRequest(message="hello")
    actual = should_take_last_message(chat_request, conversation)
    assert not actual


def test_should_take_last_message_no_conversation(
    session: DBSessionDep, user: User, conversation: Conversation
) -> None:
    chat_request = BaseChatRequest()
    actual = should_take_last_message(chat_request, conversation)
    assert not actual


def test_should_take_last_message_has_tool_calls(
    session: DBSessionDep, user: User, conversation: Conversation
) -> None:
    message = get_factory("Message", session).create(
        conversation_id=conversation.id, user_id=user.id
    )
    message_crud.create_message(session, message)
    tool_call = get_factory("ToolCall", session).create(
        name="toolkit_calculator",
        message_id=message.id,
        parameters={"expression": "1+1"},
    )
    tool_call_crud.create_tool_call(session, tool_call)
    chat_request = BaseChatRequest()
    actual = should_take_last_message(chat_request, conversation)
    assert not actual


def test_should_take_last_message_has_documents(
    session: DBSessionDep, user: User, conversation: Conversation
) -> None:
    message = get_factory("Message", session).create(
        conversation_id=conversation.id, user_id=user.id
    )
    message_crud.create_message(session, message)
    document = get_factory("Document", session).create(
        id="1",
        conversation_id=conversation.id,
        message_id=message.id,
        user_id=user.id,
        document_id="hello",
    )
    document_crud.create_document(session, document)
    chat_request = BaseChatRequest()
    actual = should_take_last_message(chat_request, conversation)
    assert not actual


def test_should_take_last_message_no_last_message(
    session: DBSessionDep, user: User, conversation: Conversation
) -> None:
    message = get_factory("Message", session).create(
        text="", conversation_id=conversation.id, user_id=user.id
    )
    message_crud.create_message(session, message)
    chat_request = BaseChatRequest()
    actual = should_take_last_message(chat_request, conversation)
    assert not actual


def test_should_take_last_message_true(
    session: DBSessionDep, user: User, conversation: Conversation
) -> None:
    message = get_factory("Message", session).create(
        text="test", conversation_id=conversation.id, user_id=user.id
    )
    message_crud.create_message(session, message)
    chat_request = BaseChatRequest()
    actual = should_take_last_message(chat_request, conversation)
    assert actual


def test_process_preamble_no_date() -> None:
    preamble = "This is a test preamble."
    request = Mock(spec=Request)
    request.headers.get.return_value = None
    result = process_preamble(preamble, request)
    request.headers.get.assert_called_with("X-Date")
    assert result == preamble


def test_process_preamble_with_date() -> None:
    preamble = "This is a test preamble."
    request = Mock(spec=Request)
    request.headers.get.return_value = "Friday, September 13, 2024 at 12:29:22"
    result = process_preamble(preamble, request)
    request.headers.get.assert_called_with("X-Date")
    assert (
        result
        == "This is a test preamble. The current date and time is Friday, September 13, 2024 at 12:29:22."
    )


def test_process_preamble_no_preamble_with_date() -> None:
    request = Mock(spec=Request)
    request.headers.get.return_value = "Friday, September 13, 2024 at 12:29:22"
    result = process_preamble("", request)
    request.headers.get.assert_called_with("X-Date")
    assert (
        result
        == """## Task And Context
Your name is North! You are an internal knowledge assistant for the company Cohere. \
You use your advanced complex reasoning capabilities to help people by answering their questions and other requests interactively. \
You will be asked a very wide array of requests on all kinds of topics. \
You will be equipped with a wide range of search engines or similar tools to help you, which you use to research your answer. \
You may need to use multiple tools in parallel or sequentially to complete your task. \
You should focus on serving the user's needs as best you can, which will be wide-ranging. \
You are an expert on every company topic. Explain your reasoning step by step. Add nuance to your answer, by taking a step back: how confident are you about the answer? \
Any caveats? Does it seem weird or against common sense? \
The current date and time is Friday, September 13, 2024 at 12:29:22.

## Style Guide
Unless the user asks for a different style of answer, you should answer in full sentences, using proper grammar and spelling"""
    )


def test_process_preamble_no_preamble_no_date() -> None:
    request = Mock(spec=Request)
    request.headers.get.return_value = None
    result = process_preamble("", request)
    request.headers.get.assert_called_with("X-Date")
    assert (
        result
        == """## Task And Context
Your name is North! You are an internal knowledge assistant for the company Cohere. \
You use your advanced complex reasoning capabilities to help people by answering their questions and other requests interactively. \
You will be asked a very wide array of requests on all kinds of topics. \
You will be equipped with a wide range of search engines or similar tools to help you, which you use to research your answer. \
You may need to use multiple tools in parallel or sequentially to complete your task. \
You should focus on serving the user's needs as best you can, which will be wide-ranging. \
You are an expert on every company topic. Explain your reasoning step by step. Add nuance to your answer, by taking a step back: how confident are you about the answer? \
Any caveats? Does it seem weird or against common sense? \


## Style Guide
Unless the user asks for a different style of answer, you should answer in full sentences, using proper grammar and spelling"""
    )


def test_create_chat_history_with_tool_results() -> None:
    conversation = Conversation(
        id=str(uuid4()),
        user_id="user-id",
        text_messages=[],
        agent_id="agent-id",
    )
    tool_call_message = Message(
        position=0,
        text="test message text tool call",
        documents=[],
        citations=[],
        tool_calls=[],
        tool_plan=None,
        created_at=datetime.datetime.now(),
        agent=MessageAgent.CHATBOT,
    )
    tool_call = ToolCall(
        name=GOOGLE_DRIVE_TOOL_ID,
        parameters={"query": "test query"},
        message_id=tool_call_message.id,
    )

    tool_call_message.tool_calls.append(tool_call)
    conversation.text_messages.append(tool_call_message)

    tool_results_message = Message(
        position=0,
        text="test message text tool result",
        documents=[],
        citations=[],
        tool_calls=[],
        tool_plan=None,
        created_at=datetime.datetime.now(),
        agent=MessageAgent.CHATBOT,
    )
    document = Document(
        text="test document text",
        title="test document title",
        url="http://example.com",
        fields={},
        tool_name=GOOGLE_DRIVE_TOOL_ID,
        document_id="doc_0",
        did_user_have_access=True,
    )
    tool_results_message.documents.append(document)
    conversation.text_messages.append(tool_results_message)

    chat_request = BaseChatRequest(
        conversation_id=conversation.id,
    )

    chat_history = create_chat_history(conversation, 1, chat_request)

    expected_chat_history = [
        {
            "role": MessageAgent.CHATBOT,
            "message": tool_call_message.text,
            "tool_calls": [
                {"name": GOOGLE_DRIVE_TOOL_ID, "parameters": {"query": "test query"}}
            ],
            "tool_plan": None,
            "tool_results": None,
        },
        {
            "role": "TOOL",
            "tool_results": [
                {
                    "call": {
                        "name": GOOGLE_DRIVE_TOOL_ID,
                        "parameters": {"query": "test query"},
                    },
                    "outputs": [
                        {
                            "text": "test document text",
                            "document_id": "doc_0",
                            "title": "test document title",
                            "url": "http://example.com",
                            "fields": {},
                            "tool_name": GOOGLE_DRIVE_TOOL_ID,
                        }
                    ],
                }
            ],
            "message": None,
            "tool_plan": None,
            "tool_calls": None,
        },
        {
            "role": MessageAgent.CHATBOT,
            "message": tool_results_message.text,
            "tool_plan": None,
            "tool_results": None,
            "tool_calls": [],
        },
    ]

    assert to_dict(chat_history) == to_dict(expected_chat_history)


def test_create_chat_history_with_two_tool_results() -> None:
    conversation = Conversation(
        id=str(uuid4()),
        user_id="user-id",
        text_messages=[],
        agent_id="agent-id",
    )
    tool_call_message = Message(
        position=0,
        text="test message text tool call",
        documents=[],
        citations=[],
        tool_calls=[],
        tool_plan=None,
        created_at=datetime.datetime.now(),
        agent=MessageAgent.CHATBOT,
    )
    tool_call = ToolCall(
        name=GOOGLE_DRIVE_TOOL_ID,
        parameters={"query": "test query"},
        message_id=tool_call_message.id,
    )

    tool_call_message.tool_calls.append(tool_call)
    conversation.text_messages.append(tool_call_message)

    tool_results_message = Message(
        position=0,
        text="test message text tool result",
        documents=[],
        citations=[],
        tool_calls=[],
        tool_plan=None,
        created_at=datetime.datetime.now(),
        agent=MessageAgent.CHATBOT,
    )
    document = Document(
        text="test document text",
        title="test document title",
        url="http://example.com",
        fields={},
        tool_name=GOOGLE_DRIVE_TOOL_ID,
        document_id="doc_0",
        did_user_have_access=True,
    )
    tool_results_message.documents.append(document)

    document_2 = Document(
        text="test document text 2",
        title="test document title 2",
        url="http://example.com/2",
        fields={},
        tool_name=GOOGLE_DRIVE_TOOL_ID,
        document_id="doc_2",
        did_user_have_access=True,
    )
    tool_results_message.documents.append(document_2)

    conversation.text_messages.append(tool_results_message)

    chat_request = BaseChatRequest(
        conversation_id=conversation.id,
    )

    chat_history = create_chat_history(conversation, 1, chat_request)

    expected_chat_history = [
        {
            "role": MessageAgent.CHATBOT,
            "message": tool_call_message.text,
            "tool_calls": [
                {"name": GOOGLE_DRIVE_TOOL_ID, "parameters": {"query": "test query"}}
            ],
            "tool_plan": None,
            "tool_results": None,
        },
        {
            "role": "TOOL",
            "tool_results": [
                {
                    "call": {
                        "name": GOOGLE_DRIVE_TOOL_ID,
                        "parameters": {"query": "test query"},
                    },
                    "outputs": [
                        {
                            "text": "test document text",
                            "document_id": "doc_0",
                            "title": "test document title",
                            "url": "http://example.com",
                            "fields": {},
                            "tool_name": GOOGLE_DRIVE_TOOL_ID,
                        },
                        {
                            "text": document_2.text,
                            "document_id": document_2.document_id,
                            "title": document_2.title,
                            "url": document_2.url,
                            "fields": {},
                            "tool_name": GOOGLE_DRIVE_TOOL_ID,
                        },
                    ],
                }
            ],
            "message": None,
            "tool_plan": None,
            "tool_calls": None,
        },
        {
            "role": MessageAgent.CHATBOT,
            "message": tool_results_message.text,
            "tool_plan": None,
            "tool_results": None,
            "tool_calls": [],
        },
    ]

    assert to_dict(chat_history) == to_dict(expected_chat_history)


def test_create_chat_history_with_tool_results_omit_missing_access_doc() -> None:
    conversation = Conversation(
        id=str(uuid4()),
        user_id="user-id",
        text_messages=[],
        agent_id="agent-id",
    )
    tool_call_message = Message(
        position=0,
        text="test message text tool call",
        documents=[],
        citations=[],
        tool_calls=[],
        tool_plan=None,
        created_at=datetime.datetime.now(),
        agent=MessageAgent.CHATBOT,
    )
    tool_call = ToolCall(
        name=GOOGLE_DRIVE_TOOL_ID,
        parameters={"query": "test query"},
        message_id=tool_call_message.id,
    )

    tool_call_message.tool_calls.append(tool_call)
    conversation.text_messages.append(tool_call_message)

    tool_results_message = Message(
        position=0,
        text="test message text tool result",
        documents=[],
        citations=[],
        tool_calls=[],
        tool_plan=None,
        created_at=datetime.datetime.now(),
        agent=MessageAgent.CHATBOT,
    )
    document = Document(
        text="test document text",
        title="test document title",
        url="http://example.com",
        fields={},
        tool_name=GOOGLE_DRIVE_TOOL_ID,
        document_id="doc_0",
        did_user_have_access=True,
    )
    tool_results_message.documents.append(document)

    missing_access_doc = Document(
        text="test document text 2",
        title="test document title 2",
        url="http://example.com/2",
        fields={},
        tool_name=GOOGLE_DRIVE_TOOL_ID,
        document_id="doc_2",
        did_user_have_access=False,
    )
    tool_results_message.documents.append(missing_access_doc)

    conversation.text_messages.append(tool_results_message)

    chat_request = BaseChatRequest(
        conversation_id=conversation.id,
    )

    chat_history = create_chat_history(conversation, 1, chat_request)

    expected_chat_history = [
        {
            "role": MessageAgent.CHATBOT,
            "message": tool_call_message.text,
            "tool_calls": [
                {"name": GOOGLE_DRIVE_TOOL_ID, "parameters": {"query": "test query"}}
            ],
            "tool_plan": None,
            "tool_results": None,
        },
        {
            "role": "TOOL",
            "tool_results": [
                {
                    "call": {
                        "name": GOOGLE_DRIVE_TOOL_ID,
                        "parameters": {"query": "test query"},
                    },
                    "outputs": [
                        {
                            "text": "test document text",
                            "document_id": "doc_0",
                            "title": "test document title",
                            "url": "http://example.com",
                            "fields": {},
                            "tool_name": GOOGLE_DRIVE_TOOL_ID,
                        }
                    ],
                }
            ],
            "message": None,
            "tool_plan": None,
            "tool_calls": None,
        },
        {
            "role": MessageAgent.CHATBOT,
            "message": tool_results_message.text,
            "tool_plan": None,
            "tool_results": None,
            "tool_calls": [],
        },
    ]

    assert to_dict(chat_history) == to_dict(expected_chat_history)


def test_create_chat_history_no_tool_results() -> None:
    conversation = Conversation(
        id=str(uuid4()),
        user_id="user-id",
        text_messages=[],
        agent_id="agent-id",
    )
    tool_call_message = Message(
        position=0,
        text="test message text tool call",
        documents=[],
        citations=[],
        tool_calls=[],
        tool_plan=None,
        created_at=datetime.datetime.now(),
        agent=MessageAgent.CHATBOT,
    )
    tool_call = ToolCall(
        name=GOOGLE_DRIVE_TOOL_ID,
        parameters={"query": "test query"},
        message_id=tool_call_message.id,
    )

    tool_call_message.tool_calls.append(tool_call)
    conversation.text_messages.append(tool_call_message)

    chat_request = BaseChatRequest(
        conversation_id=conversation.id,
    )

    chat_history = create_chat_history(conversation, 1, chat_request)

    expected_chat_history = [
        {
            "role": MessageAgent.CHATBOT,
            "message": tool_call_message.text,
            "tool_calls": [
                {"name": GOOGLE_DRIVE_TOOL_ID, "parameters": {"query": "test query"}}
            ],
            "tool_plan": None,
            "tool_results": None,
        }
    ]

    assert to_dict(chat_history) == to_dict(expected_chat_history)


def test_handle_stream_search_results_should_event_be_skipped_false_event_has_documents() -> (
    None
):
    document = {
        "id": "db doc id 0",
        "document_id": "doc_0",
        "title": "document title 0",
        "url": "http://example.com/0",
        "tool_name": GOOGLE_DRIVE_TOOL_ID,
        "did_user_have_access": True,
    }

    event = {
        "event_type": StreamEvent.SEARCH_RESULTS,
        "search_results": [],
        "documents": [document],
    }

    stream_end_data: dict[str, Any] = {
        "documents": [],
        "search_results": [],
    }
    response_message = Mock(
        Message(user_id="user_id", conversation_id="conversation_id", documents=[])
    )
    response_message.id = "response_message_id"

    document_ids_to_document: dict[str, Document] = {}
    stream_event_types: list[StreamEvent] = [
        StreamEvent.STREAM_START,
        StreamEvent.SEARCH_RESULTS,
    ]

    (
        _,
        stream_end_data,
        response_message,
        document_ids_to_document,
        should_event_be_skipped,
    ) = handle_stream_search_results(
        event,
        "",
        stream_end_data=stream_end_data,
        response_message=response_message,
        document_ids_to_document=document_ids_to_document,
        stream_event_types=stream_event_types,
    )

    assert not should_event_be_skipped


def test_handle_stream_search_results_should_event_be_skipped_false_event_not_second_event() -> (
    None
):
    event = {
        "event_type": StreamEvent.SEARCH_RESULTS,
        "search_results": [],
        "documents": [],
    }

    stream_end_data: dict[str, Any] = {
        "documents": [],
        "search_results": [],
    }
    response_message = Mock(
        Message(user_id="user_id", conversation_id="conversation_id", documents=[])
    )
    response_message.id = "response_message_id"

    document_ids_to_document: dict[str, Document] = {}
    stream_event_types: list[StreamEvent] = [
        StreamEvent.STREAM_START,
        StreamEvent.TOOL_CALLS_CHUNK,
        StreamEvent.SEARCH_RESULTS,
    ]

    (
        _,
        stream_end_data,
        response_message,
        document_ids_to_document,
        should_event_be_skipped,
    ) = handle_stream_search_results(
        event,
        "",
        stream_end_data=stream_end_data,
        response_message=response_message,
        document_ids_to_document=document_ids_to_document,
        stream_event_types=stream_event_types,
    )

    assert not should_event_be_skipped


def test_handle_stream_search_results_should_event_be_skipped_true_search_event_is_empty_and_second_event() -> (
    None
):
    event = {
        "event_type": StreamEvent.SEARCH_RESULTS,
        "search_results": [],
        "documents": [],
    }

    stream_end_data: dict[str, Any] = {
        "documents": [],
        "search_results": [],
    }
    response_message = Mock(
        Message(user_id="user_id", conversation_id="conversation_id", documents=[])
    )
    response_message.id = "response_message_id"

    document_ids_to_document: dict[str, Document] = {}
    stream_event_types: list[StreamEvent] = [
        StreamEvent.STREAM_START,
        StreamEvent.SEARCH_RESULTS,
    ]

    (
        _,
        stream_end_data,
        response_message,
        document_ids_to_document,
        should_event_be_skipped,
    ) = handle_stream_search_results(
        event,
        "",
        stream_end_data=stream_end_data,
        response_message=response_message,
        document_ids_to_document=document_ids_to_document,
        stream_event_types=stream_event_types,
    )

    assert should_event_be_skipped


def test_are_previous_actions_similar():
    distances = [
        0.5,
        0.6,
        0.8,
        0.9,
        1.0,
    ]

    assert are_previous_actions_similar(distances, 0.7, 3)


def test_are_previous_actions_not_similar():
    distances = [
        0.1,
        0.1,
        0.1,
        0.1,
    ]
    assert not are_previous_actions_similar(distances, 0.7, 3)


def test_check_similarity():
    ctx = Context()
    distances = [
        0.5,
        0.6,
        0.8,
        0.9,
        1.0,
    ]

    response = check_similarity(distances, ctx)
    assert response


def test_check_similarity_no_death_loop():
    ctx = Context()
    distances = [
        0.1,
        0.1,
        0.1,
        0.1,
    ]

    response = check_similarity(distances, ctx)
    assert not response


def test_check_similarity_not_enough_data():
    ctx = Context()
    distances = [
        0.1,
        0.1,
    ]

    response = check_similarity(distances, ctx)
    assert not response


@pytest.mark.skip(reason="We are supressing the exception while experimenting")
def test_check_death_loop_raises_on_plan():
    ctx = Context()
    event = {
        "text": "This is also a plan",
        "tool_calls": [],
    }

    event_state = EventState(
        distances_plans=[
            0.1,
            0.8,
            0.9,
        ],
        distances_actions=[
            0.1,
            0.1,
            0.1,
        ],
        previous_plan="This is a plan",
        previous_action="[]",
    )

    with pytest.raises(Exception):
        check_death_loop(event, event_state, ctx)


@pytest.mark.skip(reason="We are supressing the exception while experimenting")
def test_check_death_loop_raises_on_action():
    ctx = Context()
    event = {
        "text": "This is a plan",
        "tool_calls": [{"tool": "tool1", "args": ["This is an argument"]}],
    }

    event_state = EventState(
        distances_plans=[
            0.1,
            0.1,
            0.1,
        ],
        distances_actions=[
            0.1,
            0.8,
            0.9,
        ],
        previous_plan="Nothing like the previous plan",
        previous_action="[{'tool': 'tool1', 'args': ['This is an argument']}]",
    )

    with pytest.raises(Exception):
        check_death_loop(event, event_state, ctx)


def test_check_no_death_loop():
    ctx = Context()
    event = {
        "text": "Nothing like the previous plan",
        "tool_calls": [
            {"tool": "different_tool", "args": ["Nothing like the previous action"]}
        ],
    }

    event_state = EventState(
        distances_plans=[
            0.1,
            0.1,
            0.1,
        ],
        distances_actions=[
            0.1,
            0.1,
            0.1,
        ],
        previous_plan="This is a plan",
        previous_action='[{"tool": "tool1", "args": ["This is an argument"]}]',
    )

    new_event_state = check_death_loop(event, event_state, ctx)
    assert new_event_state.previous_plan == "Nothing like the previous plan"
    assert (
        new_event_state.previous_action
        == '[{"tool": "different_tool", "args": ["Nothing like the previous action"]}]'
    )

    assert len(new_event_state.distances_plans) == 4
    assert len(new_event_state.distances_actions) == 4

    assert new_event_state.distances_plans[-1] < max(DEATHLOOP_SIMILARITY_THRESHOLDS)
    assert new_event_state.distances_actions[-1] < max(DEATHLOOP_SIMILARITY_THRESHOLDS)
