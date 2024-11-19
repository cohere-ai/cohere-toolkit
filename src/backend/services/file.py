import io

import pandas as pd
from docx import Document
from fastapi import Depends, HTTPException
from fastapi import UploadFile as FastAPIUploadFile
from python_calamine.pandas import pandas_monkeypatch

import backend.crud.conversation as conversation_crud
import backend.crud.file as file_crud
from backend.crud import message as message_crud
from backend.database_models.conversation import ConversationFileAssociation
from backend.database_models.database import DBSessionDep
from backend.database_models.file import File as FileModel
from backend.schemas.context import Context
from backend.schemas.file import ConversationFilePublic, File
from backend.services import utils
from backend.services.agent import validate_agent_exists
from backend.services.context import get_context
from backend.services.logger.utils import LoggerFactory

MAX_FILE_SIZE = 20_000_000  # 20MB
MAX_TOTAL_FILE_SIZE = 1_000_000_000  # 1GB

PDF_EXTENSION = "pdf"
TEXT_EXTENSION = "txt"
MARKDOWN_EXTENSION = "md"
CSV_EXTENSION = "csv"
TSV_EXTENSION = "tsv"
EXCEL_EXTENSION = "xlsx"
EXCEL_OLD_EXTENSION = "xls"
JSON_EXTENSION = "json"
DOCX_EXTENSION = "docx"
PARQUET_EXTENSION = "parquet"
CALENDAR_EXTENSION = "ics"

# Monkey patch Pandas to use Calamine for Excel reading because Calamine is faster than Pandas
pandas_monkeypatch()

file_service = None

logger = LoggerFactory().get_logger()


def get_file_service():
    """
    Initialize a singular instance of FileService if not initialized yet

    Returns:
        FileService: The singleton FileService instance
    """
    global file_service
    if file_service is None:
        file_service = FileService()
    return file_service


