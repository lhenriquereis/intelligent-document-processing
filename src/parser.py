import re
import json
from decimal import Decimal

from extractor import extract_text, DATA_DIR


def extract_field(text: str, field: str):
    """Extract a specific field from document text."""

    pattern = rf"^{re.escape(field)}:[ \t]*(.+)$"

    match = re.search(pattern, text, re.MULTILINE)

    if match:
        return match.group(1).strip()

    return None


def parse_invoice(text: str) -> dict:
    """Convert invoice text into structured data."""

    amount = extract_field(text, "Total Amount")

    invoice = {
        "supplier": extract_field(text, "Supplier"),
        "invoice_number": extract_field(text, "Invoice Number"),
        "issue_date": extract_field(text, "Issue Date"),
        "due_date": extract_field(text, "Due Date"),
        "description": extract_field(text, "Description"),
        "currency": extract_field(text, "Currency"),
        "total_amount": Decimal(amount) if amount else None,
    }

    return invoice


if __name__ == "__main__":

    pdf_path = DATA_DIR / "invoice_001.pdf"

    text = extract_text(pdf_path)

    invoice = parse_invoice(text)

    print("=" * 50)
    print("STRUCTURED INVOICE DATA")
    print("=" * 50)

    print(json.dumps(invoice, indent=4, default=str))
