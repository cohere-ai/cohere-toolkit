from backend.services.file import (
    CALENDAR_EXTENSION,
    CSV_EXTENSION,
    DOCX_EXTENSION,
    EXCEL_EXTENSION,
    EXCEL_OLD_EXTENSION,
    JSON_EXTENSION,
    MARKDOWN_EXTENSION,
    PARQUET_EXTENSION,
    PDF_EXTENSION,
    TEXT_EXTENSION,
    TSV_EXTENSION,
    get_file_extension,
    read_docx,
    read_excel,
    read_parquet,
)
from backend.services.utils import read_pdf


def serialize_metadata(resource: dict) -> dict:
    data = {}

    # Only return primitive types, Coral cannot parse arrays/sub-dictionaries
    stripped_resource = {
        key: str(value)
        for key, value in resource.items()
        if isinstance(value, (str, int, bool))
    }
    data.update({**stripped_resource})

    if "name" in resource:
        data["title"] = resource["name"]

    if "webUrl" in resource:
        data["url"] = resource["webUrl"]

    return data


def serialize_file_contents(file_contents: bytes, filename: str) -> str:
    """
    Reads the file contents based on the file extension

    Args:
        file_contents(bytes): Contents of the file
        filename (str): Name of the file

    Returns:
        str: The file contents

    Raises:
        ValueError: If the file extension is not supported
    """
    file_extension = get_file_extension(filename)

    if file_extension == PDF_EXTENSION:
        return read_pdf(file_contents)
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
