from pathlib import Path
import pymupdf

# Define the project directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "samples"

# Create the sample documents directory
DATA_DIR.mkdir(parents=True, exist_ok=True)


def generate_invoice():
    document = pymupdf.open()
    page = document.new_page()

    text = (
        "SAMPLE INVOICE - NOT VALID FOR PAYMENT\n\n"
        "Supplier: Example Technology Ltd\n"
        "Invoice Number: INV-001\n"
        "Issue Date: 2026-11-01\n"
        "Due Date: 2026-12-01\n"
        "Description: Software Subscription\n"
        "Currency: USD\n"
        "Total Amount: 1250.00\n"
    )

    page.insert_text((50, 70), text, fontsize=12)

    output = DATA_DIR / "invoice_001.pdf"

    document.save(output)
    document.close()

    print(f"Sample invoice created: {output}")


if __name__ == "__main__":
    generate_invoice()
