import io

import pandas as pd
from docx import Document
from fastapi import HTTPException
from fastapi import UploadFile as FastAPIUploadFile
from python_calamine.pandas import pandas_monkeypatch

import backend.crud.conversation as conversation_crud
import backend.crud.file as file_crud
from backend.config.tools import ToolName
from backend.crud import agent as agent_crud
from backend.crud import message as message_crud
from backend.database_models.conversation import ConversationFileAssociation
from backend.database_models.database import DBSessionDep
from backend.database_models.file import File as FileModel
from backend.schemas.file import File, UpdateFileRequest
from backend.services import utils
from backend.services.agent import validate_agent_exists

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

# Monkey patch Pandas to use Calamine for Excel reading because Calamine is faster than Pandas
pandas_monkeypatch()

file_service = None


def get_file_service():
    global file_service
    if file_service is None:
        file_service = FileService()
    return file_service


class FileService:
    @property
    def is_compass_enabled(self) -> bool:
        # TODO Scott: add compass env variable anc check here
        return False

    # All these functions will eventually support file operations on Compass
    async def create_conversation_files(
        self,
        session: DBSessionDep,
        files: list[FastAPIUploadFile],
        user_id: str,
        conversation_id: str,
    ) -> list[File]:
        """
        Create files and associations with conversation

        Args:
            session (DBSessionDep): The database session
            files (list[FastAPIUploadFile]): The files to upload
            user_id (str): The user ID
            conversation_id (str): The conversation ID

        Returns:
            list[File]: The files that were created
        """
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
                FileModel(
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
        """
        Get files by agent ID

        Args:
            session (DBSessionDep): The database session
            user_id (str): The user ID
            agent_id (str): The agent ID

        Returns:
            list[File]: The files that were created
        """
        agent = validate_agent_exists(session, agent_id, user_id)

        files = []
        agent_tool_metadata = agent.tools_metadata
        if agent_tool_metadata is not None and len(agent_tool_metadata) > 0:
            artifacts = next(
                (
                    tool_metadata.artifacts
                    for tool_metadata in agent_tool_metadata
                    if tool_metadata.tool_name == ToolName.Read_File
                    or tool_metadata.tool_name == ToolName.Search_File
                ),
                [],  # Default value if the generator is empty
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
    ) -> list[FileModel]:
        """
        Get files by conversation ID

        Args:
            session (DBSessionDep): The database session
            user_id (str): The user ID
            conversation_id (str): The conversation ID

        Returns:
            list[File]: The files that were created
        """
        conversation = conversation_crud.get_conversation(
            session, conversation_id, user_id
        )
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation with ID: {conversation_id} not found.",
            )
        file_ids = conversation.file_ids

        files = []
        if file_ids is not None:
            files = file_crud.get_files_by_ids(session, file_ids, user_id)

        return files

    def delete_file_from_conversation(
        self, session: DBSessionDep, conversation_id: str, file_id: str, user_id: str
    ) -> None:
        """
        Delete file from conversation

        Args:
            session (DBSessionDep): The database session
            conversation_id (str): The conversation ID
            file_id (str): The file ID
            user_id (str): The user ID
        """
        conversation_crud.delete_conversation_file_association(
            session, conversation_id, file_id, user_id
        )
        file_crud.delete_file(session, file_id, user_id)
        return

    def get_file_by_id(self, session: DBSessionDep, file_id: str, user_id: str) -> File:
        """
        Get file by ID

        Args:
            session (DBSessionDep): The database session
            file_id (str): The file ID
            user_id (str): The user ID

        Returns:
            File: The file that was created
        """
        file = file_crud.get_file(session, file_id, user_id)
        return file

    def get_files_by_ids(
        self, session: DBSessionDep, file_ids: list[str], user_id: str
    ) -> list[FileModel]:
        """
        Get files by IDs

        Args:
            session (DBSessionDep): The database session
            file_ids (list[str]): The file IDs
            user_id (str): The user ID

        Returns:
            list[File]: The files that were created
        """
        files = file_crud.get_files_by_ids(session, file_ids, user_id)
        return files

    def update_file(
        self, session: DBSessionDep, file: File, new_file: UpdateFileRequest
    ) -> File:
        """
        Update file

        Args:
            session (DBSessionDep): The database session
            file (File): The file to update
            new_file (UpdateFileRequest): The new file data

        Returns:
            File: The updated file
        """
        updated_file = file_crud.update_file(session, file, new_file)
        return updated_file

    def bulk_delete_files(
        self, session: DBSessionDep, file_ids: list[str], user_id: str
    ) -> None:
        """
        Bulk delete files

        Args:
            session (DBSessionDep): The database session
            file_ids (list[str]): The file IDs
            user_id (str): The user ID
        """
        file_crud.bulk_delete_files(session, file_ids, user_id)

    def get_files_by_message_id(
        self, session: DBSessionDep, message_id: str, user_id: str
    ) -> list[File]:
        """
        Get message files

        Args:
            session (DBSessionDep): The database session
            message_id (str): The message ID
            user_id (str): The user ID

        Returns:
            list[File]: The files that were created
        """
        message = message_crud.get_message(session, message_id, user_id)
        files = []
        if message.file_ids is not None:
            files = file_crud.get_files_by_ids(session, message.file_ids, user_id)
        return files


