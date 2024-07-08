import io
from typing import Any

import pandas as pd
from fastapi import HTTPException
from fastapi import UploadFile as FastAPIUploadFile
from pypdf import PdfReader

import backend.crud.file as file_crud
from backend.database_models.database import DBSessionDep

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
