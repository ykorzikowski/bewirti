from datetime import date
from io import BytesIO
from pathlib import Path

import pytest
from pypdf import PdfReader

from receipt_service import ReceiptData, generate_receipt_pdf


@pytest.mark.e2e
def test_e2e_generated_receipt_artifact_is_valid() -> None:
    output_dir = Path(".artifacts/test-outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "receipt_e2e_regression.pdf"

    receipt = ReceiptData(
        reason="Kundenmeeting Q1",
        date=date(2026, 1, 15),
        location="Hamburg",
        host="Erika Beispiel",
        persons=["Alex", "Sven"],
        amount=84.5,
        tip=5.5,
    )
    pdf_bytes = generate_receipt_pdf(
        receipt=receipt,
        add_logo=False,
        logo_path="res/bewirti_logo.png",
        attachment_bytes=None,
        attachment_filename=None,
    )
    output_path.write_bytes(pdf_bytes)

    assert output_path.exists()
    assert output_path.stat().st_size > 1000

    reader = PdfReader(BytesIO(pdf_bytes))
    assert len(reader.pages) == 1
    text = reader.pages[0].extract_text()
    assert text is not None
    assert "Bewirtungsbeleg" in text
    assert "Kundenmeeting Q1" in text
    assert "Erika Beispiel" in text
    assert "90.00" in text
