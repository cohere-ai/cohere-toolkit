import io
from copy import deepcopy
from typing import Any, Optional

import pandas as pd
from fastapi import HTTPException
from fastapi import UploadFile as FastAPIUploadFile
from pypdf import PdfReader

import backend.crud.conversation as conversation_crud
import backend.crud.file as file_crud
from backend.config.tools import ToolName
from backend.crud import agent as agent_crud
from backend.crud import message as message_crud
from backend.database_models.conversation import ConversationFileAssociation
from backend.database_models.database import DBSessionDep
from backend.database_models.file import File
from backend.schemas.conversation import UpdateConversation
from backend.schemas.file import UpdateFile

MAX_FILE_SIZE = 20_000_000  # 20MB
MAX_TOTAL_FILE_SIZE = 1_000_000_000  # 1GB

PDF_EXTENSION = "pdf"
TEXT_EXTENSION = "txt"
MARKDOWN_EXTENSION = "md"
CSV_EXTENSION = "csv"
EXCEL_EXTENSION = "xlsx"
EXCEL_OLD_EXTENSION = "xls"
JSON_EXTENSION = "json"
DOCX_EXTENSION = "docx"


class FileService:
    @property
    def is_compass_enabled(self) -> bool:
        # todo: add compass env variable anc check here
        return False

    # All these functions will eventually support file operations on Compass
    async def create_conversation_files(
        self,
        session: DBSessionDep,
        files: list[FastAPIUploadFile],
        user_id: str,
        conversation_id: str,
    ) -> list[File]:
        # Todo @scott-cohere: need to refactor this file singular and multiple files
        files_to_upload = []
        for file in files:
            content = await get_file_content(file)
            cleaned_content = content.replace("\x00", "")
            filename = file.filename.encode("ascii", "ignore").decode("utf-8")
            conversation = conversation_crud.get_conversation(
                session, conversation_id, user_id
            )
            if not conversation:
                raise HTTPException(
                    status_code=404,
                    detail=f"Conversation with ID: {conversation_id} not found.",
                )

            files_to_upload.append(
                File(
                    file_name=filename,
                    file_size=file.size,
                    file_path=filename,
                    file_content=cleaned_content,
                    user_id=conversation.user_id,
                )
            )

        uploaded_files = file_crud.batch_create_files(session, files_to_upload)
        uploaded_file_ids = [file.id for file in uploaded_files]
        for file_id in uploaded_file_ids:
            conversation_crud.create_conversation_file_association(
                session,
                ConversationFileAssociation(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    file_id=file_id,
                ),
            )

        return uploaded_files

    def get_files_by_agent_id(
        self, session: DBSessionDep, user_id: str, agent_id: str
    ) -> list[File]:
        agent = agent_crud.get_agent_by_id(session, agent_id)
        if agent is None:
            raise HTTPException(
                status_code=404,
                detail=f"Agent with ID: {agent_id} not found.",
            )

        files = []
        agent_tool_metadata = agent.tools_metadata
        if agent_tool_metadata is not None:
            artifacts = next(
                tool_metadata.artifacts
                for tool_metadata in agent_tool_metadata
                if tool_metadata.tool_name == ToolName.Read_File
                or tool_metadata.tool_name == ToolName.Search_File
            )

            # TODO scott: enumerate type names (?), different types for local vs. compass?
            file_ids = [
                artifact.get("id")
                for artifact in artifacts
                if artifact.get("type") == "local_file"
            ]

            files = file_crud.get_files_by_ids(session, file_ids, user_id)

        return files

    def get_files_by_conversation_id(
        self, session: DBSessionDep, user_id: str, conversation_id: str
    ) -> list[File]:
        # TODO scott: add checks that conversations exists, will get none type error on .file_ids
        conversation = conversation_crud.get_conversation(
            session, conversation_id, user_id
        )
        file_ids = conversation.file_ids

        files = []
        if file_ids is not None:
            files = file_crud.get_files_by_ids(session, file_ids, user_id)

        return files

    def delete_file_from_conversation(
        self, session: DBSessionDep, conversation_id: str, file_id: str, user_id: str
    ) -> None:
        conversation_crud.delete_conversation_file_association(
            session, conversation_id, file_id, user_id
        )
        file_crud.delete_file(session, file_id, user_id)
        return

    def get_file_by_id(self, session: DBSessionDep, file_id: str, user_id: str) -> File:
        # currently DB only, implement and fetch from compass after
        file = file_crud.get_file(session, file_id, user_id)
        return file

    def get_files_by_ids(
        self, session: DBSessionDep, file_ids: list[str], user_id: str
    ) -> list[File]:
        # currently DB only, implement and fetch from compass after
        files = file_crud.get_files_by_ids(session, file_ids, user_id)
        return files

    def update_file(
        self, session: DBSessionDep, file: File, new_file: UpdateFile
    ) -> File:
        updated_file = file_crud.update_file(session, file, new_file)
        return updated_file

    def bulk_delete_files(
        self, session: DBSessionDep, file_ids: list[str], user_id: str
    ) -> None:
        file_crud.bulk_delete_files(session, file_ids, user_id)

    def get_message_files(
        self, session: DBSessionDep, message_id: str, user_id: str
    ) -> list[File]:
        message = message_crud.get_message(session, message_id, user_id)
        files = []
        if message.file_ids is not None:
            files = file_crud.get_files_by_ids(session, message.file_ids, user_id)
        return files


