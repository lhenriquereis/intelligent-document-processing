from generate_samples import create_pdf


def generate_duplicate_samples():

    # Same invoice with different PDF content

    create_pdf(
        "invoice_002_reissued.pdf",
        "SAMPLE INVOICE - REISSUED COPY\n\n"
        "Supplier: Demo Logistics Ltd\n"
        "Invoice Number: INV-002\n"
        "Issue Date: 2026-11-05\n"
        "Due Date: 2026-12-05\n"
        "Description: Transportation Services\n"
        "Currency: USD\n"
        "Total Amount: 850.00\n"
    )

    # Same invoice number with a conflicting amount

    create_pdf(
        "invoice_002_review.pdf",
        "SAMPLE INVOICE - REVISED COPY\n\n"
        "Supplier: Demo Logistics Ltd\n"
        "Invoice Number: INV-002\n"
        "Issue Date: 2026-11-05\n"
        "Due Date: 2026-12-05\n"
        "Description: Transportation Services\n"
        "Currency: USD\n"
        "Total Amount: 950.00\n"
    )

    print("\nBusiness duplicate samples created.")


if __name__ == "__main__":
    generate_duplicate_samples()