class FileService:
    """
    FileService class

    This class manages interfacing with different file storage solutions,
    currently supports storing files in PostgreSQL.
    """

    async def create_conversation_files(
        self,
        session: DBSessionDep,
        files: list[FastAPIUploadFile],
        user_id: str,
        conversation_id: str,
        ctx: Context,
    ) -> list[File]:
        """
        Create files and associations with a conversation

        Args:
            session (DBSessionDep): The database session
            files (list[FastAPIUploadFile]): The files to upload
            user_id (str): The user ID
            conversation_id (str): The conversation ID
            ctx (Context): Context object

        Returns:
            list[File]: The files that were created
        """
        uploaded_files = await insert_files_in_db(session, files, user_id)

        for file in uploaded_files:
            conversation_crud.create_conversation_file_association(
                session,
                ConversationFileAssociation(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    file_id=file.id,
                ),
            )

        return uploaded_files

    async def create_agent_files(
        self,
        session: DBSessionDep,
        files: list[FastAPIUploadFile],
        user_id: str,
        ctx: Context,
    ) -> list[File]:
        """
        Create files and associations with an agent

        Args:
            session (DBSessionDep): The database session
            files (list[FastAPIUploadFile]): The files to upload
            user_id (str): The user ID
        Returns:
            list[File]: The files that were created
        """
        uploaded_files = await insert_files_in_db(session, files, user_id)

        return uploaded_files

    def get_file_ids_by_agent_id(
        self, session: DBSessionDep, user_id: str, agent_id: str, ctx: Context
    ) -> list[str]:
        """
        Get file IDs associated with a specific agent ID

        Args:
            session (DBSessionDep): The database session
            user_id (str): The user ID
            agent_id (str): The agent ID
            ctx (Context): Context object

        Returns:
            list[str]: IDs of files that were created
        """
        from backend.config.tools import Tool
        from backend.tools.files import FileToolsArtifactTypes

        agent = validate_agent_exists(session, agent_id, user_id)

        if not agent.tools_metadata:
            return []

        artifacts = next(
            (
                tool_metadata.artifacts
                for tool_metadata in agent.tools_metadata
                if tool_metadata.tool_name == Tool.Read_File.value.ID
                or tool_metadata.tool_name == Tool.Search_File.value.ID
            ),
            [],  # Default value if the generator is empty
        )

        return [
            artifact.get("id")
            for artifact in artifacts
            if artifact.get("type") == FileToolsArtifactTypes.local_file
        ]

    def get_files_by_agent_id(
        self, session: DBSessionDep, user_id: str, agent_id: str, ctx: Context
    ) -> list[File]:
        """
        Get files by agent ID

        Args:
            session (DBSessionDep): The database session
            user_id (str): The user ID
            agent_id (str): The agent ID
            ctx (Context): Context object

        Returns:
            list[File]: The files that were created
        """
        file_ids = self.get_file_ids_by_agent_id(session, user_id, agent_id, ctx)

        if not file_ids:
            return []

        return file_crud.get_files_by_ids(session, file_ids, user_id)

    def get_files_by_conversation_id(
        self, session: DBSessionDep, user_id: str, conversation_id: str, ctx: Context
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

    def delete_conversation_file_by_id(
        self,
        session: DBSessionDep,
        conversation_id: str,
        file_id: str,
        user_id: str,
        ctx: Context,
    ) -> None:
        """
        Delete a file asociated with a conversation

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

    def delete_agent_file_by_id(
        self,
        session: DBSessionDep,
        agent_id: str,
        file_id: str,
        user_id: str,
        ctx: Context,
    ) -> None:
        """
        Delete a file asociated with an agent

        Args:
            session (DBSessionDep): The database session
            agent_id (str): The agent ID
            file_id (str): The file ID
            user_id (str): The user ID
        """
        file_crud.delete_file(session, file_id, user_id)

        return

    def delete_all_conversation_files(
        self,
        session: DBSessionDep,
        conversation_id: str,
        file_ids: list[str],
        user_id: str,
        ctx: Context = Depends(get_context),
    ) -> None:
        """
        Delete all files associated with a conversation

        Args:
            session (DBSessionDep): The database session
            conversation_id (str): The conversation ID
            file_ids (list[str]): The file IDs
            user_id (str): The user ID
            ctx (Context): Context object
        """
        logger = ctx.get_logger()

        logger.info(
                event=f"Deleting conversation {conversation_id} files from DB."
            )
        file_crud.bulk_delete_files(session, file_ids, user_id)

    def get_files_by_message_id(
        self, session: DBSessionDep, message_id: str, user_id: str, ctx: Context
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


# Misc
def validate_file(
    session: DBSessionDep, file_id: str, user_id: str
) -> File:
    """
    Validates if a file exists and belongs to the user

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


async def insert_files_in_db(
    session: DBSessionDep,
    files: list[FastAPIUploadFile],
    user_id: str,
) -> list[File]:
    """
    Insert files into the database

    Args:
        session (DBSessionDep): The database session
        files (list[FastAPIUploadFile]): The files to upload
        user_id (str): The user ID

    Returns:
        list[File]: The files that were created
    """
    files_to_upload = []
    for file in files:
        content = await get_file_content(file)
        cleaned_content = content.replace("\x00", "")
        filename = file.filename.encode("ascii", "ignore").decode("utf-8")

        files_to_upload.append(
            FileModel(
                file_name=filename,
                file_size=file.size,
                file_content=cleaned_content,
                user_id=user_id,
            )
        )

    uploaded_files = file_crud.batch_create_files(session, files_to_upload)
    return uploaded_files


def attach_conversation_id_to_files(
    conversation_id: str, files: list[FileModel]
) -> list[ConversationFilePublic]:
    results = []
    for file in files:
        results.append(
            ConversationFilePublic(
                id=file.id,
                conversation_id=conversation_id,
                file_name=file.file_name,
                file_size=file.file_size,
                user_id=file.user_id,
                created_at=file.created_at,
                updated_at=file.updated_at,
            )
        )
    return results



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
    """Reads the text from a DOCX file

    Args:
        file_contents (bytes): The file contents

    Returns:
        str: The text extracted from the DOCX file, with each paragraph separated by a newline
    """
    document = Document(io.BytesIO(file_contents))
    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


def read_parquet(file_contents: bytes) -> str:
    """Reads the text from a Parquet file using Pandas

    Args:
        file_contents (bytes): The file contents

    Returns:
        str: The text extracted from the Parquet
    """
    parquet = pd.read_parquet(io.BytesIO(file_contents), engine="pyarrow")
    return parquet.to_string()



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
    elif file_extension == PARQUET_EXTENSION:
        return read_parquet(file_contents)
    elif file_extension in [
        TEXT_EXTENSION,
        MARKDOWN_EXTENSION,
        CSV_EXTENSION,
        TSV_EXTENSION,
        JSON_EXTENSION,
        CALENDAR_EXTENSION
    ]:
        return file_contents.decode("utf-8")
    elif file_extension in [EXCEL_EXTENSION, EXCEL_OLD_EXTENSION]:
        return read_excel(file_contents)

    raise ValueError(f"File extension {file_extension} is not supported")
