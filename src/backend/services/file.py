import io
import uuid
from datetime import datetime

import pandas as pd
from docx import Document
from fastapi import Depends, HTTPException
from fastapi import UploadFile as FastAPIUploadFile
from python_calamine.pandas import pandas_monkeypatch

import backend.crud.conversation as conversation_crud
import backend.crud.file as file_crud
from backend.config.settings import Settings
from backend.crud import message as message_crud
from backend.database_models.conversation import ConversationFileAssociation
from backend.database_models.database import DBSessionDep
from backend.database_models.file import File as FileModel
from backend.schemas.context import Context
from backend.schemas.file import File
from backend.services import utils
from backend.services.agent import validate_agent_exists
from backend.services.compass import Compass
from backend.services.context import get_context
from backend.services.logger.utils import LoggerFactory

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
compass = None

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


def get_compass():
    """
    Initialize a singular instance of Compass if not initialized yet

    Returns:
        Compass: The singleton Compass instance
    """
    global compass

    if compass is None:
        try:
            compass = Compass()
        except Exception as e:
            logger.error(
                event=f"[Compass File Service] Error initializing Compass: {e}"
            )
            raise e
    return compass


class FileService:
    """
    FileService class

    This class manages interfacing with different file storage solutions. Currently it supports storing files in the Postgres DB and or using Compass.
    By default Toolkit will run with Postgres DB as the storage solution for files.
    To enable Compass as the storage solution, set the `use_compass_file_storage` feature flag to `true` in the .env or .configuration file.
    Also be sure to add the appropriate Compass environment variables to the .env or .configuration file.
    """

    @property
    def is_compass_enabled(self) -> bool:
        """
        Returns whether Compass is enabled as the file storage solution
        """
        return Settings().feature_flags.use_compass_file_storage

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
        if self.is_compass_enabled:
            uploaded_files = await insert_files_in_compass(
                files, user_id, ctx, conversation_id
            )
        else:
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
        uploaded_files = []
        if self.is_compass_enabled:
            """
            Since agents are created after the files are upload we index files into dummy indices first
            We later consolidate them in consolidate_agent_files_in_compass() to a singular index when an agent is created.
            """
            uploaded_files = await insert_files_in_compass(files, ctx, user_id)
        else:
            uploaded_files = await insert_files_in_db(session, files, user_id)

        return uploaded_files

    def get_files_by_agent_id(
        self, session: DBSessionDep, user_id: str, agent_id: str, ctx: Context
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
        from backend.config.tools import ToolName
        from backend.tools.files import FileToolsArtifactTypes

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

            file_ids = list(
                set(
                    artifact.get("id")
                    for artifact in artifacts
                    if artifact.get("type") == FileToolsArtifactTypes.local_file
                )
            )

            if self.is_compass_enabled:
                files = get_files_in_compass(agent_id, file_ids, user_id, ctx)
            else:
                files = file_crud.get_files_by_ids(session, file_ids, user_id)

        return files

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
            if self.is_compass_enabled:
                files = get_files_in_compass(conversation_id, file_ids, user_id, ctx)
            else:
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

        if self.is_compass_enabled:
            delete_file_in_compass(conversation_id, file_id, user_id, ctx)
        else:
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
        if self.is_compass_enabled:
            delete_file_in_compass(agent_id, file_id, user_id, ctx)
        else:
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

        if self.is_compass_enabled:
            compass = get_compass()
            try:
                compass.invoke(
                    action=Compass.ValidActions.DELETE_INDEX,
                    parameters={"index": conversation_id},
                )
            except Exception as e:
                logger.error(
                    event=f"[Compass File Service] Error deleting conversation {conversation_id} files from Compass: {e}"
                )
        else:
            file_crud.bulk_delete_files(session, file_ids, user_id)

        return

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
            if self.is_compass_enabled:
                files = get_files_in_compass(
                    message.conversation_id, message.file_ids, user_id, ctx
                )
            else:
                files = file_crud.get_files_by_ids(session, message.file_ids, user_id)
        return files


# Compass Operations
def delete_file_in_compass(
    index: str, file_id: str, user_id: str, ctx: Context
) -> None:
    """
    Delete a file from Compass

    Args:
        index (str): The index
        file_id (str): The file ID
        user_id (str): The user ID
        ctx (Context): Context object

    Raises:
        HTTPException: If the file is not found
    """
    logger = ctx.get_logger()
    compass = get_compass()

    try:
        compass.invoke(
            action=Compass.ValidActions.DELETE,
            parameters={"index": index, "file_id": file_id},
        )
    except Exception as e:
        logger.error(
            event=f"[Compass File Service] Error deleting file {file_id} on index {index} from Compass: {e}"
        )


def get_files_in_compass(
    index: str, file_ids: list[str], user_id: str, ctx: Context
) -> list[File]:
    """
    Get files from Compass

    Args:
        index (str): The index
        file_ids (list[str]): The file IDs
        user_id (str): The user ID

    Returns:
        list[File]: The files that were created
    """
    compass = get_compass()
    logger = ctx.get_logger()

    files = []
    for file_id in file_ids:
        try:
            fetched_doc = compass.invoke(
                action=Compass.ValidActions.GET_DOCUMENT,
                parameters={"index": index, "file_id": file_id},
            ).result["doc"]["content"]
        except Exception as e:
            logger.error(
                event=f"[Compass File Service] Error fetching file {file_id} on index {index} from Compass: {e}"
            )
            raise HTTPException(
                status_code=404, detail=f"File with ID: {file_id} not found."
            )

        files.append(
            File(
                id=file_id,
                file_name=fetched_doc["file_name"],
                file_size=fetched_doc["file_size"],
                file_path=fetched_doc["file_path"],
                file_content=fetched_doc["text"],
                user_id=user_id,
                created_at=datetime.fromisoformat(fetched_doc["created_at"]),
                updated_at=datetime.fromisoformat(fetched_doc["updated_at"]),
            )
        )

    return files


async def consolidate_agent_files_in_compass(
    file_ids,
    agent_id,
    ctx: Context,
) -> None:
    """
    Consolidate files into a single index (agent ID) in Compass.
    We do this because when agents are created after a file is uploaded, the file is not associated with the agent.
    We consolidate them in a single index to under one agent ID when an agent is created.

    Args:
        file_ids (list[str]): The file IDs
        agent_id (str): The agent ID
        ctx (Context): Context object
    """
    logger = ctx.get_logger()
    compass = get_compass()

    try:
        compass.invoke(
            action=Compass.ValidActions.CREATE_INDEX,
            parameters={
                "index": agent_id,
            },
        )
    except Exception as e:
        logger.Error(
            event=f"[Compass File Service] Error creating index for agent files: {agent_id}, error: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error creating index for agent files: {agent_id}, error: {e}",
        )

    for file_id in file_ids:
        try:
            fetched_doc = compass.invoke(
                action=Compass.ValidActions.GET_DOCUMENT,
                parameters={"index": file_id, "file_id": file_id},
            ).result["doc"]["content"]
            compass().invoke(
                action=Compass.ValidActions.CREATE,
                parameters={
                    "index": agent_id,
                    "file_id": file_id,
                    "file_text": fetched_doc["text"],
                    "custom_context": {
                        "file_id": file_id,
                        "file_name": fetched_doc["file_name"],
                        "file_path": fetched_doc["file_path"],
                        "file_size": fetched_doc["file_size"],
                        "user_id": fetched_doc["user_id"],
                        "created_at": fetched_doc["created_at"],
                        "updated_at": fetched_doc["updated_at"],
                    },
                },
            )
            compass.invoke(
                action=Compass.ValidActions.REFRESH,
                parameters={"index": agent_id},
            )
            # Remove the temporary file index entry
            compass.invoke(
                action=Compass.ValidActions.DELETE_INDEX, parameters={"index": file_id}
            )
        except Exception as e:
            logger.error(
                event=f"[Compass File Service] Error consolidating file {file_id} into agent {agent_id}, error: {e}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Error consolidating file {file_id} into agent {agent_id}, error: {e}",
            )


async def insert_files_in_compass(
    files: list[FastAPIUploadFile],
    user_id: str,
    ctx: Context,
    index: str = None,
) -> list[File]:
    logger = ctx.get_logger()
    compass = get_compass()

    if index is not None:
        try:
            compass.invoke(
                action=Compass.ValidActions.CREATE_INDEX,
                parameters={
                    "index": index,
                },
            )
        except Exception as e:
            logger.error(
                event=f"[Compass File Service] Failed to create index: {index}, error: {e}"
            )

    uploaded_files = []
    for file in files:
        filename = file.filename.encode("ascii", "ignore").decode("utf-8")
        file_bytes = await file.read()
        new_file_id = str(uuid.uuid4())

        # Create temporary index for individual file (files not associated with conversations)
        # Consolidate them under one agent index during agent creation
        if index is None:
            try:
                compass.invoke(
                    action=Compass.ValidActions.CREATE_INDEX,
                    parameters={
                        "index": new_file_id,
                    },
                )
            except Exception as e:
                logger.error(
                    event=f"[Compass File Service] Failed to create index: {index}, error: {e}"
                )

        try:
            compass.invoke(
                action=Compass.ValidActions.CREATE,
                parameters={
                    "index": new_file_id if index is None else index,
                    "file_id": new_file_id,
                    "file_text": file_bytes,
                    "custom_context": {
                        "file_id": new_file_id,
                        "file_name": filename,
                        "file_path": filename,
                        "file_size": file.size,
                        "user_id": user_id,
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                    },
                },
            )
            compass.invoke(
                action=Compass.ValidActions.REFRESH,
                parameters={"index": new_file_id if index is None else index},
            )
        except Exception as e:
            logger.error(
                event=f"[Compass File Service] Failed to create document on index: {index}, error: {e}"
            )

        uploaded_files.append(
            File(
                file_name=filename,
                id=new_file_id,
                file_size=file.size,
                file_path=filename,
                user_id=user_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
        )

    return uploaded_files


# Misc
def validate_file(
    session: DBSessionDep, file_id: str, user_id: str, index: str, ctx: Context
) -> File:
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
    if Settings().feature_flags.use_compass_file_storage:
        file = get_files_in_compass(index, [file_id], user_id, ctx)[0]
    else:
        file = file_crud.get_file(session, file_id, user_id)

    if not file:
        raise HTTPException(
            status_code=404,
            detail=f"File with ID: {file_id} not found.",
        )


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
                file_path=filename,
                file_content=cleaned_content,
                user_id=user_id,
            )
        )

    uploaded_files = file_crud.batch_create_files(session, files_to_upload)
    return uploaded_files


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

    Raises:p
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
