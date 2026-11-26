from extractor import extract_text, DATA_DIR


def classify_document(text: str) -> str:
    """Classify a financial document using predefined rules."""

    lines = text.strip().upper().splitlines()

    if not lines:
        return "UNKNOWN"

    header = lines[0].strip()

    if header.startswith("SAMPLE INVOICE"):
        return "INVOICE"

    elif header.startswith("SAMPLE RECEIPT"):
        return "RECEIPT"

    elif header.startswith("SAMPLE PAYMENT NOTICE"):
        return "PAYMENT_NOTICE"

    else:
        return "UNKNOWN"


if __name__ == "__main__":

    pdf_path = DATA_DIR / "invoice_001.pdf"

    text = extract_text(pdf_path)

    document_type = classify_document(text)

    print("=" * 50)
    print("DOCUMENT CLASSIFICATION")
    print("=" * 50)

    print(f"File: {pdf_path.name}")
    print(f"Document type: {document_type}")
