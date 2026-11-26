from decimal import Decimal

import pytest
import pymupdf

import generate_samples
import generate_scanned_sample

from extractor import extract_text, find_tessdata
from classifier import classify_document
from parser import parse_invoice
from validator import validate_invoice


def test_scanned_invoice_ocr(tmp_path, monkeypatch):
    """Verify OCR extraction and financial validation."""

    if find_tessdata() is None:
        pytest.skip("Tesseract language data not available")

    # Create temporary directories

    samples_dir = tmp_path / "samples"
    samples_dir.mkdir()

    ocr_dir = tmp_path / "ocr_samples"

    monkeypatch.setattr(
        generate_samples,
        "DATA_DIR",
        samples_dir
    )

    monkeypatch.setattr(
        generate_scanned_sample,
        "DATA_DIR",
        samples_dir
    )

    monkeypatch.setattr(
        generate_scanned_sample,
        "OCR_DATA_DIR",
        ocr_dir
    )

    # Generate synthetic documents

    generate_samples.generate_samples()

    scanned_pdf = (
        generate_scanned_sample.generate_scanned_sample()
    )

    assert scanned_pdf.is_file()

    # Confirm the PDF contains no selectable text

    with pymupdf.open(scanned_pdf) as document:

        native_text = "".join(
            page.get_text() for page in document
        )

    assert native_text.strip() == ""

    # Extract text using OCR

    text = extract_text(scanned_pdf)

    assert text.strip() != ""

    # Classify the document

    document_type = classify_document(text)

    assert document_type == "INVOICE"

    # Extract structured financial data

    invoice = parse_invoice(text)

    assert invoice["supplier"] == "Example Technology Ltd"
    assert invoice["invoice_number"] == "INV-001"
    assert invoice["issue_date"] == "2026-11-01"
    assert invoice["due_date"] == "2026-12-01"
    assert invoice["description"] == "Software Subscription"
    assert invoice["currency"] == "USD"
    assert invoice["total_amount"] == Decimal("1250.00")

    # Validate the extracted information

    assert validate_invoice(invoice) == []
