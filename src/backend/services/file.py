import io
from typing import Any, Optional

import pandas as pd
from fastapi import HTTPException
from fastapi import UploadFile as FastAPIUploadFile
from pypdf import PdfReader
import backend.crud.file as file_crud
import backend.crud.conversation as conversation_crud
from backend.database_models.database import DBSessionDep
from backend.database_models.file import File
from copy import deepcopy
from backend.schemas.conversation import UpdateConversation


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
    def __init__(self, session: DBSessionDep):
        self.session = session
    
    @property
    def is_compass_enabled(self) -> bool:
        # todo: add compass env variable anc check here
        return False
    
    # Files in converations
    async def create_conversation_file(
            self,
            session: DBSessionDep,
            file: FastAPIUploadFile,
            user_id: str,
            conversation_id: str, 
    ) -> File:
        content = await get_file_content(file)
        cleaned_content = content.replace("\x00", "")
        filename = file.filename.encode("ascii", "ignore").decode("utf-8")
        conversation = conversation_crud.get_conversation(session, conversation_id, user_id)
        if not conversation:
            raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID: {conversation_id} not found.",
        )

        file = file_crud.create_file(
            session, 
            File(
                file_name=filename, 
                file_size=file.size,
                file_path=filename,
                file_content=cleaned_content,
                user_id=conversation.user_id)
            )
        
        update_conversation = UpdateConversation()
        if conversation.file_ids:
            file_ids = deepcopy(conversation.file_ids)
            file_ids.append(file.id)
            update_conversation.file_ids = file_ids
        else:
            update_conversation.file_ids = [file.id]

        print("old", conversation.file_ids)
        print("new", update_conversation.file_ids)
        
        conversation_crud.update_conversation(session, conversation, update_conversation)

        return file

    
    def get_files_by_conversation_id(self, conversation_id: str) -> list[File]:
        conversation = conversation_crud.get_conversation(self.session, conversation_id)
        file_ids = conversation.file_ids
        files = file_crud.get_files_by_ids(self.session, file_ids)
        return files


    def delete_file_from_conversation(self, conversation_id: str, file_id: str) -> None:
        conversation = conversation_crud.get_conversation(self.session, conversation_id)
        conversation.file_ids.remove(file_id)
        conversation_crud.update_conversation(self.session, conversation)
        file_crud.delete_file(self.session, file_id)
        return


    # def get_file(self) -> bool:
    #     pass

    # def list_file(self) -> bool:
    #     pass

    # def delete_file(self) -> bool:
    #     pass

    # def update_file(self) -> bool:
    #     pass


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
