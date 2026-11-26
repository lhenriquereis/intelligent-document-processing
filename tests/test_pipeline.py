from decimal import Decimal

import pytest

from classifier import classify_document
from parser import parse_invoice
from validator import validate_invoice
from duplicate_detector import calculate_hash
from extractor import extract_text

import generate_samples
import generate_duplicate_samples
import main
import exporter


SAMPLE_TEXT = (
    "SAMPLE INVOICE\n"
    "Supplier: Example Technology Ltd\n"
    "Invoice Number: INV-001\n"
    "Issue Date: 2026-11-01\n"
    "Due Date: 2026-12-01\n"
    "Description: Software Subscription\n"
    "Currency: USD\n"
    "Total Amount: 1250.00\n"
)


# Classification tests

@pytest.mark.parametrize(
    "text, expected",
    [
        ("SAMPLE INVOICE", "INVOICE"),
        ("SAMPLE RECEIPT", "RECEIPT"),
        ("SAMPLE PAYMENT NOTICE", "PAYMENT_NOTICE"),
        ("EMPLOYEE CONTRACT", "UNKNOWN"),
    ]
)
def test_document_classification(text, expected):

    assert classify_document(text) == expected


# Structured data extraction test

def test_invoice_parser():

    invoice = parse_invoice(SAMPLE_TEXT)

    assert invoice["supplier"] == "Example Technology Ltd"
    assert invoice["invoice_number"] == "INV-001"
    assert invoice["currency"] == "USD"
    assert invoice["total_amount"] == Decimal("1250.00")


# Financial validation tests

def test_valid_invoice():

    invoice = parse_invoice(SAMPLE_TEXT)

    assert validate_invoice(invoice) == []


def test_negative_amount():

    invoice = parse_invoice(SAMPLE_TEXT)

    invoice["total_amount"] = Decimal("-350.00")

    errors = validate_invoice(invoice)

    assert "Total amount must be a positive decimal" in errors


def test_missing_supplier():

    invoice = parse_invoice(SAMPLE_TEXT)

    invoice["supplier"] = None

    errors = validate_invoice(invoice)

    assert "Missing required field: supplier" in errors


def test_invalid_due_date():

    invoice = parse_invoice(SAMPLE_TEXT)

    invoice["due_date"] = "2026-10-01"

    errors = validate_invoice(invoice)

    assert "Due date cannot be before issue date" in errors


# Binary duplicate detection test

def test_file_hash(tmp_path):

    file_a = tmp_path / "file_a.pdf"
    file_b = tmp_path / "file_b.pdf"

    file_a.write_bytes(b"identical sample content")
    file_b.write_bytes(b"identical sample content")

    assert calculate_hash(file_a) == calculate_hash(file_b)

    file_b.write_bytes(b"different sample content")

    assert calculate_hash(file_a) != calculate_hash(file_b)


# PDF extraction test

def test_pdf_extraction(tmp_path, monkeypatch):

    monkeypatch.setattr(
        generate_samples, "DATA_DIR", tmp_path
    )

    pdf = generate_samples.create_pdf(
        "test_invoice.pdf",
        SAMPLE_TEXT
    )

    text = extract_text(pdf)

    assert "Example Technology Ltd" in text
    assert "1250.00" in text


# Full pipeline integration test

def test_full_pipeline(tmp_path, monkeypatch):

    monkeypatch.setattr(
        generate_samples, "DATA_DIR", tmp_path
    )

    monkeypatch.setattr(
        main, "DATA_DIR", tmp_path
    )

    generate_samples.generate_samples()

    generate_duplicate_samples.generate_duplicate_samples()

    results = main.process_documents()

    assert len(results) == 11

    documents = {
        result["filename"]: result
        for result in results
    }

    assert documents["invoice_001.pdf"]["status"] == "VALIDATED"

    assert (
        documents["invoice_001_duplicate.pdf"]["duplicate_type"]
        == "FILE_HASH"
    )

    assert (
        documents["invoice_002_reissued.pdf"]["duplicate_type"]
        == "BUSINESS_KEY"
    )

    assert (
        documents["invoice_002_review.pdf"]["review_reason"]
        == "CONFLICTING_INVOICE_DATA"
    )

    assert documents["invoice_003.pdf"]["status"] == "VALIDATION_FAILED"

    assert documents["invoice_004.pdf"]["status"] == "VALIDATION_FAILED"

    assert documents["invoice_005.pdf"]["status"] == "VALIDATION_FAILED"

    assert all(
        result["status"] != "ERROR"
        for result in results
    )

    # Excel export verification

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    monkeypatch.setattr(
        exporter, "OUTPUT_DIR", output_dir
    )

    report = exporter.export_results(results)

    assert report.is_file()

    from openpyxl import load_workbook

    workbook = load_workbook(report)

    try:

        assert len(workbook.sheetnames) == 7

        summary = dict(
            workbook["Summary"].values
        )

        assert summary["Total Documents"] == 11
        assert summary["Validated Without Conflict"] == 1
        assert summary["Duplicates"] == 2
        assert summary["Validation Failed"] == 3
        assert summary["Review Required"] == 5
        assert summary["Technical Errors"] == 0

    finally:

        workbook.close()
