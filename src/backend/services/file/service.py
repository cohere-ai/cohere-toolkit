import io
from typing import Any

import pandas as pd
from fastapi import UploadFile as FastAPIUploadFile
from pypdf import PdfReader

PDF_EXTENTION = "pdf"
TEXT_EXTENTION = "txt"
MARKDOWN_EXTENTION = "md"
CSV_EXTENTION = "csv"
EXCEL_EXTENTION = "xlsx"
EXCEL_OLD_EXTENTION = "xls"
JSON_EXTENTION = "json"
DOCX_EXTENTION = "docx"


def get_file_extention(file_name: str) -> str:
    return file_name.split(".")[-1].lower()


async def get_file_content(file: FastAPIUploadFile) -> str:
    file_contents = await file.read()
    file_extention = get_file_extention(file.filename)

    if file_extention == PDF_EXTENTION:
        return read_pdf(file_contents)
    elif file_extention in [
        TEXT_EXTENTION,
        MARKDOWN_EXTENTION,
        CSV_EXTENTION,
        JSON_EXTENTION,
        DOCX_EXTENTION,
    ]:
        return file_contents.decode("utf-8")
    elif file_extention in [EXCEL_EXTENTION, EXCEL_OLD_EXTENTION]:
        return read_excel(file_contents)

    raise ValueError(f"File extention {file_extention} is not supported")


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
