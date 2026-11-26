import argparse
import json
import time
from decimal import InvalidOperation

from extractor import extract_text
from parser import parse_invoice
from validator import validate_invoice
from ai_extractor import extract_invoice_with_ai


REQUIRED_FIELDS = [
    "supplier",
    "invoice_number",
    "issue_date",
    "due_date",
    "currency",
    "total_amount"
]


def extract_invoice_hybrid(text: str, allow_ai=False):

    start_time = time.perf_counter()

    # Step 1: Traditional extraction

    try:

        invoice = parse_invoice(text)

    except InvalidOperation:

        return {
            "method": "REGEX",
            "status": "REVIEW_REQUIRED",
            "data": {},
            "validation_errors": [
                "Invalid monetary amount"
            ],
            "ai_attempted": False
        }

    validation_errors = validate_invoice(invoice)

    missing_fields = [
        field
        for field in REQUIRED_FIELDS
        if invoice.get(field) is None
        or invoice.get(field) == ""
    ]

    result = {
        "method": "REGEX",
        "data": invoice,
        "status": (
            "VALIDATION_FAILED"
            if validation_errors
            else "VALIDATED"
        ),
        "validation_errors": validation_errors,
        "missing_fields": missing_fields,
        "ai_attempted": False
    }

    # Step 2: Decide whether AI is necessary

    if len(missing_fields) >= 2:

        if not allow_ai:

            result["status"] = "REVIEW_REQUIRED"

            result["review_reason"] = (
                "INSUFFICIENT_EXTRACTION_AI_DISABLED"
            )

        else:

            result["ai_attempted"] = True

            print("AI fallback activated...", flush=True)

            try:

                ai_result = extract_invoice_with_ai(text)

                result = {
                    "method": "GEMINI",
                    "data": ai_result["data"],
                    "status": ai_result["status"],
                    "validation_errors": (
                        ai_result["validation_errors"]
                    ),
                    "ai_attempted": True,
                    "metrics": ai_result["metrics"]
                }

            except Exception as error:

                result["status"] = "REVIEW_REQUIRED"

                result["review_reason"] = "AI_FALLBACK_FAILED"

                result["error_type"] = type(error).__name__

    result["processing_time_seconds"] = round(
        time.perf_counter() - start_time, 6
    )

    return result


def run_demo(allow_ai=False):

    from benchmark import (
        TEST_CASES,
        generate_benchmark_pdf
    )

    results = []

    print("=" * 60)
    print("HYBRID AI DOCUMENT PROCESSING")
    print("=" * 60)

    print(f"AI enabled: {allow_ai}")

    for test_case in TEST_CASES:

        pdf_path = generate_benchmark_pdf(test_case)

        text = extract_text(pdf_path)

        print(f"\nDocument: {pdf_path.name}")

        result = extract_invoice_hybrid(
            text,
            allow_ai=allow_ai
        )

        result["filename"] = pdf_path.name

        results.append(result)

        print(json.dumps(
            result,
            indent=4,
            default=str
        ))

    regex_count = sum(
        result["method"] == "REGEX"
        for result in results
    )

    ai_count = sum(
        result["method"] == "GEMINI"
        for result in results
    )

    api_attempts = sum(
        result["ai_attempted"]
        for result in results
    )

    print("\n" + "=" * 60)
    print("HYBRID PROCESSING SUMMARY")
    print("=" * 60)

    print(f"Total documents: {len(results)}")
    print(f"Regex processed: {regex_count}")
    print(f"AI processed: {ai_count}")
    print(f"AI requests attempted: {api_attempts}")

    print("Billing policy: Free tier only.")

    return results


if __name__ == "__main__":

    cli = argparse.ArgumentParser(
        description="Hybrid financial document extraction."
    )

    cli.add_argument(
        "--enable-ai",
        action="store_true",
        help="Enable AI fallback for synthetic documents."
    )

    args = cli.parse_args()

    run_demo(allow_ai=args.enable_ai)