def attach_conversation_id_to_files(
    conversation_id: str, files: list[FileModel]
) -> list[File]:
    results = []
    for file in files:
        results.append(
            File(
                id=file.id,
                conversation_id=conversation_id,
                file_name=file.file_name,
                file_size=file.file_size,
                file_path=file.file_path,
                user_id=file.user_id,
                created_at=file.created_at,
                updated_at=file.updated_at,
            )
        )
    return results


def validate_file(session: DBSessionDep, file_id: str, user_id: str) -> File:
    """Validates if a file exists and belongs to the user

    Args:
        session (DBSessionDep): Database session
        file_id (str): File ID
        user_id (str): User ID

    Returns:
        File: File object

    Raises:
        HTTPException: If the file is not found
    """
    file = file_crud.get_file(session, file_id, user_id)

    if not file:
        raise HTTPException(
            status_code=404,
            detail=f"File with ID: {file_id} not found.",
        )

    return file


def get_file_extension(file_name: str) -> str:
    """Returns the file extension

    Args:
        file_name (str): The file name

    Returns:
        str: The file extension
    """
    return file_name.split(".")[-1].lower()


async def get_file_content(file: FastAPIUploadFile) -> str:
    """Reads the file contents based on the file extension

    Args:
        file (UploadFile): The file to read

    Returns:
        str: The file contents

    Raises:
        ValueError: If the file extension is not supported
    """
    file_contents = await file.read()
    file_extension = get_file_extension(file.filename)

    if file_extension == PDF_EXTENSION:
        return utils.read_pdf(file_contents)
    elif file_extension == DOCX_EXTENSION:
        return read_docx(file_contents)
    elif file_extension in [
        TEXT_EXTENSION,
        MARKDOWN_EXTENSION,
        CSV_EXTENSION,
        JSON_EXTENSION,
    ]:
        return file_contents.decode("utf-8")
    elif file_extension in [EXCEL_EXTENSION, EXCEL_OLD_EXTENSION]:
        return read_excel(file_contents)

    raise ValueError(f"File extension {file_extension} is not supported")


def read_excel(file_contents: bytes) -> str:
    """Reads the text from an Excel file using Pandas

    Args:
        file_contents (bytes): The file contents

    Returns:
        str: The text extracted from the Excel
    """
    excel = pd.read_excel(io.BytesIO(file_contents), engine="calamine")
    return excel.to_string()


def read_docx(file_contents: bytes) -> str:
    document = Document(io.BytesIO(file_contents))
    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


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
