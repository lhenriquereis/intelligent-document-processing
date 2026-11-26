from pathlib import Path
import pymupdf


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "samples"


def extract_text(pdf_path: Path) -> str:
    """Extract text from all pages of a PDF document."""

    if not pdf_path.is_file():
        raise FileNotFoundError(f"File not found: {pdf_path}")

    pages = []

    with pymupdf.open(pdf_path) as document:
        for page in document:
            pages.append(page.get_text())

    return "\n".join(pages)


if __name__ == "__main__":

    pdf_path = DATA_DIR / "invoice_001.pdf"

    extracted_text = extract_text(pdf_path)

    print("=" * 50)
    print("EXTRACTED DOCUMENT TEXT")
    print("=" * 50)
    print(extracted_text)
