import io

from fastapi import Request
from pypdf import PdfReader


def get_deployment_config(request: Request) -> dict:
    headers = request.get("headers", {})
    header = get_header_value(headers, ["deployment-config", "Deployment-Config"])
    config = {}
    for c in header.split(";"):
        kv = c.split("=")
        if len(kv) < 2:
            continue
        config[kv[0]] = "".join(kv[1:])
    return config


def get_header_value(headers: list, keys: list) -> str:
    for k, v in headers:
        if k.decode("utf-8") in keys:
            return v.decode("utf-8")
    return ""


def read_pdf(file_contents: bytes) -> str:
    """Reads the text from a PDF file using PyPDF2

    Args:
        file_contents (bytes): The file contents

    Returns:
        str: The text extracted from the PDF
    """
    pdf_reader = PdfReader(io.BytesIO(file_contents))
    text = ""

    # Extract text from each page
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        text += page_text

    return text