def get_file_extension(file_name: str) -> str:
    return file_name.split(".")[-1].lower()


async def get_file_content(file: FastAPIUploadFile) -> str:
    file_contents = await file.read()
    file_extension = get_file_extension(file.filename)

    if file_extension == PDF_EXTENSION:
        return read_pdf(file_contents)
    elif file_extension in [
        TEXT_EXTENSION,
        MARKDOWN_EXTENSION,
        CSV_EXTENSION,
        JSON_EXTENSION,
        DOCX_EXTENSION,
    ]:
        return file_contents.decode("utf-8")
    elif file_extension in [EXCEL_EXTENSION, EXCEL_OLD_EXTENSION]:
        return read_excel(file_contents)

    raise ValueError(f"File extension {file_extension} is not supported")


def read_pdf(file_contents: bytes) -> str:
    pdf_reader = PdfReader(io.BytesIO(file_contents))
    text = ""

    # Extract text from each page
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        text += page_text

    return text


def read_excel(file_contents: bytes) -> str:
    excel = pd.read_excel(io.BytesIO(file_contents))
    return excel.to_string()


def validate_file_size(
    session: DBSessionDep, user_id: str, file: FastAPIUploadFile
) -> None:
    """Validates the file size

    Args:
        user_id (str): The user ID
        file (UploadFile): The file to validate

    Raises:
        HTTPException: If the file size is too large
    """
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds the maximum allowed size of {MAX_FILE_SIZE} bytes.",
        )

    existing_files = file_crud.get_files_by_user_id(session, user_id)
    total_file_size = sum([f.file_size for f in existing_files]) + file.size

    if total_file_size > MAX_TOTAL_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Total file size exceeds the maximum allowed size of {MAX_TOTAL_FILE_SIZE} bytes.",
        )


def validate_batch_file_size(
    session: DBSessionDep, user_id: str, files: list[FastAPIUploadFile]
) -> None:
    """Validate sizes of files in batch

    Args:
        user_id (str): The user ID
        files (list[FastAPIUploadFile]): The files to validate

    Raises:
        HTTPException: If the file size is too large
    """
    total_batch_size = 0
    for file in files:
        if file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"{file.filename} exceeds the maximum allowed size of {MAX_FILE_SIZE} bytes.",
            )
        total_batch_size += file.size

    existing_files = file_crud.get_files_by_user_id(session, user_id)
    total_file_size = sum([f.file_size for f in existing_files]) + total_batch_size

    if total_file_size > MAX_TOTAL_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Total file size exceeds the maximum allowed size of {MAX_TOTAL_FILE_SIZE} bytes.",
        )
