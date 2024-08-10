from fastapi import APIRouter, Depends

from backend.chat.collate import to_dict
from backend.config.routers import RouterName
from backend.crud import citation as citation_crud
from backend.crud import document as document_crud
from backend.crud import message as message_crud
from backend.crud import tool_call as tool_call_crud
from backend.crud.message import delete_messages_after_message, get_message
from backend.database_models.database import DBSessionDep
from backend.database_models.tool_call import ToolCall as ToolCallModel
from backend.schemas.context import Context
from backend.schemas.message import UpdateMessage, UpdateMessageResponse
from backend.services.context import get_context

router = APIRouter(prefix="/v1/messages")
router.name = RouterName.MESSAGE


@router.post("/{message_id}", response_model=UpdateMessageResponse)
async def update_message(
    message_id: str,
    new_message: UpdateMessage,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> UpdateMessageResponse:
    print("HERE <----------------------------------------")
    print("update_conversation")
    user_id = ctx.get_user_id()
    message = get_message(session, message_id, user_id)
    delete_messages_after_message(session, message, user_id)
    if new_message.tool_calls:
        tool_call_crud.delete_tool_calls_by_message_id(session, message_id)
        for tool_call in new_message.tool_calls:
            tool_call = ToolCallModel(
                name=tool_call.name,
                parameters=to_dict(tool_call.parameters),
                message_id=message.id,
            )
            tool_call_crud.create_tool_call(session, tool_call)
        new_message.tool_calls = None
    if new_message.documents:
        ids = [document.document_id for document in new_message.documents]
        print(f"new_message.documents {new_message.documents}")
        for document in message.documents:
            if document.document_id not in ids:
                print(f"deleting document {document.document_id}")
                document_crud.delete_document(session, document.id)
        for citation in message.citations:
            citation_crud.delete_citation(session, citation.id)
        new_message.text = ""
        new_message.documents = None
    if new_message.tool_plan:
        new_message.text = new_message.tool_plan
    message_crud.update_message(session, message, new_message)
    return UpdateMessageResponse()
