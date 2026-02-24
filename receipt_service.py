import io
from dataclasses import dataclass
from datetime import date
from typing import Iterable

from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


class LogoLoadError(Exception):
    pass


@dataclass(frozen=True)
class ReceiptData:
    reason: str
    date: date
    location: str
    host: str
    persons: list[str]
    amount: float
    tip: float

    @property
    def total_amount(self) -> float:
        return self.amount + self.tip


def validate_receipt_inputs(
    *,
    host: str,
    location: str,
    reason: str,
    persons: Iterable[str],
    has_receipt_attachment: bool,
) -> list[str]:
    errors: list[str] = []
    if not host.strip():
        errors.append("Bitte gib den Bewirtenden an.")
    if not location.strip():
        errors.append("Bitte gib den Ort der Bewirtung an.")
    if not reason.strip():
        errors.append("Bitte gib den Anlass der Bewirtung an.")
    if len([person for person in persons if person.strip()]) < 1:
        errors.append("Bitte gib mindestens eine bewirtete Personen an.")
    if not has_receipt_attachment:
        errors.append("Bitte lade einen Beleg hoch oder nimm ein Foto auf.")
    return errors


def generate_receipt_pdf(
    *,
    receipt: ReceiptData,
    add_logo: bool,
    logo_path: str,
    attachment_bytes: bytes | None,
    attachment_filename: str | None,
) -> bytes:
    summary_pdf = _build_summary_pdf(receipt=receipt, add_logo=add_logo, logo_path=logo_path)
    if not attachment_bytes:
        return summary_pdf

    attachment_name = (attachment_filename or "").lower()
    if attachment_name.endswith(".pdf"):
        return _append_attachment_pdf(summary_pdf=summary_pdf, attachment_pdf=attachment_bytes)

    return _append_attachment_image(summary_pdf=summary_pdf, image_bytes=attachment_bytes)


def _build_summary_pdf(*, receipt: ReceiptData, add_logo: bool, logo_path: str) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    if add_logo:
        try:
            _draw_logo(pdf=pdf, logo_path=logo_path, page_width=width, page_height=height)
        except Exception as exc:
            raise LogoLoadError(str(exc)) from exc

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, "Bewirtungsbeleg")

    pdf.setFont("Helvetica-Bold", 11)
    y = height - 80
    line_spacing = 18

    pdf.drawString(50, y, "Anlass der Bewirtung:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(180, y, receipt.reason)

    y -= line_spacing
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, y, "Tag der Bewirtung:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(180, y, receipt.date.strftime("%d.%m.%Y"))

    y -= line_spacing
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, y, "Ort der Bewirtung:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(180, y, receipt.location)

    y -= line_spacing
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, y, "Betrag:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(180, y, f"{receipt.amount:.2f} €")

    y -= line_spacing
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, y, "Trinkgeld:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(180, y, f"{receipt.tip:.2f} €")

    y -= line_spacing
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, y, "Gesamtbetrag:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(180, y, f"{receipt.total_amount:.2f} €")

    y -= line_spacing
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, y, "Bewirtende Person:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(180, y, receipt.host)

    y -= line_spacing * 2
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, y, "Bewirtete Personen:")

    y -= line_spacing
    pdf.setFont("Helvetica", 11)
    for person in receipt.persons:
        pdf.drawString(70, y, f"- {person}")
        y -= line_spacing

    signature_y = 100
    pdf.setFont("Helvetica", 11)
    pdf.line(50, signature_y, 250, signature_y)
    pdf.drawString(50, signature_y - 15, "Unterschrift")
    pdf.drawRightString(
        width - 50,
        signature_y - 15,
        f"Datum: {receipt.date.strftime('%d.%m.%Y')}",
    )

    footer_text = (
        "Dieser Beleg wurde erstellt mit Bewirti – Der Bewirtungsbeleg Buddy - "
        "bewirti.swokiz.com"
    )
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawCentredString(width / 2, 30, footer_text)
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def _draw_logo(
    *,
    pdf: canvas.Canvas,
    logo_path: str,
    page_width: float,
    page_height: float,
) -> None:
    with Image.open(logo_path) as logo:
        logo_width_original, logo_height_original = logo.size
    display_width = 150
    aspect_ratio = logo_height_original / logo_width_original
    display_height = display_width * aspect_ratio
    pdf.drawImage(
        logo_path,
        page_width - display_width - 50,
        page_height - display_height - 30,
        width=display_width,
        height=display_height,
        mask="auto",
    )


def _append_attachment_pdf(*, summary_pdf: bytes, attachment_pdf: bytes) -> bytes:
    output = PdfWriter()
    output.append(PdfReader(io.BytesIO(summary_pdf)))
    output.append(PdfReader(io.BytesIO(attachment_pdf)))
    final_pdf = io.BytesIO()
    output.write(final_pdf)
    final_pdf.seek(0)
    return final_pdf.getvalue()


def _append_attachment_image(*, summary_pdf: bytes, image_bytes: bytes) -> bytes:
    summary_reader = PdfReader(io.BytesIO(summary_pdf))
    width, height = A4

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_width, image_height = image.size
    aspect_ratio = image_height / image_width
    max_width = width - 100
    scaled_height = max_width * aspect_ratio

    image_page_buffer = io.BytesIO()
    image_canvas = canvas.Canvas(image_page_buffer, pagesize=A4)
    image_canvas.drawImage(
        ImageReader(image),
        50,
        height - scaled_height - 50,
        width=max_width,
        height=scaled_height,
    )
    image_canvas.showPage()
    image_canvas.save()
    image_page_buffer.seek(0)
    image_reader = PdfReader(image_page_buffer)

    output = PdfWriter()
    for page in summary_reader.pages:
        output.add_page(page)
    for page in image_reader.pages:
        output.add_page(page)

    final_pdf = io.BytesIO()
    output.write(final_pdf)
    final_pdf.seek(0)
    return final_pdf.getvalue()
