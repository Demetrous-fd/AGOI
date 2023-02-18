from tempfile import TemporaryDirectory
from typing import Literal, Iterable
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4
from enum import Enum
import io

from django.template.loader import get_template

import pdfkit


class PageSize(Enum):
    A4 = "A4"
    LP2824_PLUS = "LP2824_PLUS"


def _get_page_size_options(page_size: PageSize) -> dict:
    _page_size = {
        PageSize.A4: {'page-size': "A4"},
        PageSize.LP2824_PLUS: {
            'page-width': 58,
            'page-height': 30,
        },
    }
    return _page_size.get(page_size, {})


@dataclass(frozen=True)
class PDFBlock:
    contract_number: str
    instances: Iterable


@dataclass(frozen=True)
class PDFContext:
    items: list[PDFBlock]
    page_size: PageSize


def create_pdf(context: PDFContext) -> io.BytesIO:
    template = get_template("inventory/download-qr-codes.html")
    html = template.render({"items": context.items, "page_size": context.page_size})
    buffer = io.BytesIO()
    options = {
        **_get_page_size_options(context.page_size),
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
