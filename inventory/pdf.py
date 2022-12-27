from tempfile import TemporaryDirectory
from typing import Literal, Iterable
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4
import io

from django.template.loader import get_template

import pdfkit


@dataclass(frozen=True)
class PDFBlock:
    batch_code: str
    instances: Iterable


@dataclass(frozen=True)
class CreatePDFContext:
    items: list[PDFBlock]
    page_size: Literal["A4", "A5", "A6"]


def create_pdf(context: CreatePDFContext) -> io.BytesIO:
    template = get_template("inventory/download-qr-codes.html")
    html = template.render({"items": context.items})
    buffer = io.BytesIO()
    options = {
        'page-size': context.page_size,
        'margin-top': '0',
        'margin-right': '0',
        'margin-bottom': '0',
        'margin-left': '0'
    }
    with TemporaryDirectory() as dir_:
        file_path = Path(dir_, f"{uuid4()}.pdf")
        pdfkit.from_string(html, file_path, options=options)
        with open(file_path, "rb") as file:
            buffer.write(file.read())
            buffer.seek(0)
    return buffer
