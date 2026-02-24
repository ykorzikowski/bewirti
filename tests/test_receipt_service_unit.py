from datetime import date
from io import BytesIO

from PIL import Image
from pypdf import PdfReader
from reportlab.pdfgen import canvas

from receipt_service import ReceiptData, generate_receipt_pdf, validate_receipt_inputs


def _base_receipt() -> ReceiptData:
    return ReceiptData(
        reason="Team Lunch",
        date=date(2026, 2, 1),
        location="Berlin",
        host="Max Mustermann",
        persons=["Anna", "Bob"],
        amount=100.0,
        tip=10.0,
    )


def test_validate_receipt_inputs_collects_expected_errors() -> None:
    errors = validate_receipt_inputs(
        host="",
        location="",
        reason="",
        persons=[],
        has_receipt_attachment=False,
    )
    assert errors == [
        "Bitte gib den Bewirtenden an.",
        "Bitte gib den Ort der Bewirtung an.",
        "Bitte gib den Anlass der Bewirtung an.",
        "Bitte gib mindestens eine bewirtete Personen an.",
        "Bitte lade einen Beleg hoch oder nimm ein Foto auf.",
    ]


def test_generate_receipt_pdf_without_attachment_contains_business_fields() -> None:
    pdf_bytes = generate_receipt_pdf(
        receipt=_base_receipt(),
        add_logo=False,
        logo_path="res/bewirti_logo.png",
        attachment_bytes=None,
        attachment_filename=None,
    )
    reader = PdfReader(BytesIO(pdf_bytes))
    assert len(reader.pages) == 1
    text = reader.pages[0].extract_text()
    assert text is not None
    assert "Bewirtungsbeleg" in text
    assert "Team Lunch" in text
    assert "110.00" in text
    assert "Max Mustermann" in text


def test_generate_receipt_pdf_with_pdf_attachment_appends_pages() -> None:
    attachment_buffer = BytesIO()
    attachment_canvas = canvas.Canvas(attachment_buffer)
    attachment_canvas.drawString(100, 700, "Attached PDF")
    attachment_canvas.showPage()
    attachment_canvas.save()
    attachment_buffer.seek(0)

    pdf_bytes = generate_receipt_pdf(
        receipt=_base_receipt(),
        add_logo=False,
        logo_path="res/bewirti_logo.png",
        attachment_bytes=attachment_buffer.getvalue(),
        attachment_filename="receipt.pdf",
    )
    reader = PdfReader(BytesIO(pdf_bytes))
    assert len(reader.pages) == 2
    assert "Attached PDF" in (reader.pages[1].extract_text() or "")


def test_generate_receipt_pdf_with_image_attachment_adds_image_page() -> None:
    image = Image.new("RGB", (320, 240), color=(255, 255, 255))
    image_buffer = BytesIO()
    image.save(image_buffer, format="JPEG")
    image_buffer.seek(0)

    pdf_bytes = generate_receipt_pdf(
        receipt=_base_receipt(),
        add_logo=False,
        logo_path="res/bewirti_logo.png",
        attachment_bytes=image_buffer.getvalue(),
        attachment_filename="receipt.jpg",
    )
    reader = PdfReader(BytesIO(pdf_bytes))
    assert len(reader.pages) == 2
