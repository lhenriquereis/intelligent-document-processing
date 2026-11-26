import os
import argparse
from pathlib import Path

import pymupdf


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "samples"


def find_tessdata():
    """Locate Tesseract language data."""

    candidates = []

    configured_path = os.getenv("TESSDATA_PREFIX")

    if configured_path:
        candidates.append(Path(configured_path))

    for variable in ["LOCALAPPDATA", "ProgramFiles", "ProgramFiles(x86)"]:

        base = os.getenv(variable)

        if base:

            base_path = Path(base)

            if variable == "LOCALAPPDATA":
                base_path = base_path / "Programs"

            candidates.append(
                base_path / "Tesseract-OCR" / "tessdata"
            )

    for candidate in candidates:

        if (candidate / "eng.traineddata").is_file():
            return str(candidate)

    return None


def extract_text(pdf_path: Path) -> str:
    """Extract PDF text using native extraction or OCR."""

    pdf_path = Path(pdf_path)

    if not pdf_path.is_file():

        raise FileNotFoundError(
            f"File not found: {pdf_path}"
        )

    pages = []

    with pymupdf.open(pdf_path) as document:

        for page in document:

            text = page.get_text()

            # Use OCR when native text is unavailable

            if not text.strip():

                print(
                    f"OCR required: {pdf_path.name} "
                    f"- Page {page.number + 1}"
                )

                text_page = page.get_textpage_ocr(
                    language="eng",
                    dpi=300,
                    full=True,
                    tessdata=find_tessdata()
                )

                text = page.get_text(
                    textpage=text_page
                )

            pages.append(text)

    return "\n".join(pages)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Extract text from PDF documents."
    )

    parser.add_argument(
        "pdf",
        nargs="?",
        type=Path,
        default=DATA_DIR / "invoice_001.pdf"
    )

    args = parser.parse_args()

    extracted_text = extract_text(args.pdf)

    print("=" * 50)
    print("EXTRACTED DOCUMENT TEXT")
    print("=" * 50)

    print(extracted_text)
