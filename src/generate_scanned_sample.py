import pymupdf

from extractor import DATA_DIR


OCR_DATA_DIR = DATA_DIR.parent / "ocr_samples"


def generate_scanned_sample():
    """Convert a digital PDF into an image-based PDF."""

    OCR_DATA_DIR.mkdir(parents=True, exist_ok=True)

    source = DATA_DIR / "invoice_001.pdf"

    output = OCR_DATA_DIR / "scanned_invoice_001.pdf"

    with pymupdf.open(source) as original:

        with pymupdf.open() as scanned:

            for page in original:

                image = page.get_pixmap(dpi=300)

                new_page = scanned.new_page(
                    width=page.rect.width,
                    height=page.rect.height
                )

                new_page.insert_image(
                    new_page.rect,
                    pixmap=image
                )

            scanned.save(output)

    print(f"Scanned PDF created: {output}")

    with pymupdf.open(output) as document:

        text = "".join(
            page.get_text() for page in document
        )

        print(f"Selectable text characters: {len(text.strip())}")

    return output


if __name__ == "__main__":
    generate_scanned_sample()
