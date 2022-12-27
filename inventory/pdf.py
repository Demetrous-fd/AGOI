from tempfile import TemporaryDirectory
from dataclasses import dataclass
from typing import Literal
from pathlib import Path
from uuid import uuid4
import io

from django.template.loader import get_template

import pdfkit


@dataclass(frozen=True)
class PDFBlock:
    object: str
    batch_code: str
    instances: list


@dataclass(frozen=True)
class CreatePDFContext:
    items: list[PDFBlock]
    page_size: Literal["A4", "A5", "A6"]


def create_pdf(context: CreatePDFContext) -> io.BytesIO:
    template = get_template("inventory/download-qr-codes.html")
    html = template.render({"items": context.items})
    buffer = io.BytesIO()
    options = {
        'page-size': context.page_size
    }
    with TemporaryDirectory() as dir_:
        file_path = Path(dir_, f"{uuid4()}.pdf")
        pdfkit.from_string(html, file_path, options=options)
        with open(file_path, "rb") as file:
            buffer.write(file.read())
            buffer.seek(0)
    return buffer
