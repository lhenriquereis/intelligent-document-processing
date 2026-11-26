from pathlib import Path
import shutil
import pymupdf


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "samples"

DATA_DIR.mkdir(parents=True, exist_ok=True)


def create_pdf(filename: str, text: str):
    """Generate a synthetic PDF document."""

    output = DATA_DIR / filename

    with pymupdf.open() as document:
        page = document.new_page()
        page.insert_text((50, 70), text, fontsize=12)
        document.save(output)

    print(f"Created: {filename}")

    return output


def generate_samples():

    # Valid invoice 001

    invoice = create_pdf(
        "invoice_001.pdf",
        "SAMPLE INVOICE - NOT VALID FOR PAYMENT\n\n"
        "Supplier: Example Technology Ltd\n"
        "Invoice Number: INV-001\n"
        "Issue Date: 2026-11-01\n"
        "Due Date: 2026-12-01\n"
        "Description: Software Subscription\n"
        "Currency: USD\n"
        "Total Amount: 1250.00\n"
    )

    # Valid invoice 002

    create_pdf(
        "invoice_002.pdf",
        "SAMPLE INVOICE - NOT VALID FOR PAYMENT\n\n"
        "Supplier: Demo Logistics Ltd\n"
        "Invoice Number: INV-002\n"
        "Issue Date: 2026-11-05\n"
        "Due Date: 2026-12-05\n"
        "Description: Transportation Services\n"
        "Currency: USD\n"
        "Total Amount: 850.00\n"
    )

    # Invalid invoice: negative amount

    create_pdf(
        "invoice_003.pdf",
        "SAMPLE INVOICE - NOT VALID FOR PAYMENT\n\n"
        "Supplier: Fictional Marketing Ltd\n"
        "Invoice Number: INV-003\n"
        "Issue Date: 2026-11-10\n"
        "Due Date: 2026-12-10\n"
        "Description: Marketing Services\n"
        "Currency: USD\n"
        "Total Amount: -350.00\n"
    )

    # Invalid invoice: missing supplier

    create_pdf(
        "invoice_004.pdf",
        "SAMPLE INVOICE - NOT VALID FOR PAYMENT\n\n"
        "Invoice Number: INV-004\n"
        "Issue Date: 2026-11-12\n"
        "Due Date: 2026-12-12\n"
        "Description: Office Equipment\n"
        "Currency: USD\n"
        "Total Amount: 700.00\n"
    )

    # Invalid invoice: inconsistent dates

    create_pdf(
        "invoice_005.pdf",
        "SAMPLE INVOICE - NOT VALID FOR PAYMENT\n\n"
        "Supplier: Demo Consulting Ltd\n"
        "Invoice Number: INV-005\n"
        "Issue Date: 2026-11-20\n"
        "Due Date: 2026-11-10\n"
        "Description: Consulting Services\n"
        "Currency: USD\n"
        "Total Amount: 1200.00\n"
    )

    # Receipt

    create_pdf(
        "receipt_001.pdf",
        "SAMPLE RECEIPT\n\n"
        "Supplier: Fictional Office Supplies\n"
        "Receipt Number: REC-001\n"
        "Payment Date: 2026-11-10\n"
        "Currency: USD\n"
        "Total Amount: 150.00\n"
    )

    # Payment notice

    create_pdf(
        "payment_001.pdf",
        "SAMPLE PAYMENT NOTICE\n\n"
        "Supplier: Example Consulting Ltd\n"
        "Reference: PAY-001\n"
        "Due Date: 2026-12-10\n"
        "Currency: USD\n"
        "Total Amount: 500.00\n"
    )

    # Unknown document

    create_pdf(
        "unknown_001.pdf",
        "SAMPLE EMPLOYEE CONTRACT\n\n"
        "This document is not a financial document.\n"
    )

    # Exact duplicate

    shutil.copyfile(
        invoice,
        DATA_DIR / "invoice_001_duplicate.pdf"
    )

    print("Created: invoice_001_duplicate.pdf")
    print("\nSample generation completed.")


if __name__ == "__main__":
    generate_samples()
