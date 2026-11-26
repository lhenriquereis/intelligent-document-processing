import json
from collections import Counter

from extractor import extract_text, DATA_DIR
from classifier import classify_document
from parser import parse_invoice
from duplicate_detector import find_duplicates
from validator import validate_invoice


def normalize_text(value: str) -> str:
    """Normalize text for consistent comparisons."""

    return " ".join(value.strip().casefold().split())


def create_business_key(invoice: dict) -> tuple:
    """Create a unique financial identification key."""

    return (
        normalize_text(invoice["supplier"]),
        normalize_text(invoice["invoice_number"])
    )


def process_documents():

    results = []

    seen_invoices = {}

    duplicates = find_duplicates(DATA_DIR)

    duplicate_map = {
        item["duplicate"]: item["original"]
        for item in duplicates
    }

    files = sorted(DATA_DIR.glob("*.pdf"))

    print("=" * 60)
    print("INTELLIGENT DOCUMENT PROCESSING")
    print("=" * 60)

    for file_path in files:

        result = {
            "filename": file_path.name
        }

        try:

            # Detect exact binary duplicates

            if file_path.name in duplicate_map:

                result["status"] = "DUPLICATE"
                result["duplicate_type"] = "FILE_HASH"

                result["duplicate_of"] = duplicate_map[
                    file_path.name
                ]

            else:

                text = extract_text(file_path)

                document_type = classify_document(text)

                result["document_type"] = document_type

                if document_type == "INVOICE":

                    invoice = parse_invoice(text)

                    result["data"] = invoice

                    validation_errors = validate_invoice(invoice)

                    if validation_errors:

                        result["status"] = "VALIDATION_FAILED"
                        result["validation_errors"] = validation_errors

                    else:

                        business_key = create_business_key(invoice)

                        if business_key in seen_invoices:

                            previous = seen_invoices[business_key]

                            result["duplicate_of"] = previous["filename"]

                            financial_fields = [
                                "total_amount",
                                "currency",
                                "issue_date",
                                "due_date"
                            ]

                            conflicts = [
                                field
                                for field in financial_fields
                                if invoice[field] != previous["data"][field]
                            ]

                            if conflicts:

                                result["status"] = "REVIEW_REQUIRED"

                                result["review_reason"] = (
                                    "CONFLICTING_INVOICE_DATA"
                                )

                                result["conflicting_fields"] = conflicts

                            else:

                                result["status"] = "DUPLICATE"

                                result["duplicate_type"] = "BUSINESS_KEY"

                        else:

                            seen_invoices[business_key] = {
                                "filename": file_path.name,
                                "data": invoice
                            }

                            result["status"] = "VALIDATED"

                else:

                    result["status"] = "REVIEW_REQUIRED"

        except Exception as error:

            result["status"] = "ERROR"
            result["error"] = str(error)

        results.append(result)

        print(f"{file_path.name}: {result['status']}")

    summary = Counter(
        item["status"] for item in results
    )

    duplicate_summary = Counter(
        item["duplicate_type"]
        for item in results
        if item["status"] == "DUPLICATE"
    )

    print("\n" + "=" * 60)
    print("PROCESSING SUMMARY")
    print("=" * 60)

    print(f"Total documents: {len(files)}")
    print(f"Validated: {summary['VALIDATED']}")
    print(f"Validation failed: {summary['VALIDATION_FAILED']}")
    print(f"Duplicates: {summary['DUPLICATE']}")
    print(f"Review required: {summary['REVIEW_REQUIRED']}")
    print(f"Errors: {summary['ERROR']}")

    print("\nDUPLICATE BREAKDOWN")

    print(f"File hash duplicates: {duplicate_summary['FILE_HASH']}")
    print(f"Business key duplicates: {duplicate_summary['BUSINESS_KEY']}")

    print("\nDETAILED RESULTS")

    print(json.dumps(results, indent=4, default=str))

    return results


if __name__ == "__main__":
    process_documents()
