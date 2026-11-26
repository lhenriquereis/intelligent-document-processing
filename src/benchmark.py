import time
from decimal import Decimal
from pathlib import Path

import pymupdf

from extractor import extract_text
from parser import parse_invoice
from validator import validate_invoice
from ai_extractor import extract_invoice_with_ai


BASE_DIR = Path(__file__).resolve().parent.parent
BENCHMARK_DIR = BASE_DIR / "data" / "benchmark_samples"


TEST_CASES = [
    {
        "filename": "standard_invoice.pdf",
        "text": (
            "SAMPLE INVOICE\n"
            "Supplier: Example Technology Ltd\n"
            "Invoice Number: INV-001\n"
            "Issue Date: 2026-11-01\n"
            "Due Date: 2026-12-01\n"
            "Description: Software Subscription\n"
            "Currency: USD\n"
            "Total Amount: 1250.00\n"
        ),
        "expected": {
            "supplier": "Example Technology Ltd",
            "invoice_number": "INV-001",
            "issue_date": "2026-11-01",
            "due_date": "2026-12-01",
            "description": "Software Subscription",
            "currency": "USD",
            "total_amount": Decimal("1250.00")
        }
    },
    {
        "filename": "alternative_invoice.pdf",
        "text": (
            "SAMPLE INVOICE\n"
            "Vendor: Demo Logistics Ltd\n"
            "Bill Reference: INV-002\n"
            "Issued On: November 5, 2026\n"
            "Pay By: December 5, 2026\n"
            "Services: Transportation Services\n"
            "Billing Currency: USD\n"
            "Amount Payable: USD 850.00\n"
        ),
        "expected": {
            "supplier": "Demo Logistics Ltd",
            "invoice_number": "INV-002",
            "issue_date": "2026-11-05",
            "due_date": "2026-12-05",
            "description": "Transportation Services",
            "currency": "USD",
            "total_amount": Decimal("850.00")
        }
    },
    {
        "filename": "missing_supplier_invoice.pdf",
        "text": (
            "SAMPLE INVOICE\n"
            "Invoice Number: INV-003\n"
            "Issue Date: 2026-11-12\n"
            "Due Date: 2026-12-12\n"
            "Description: Office Equipment\n"
            "Currency: USD\n"
            "Total Amount: 700.00\n"
        ),
        "expected": {
            "supplier": None,
            "invoice_number": "INV-003",
            "issue_date": "2026-11-12",
            "due_date": "2026-12-12",
            "description": "Office Equipment",
            "currency": "USD",
            "total_amount": Decimal("700.00")
        }
    }
]


def generate_benchmark_pdf(test_case):

    BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)

    output = BENCHMARK_DIR / test_case["filename"]

    with pymupdf.open() as document:

        page = document.new_page()

        page.insert_text(
            (50, 70),
            test_case["text"],
            fontsize=12
        )

        document.save(output)

    return output


def evaluate_accuracy(actual, expected):

    correct_fields = 0
    incorrect_fields = []

    for field, expected_value in expected.items():

        actual_value = actual.get(field)

        if actual_value == expected_value:
            correct_fields += 1

        else:
            incorrect_fields.append(field)

    total_fields = len(expected)

    return {
        "correct": correct_fields,
        "total": total_fields,
        "accuracy": correct_fields / total_fields * 100,
        "incorrect_fields": incorrect_fields
    }


def run_benchmark():

    results = []

    print("=" * 60)
    print("REGEX VS GEMINI - PERFORMANCE BENCHMARK")
    print("=" * 60)

    for test_case in TEST_CASES:

        pdf_path = generate_benchmark_pdf(test_case)

        text = extract_text(pdf_path)

        expected = test_case["expected"]

        print("\n" + "-" * 60)
        print(f"Document: {pdf_path.name}")
        print("-" * 60)

        # Traditional extraction

        start = time.perf_counter()

        regex_data = parse_invoice(text)
        regex_errors = validate_invoice(regex_data)

        regex_time = time.perf_counter() - start

        regex_score = evaluate_accuracy(
            regex_data,
            expected
        )

        # AI extraction

        print("Sending synthetic text to Gemini...", flush=True)

        start = time.perf_counter()

        try:

            ai_result = extract_invoice_with_ai(text)

        except Exception as error:

            print(f"API or extraction error: {type(error).__name__}")
            print("Benchmark stopped. No further API calls.")

            break

        ai_time = time.perf_counter() - start

        ai_score = evaluate_accuracy(
            ai_result["data"],
            expected
        )

        tokens = ai_result["metrics"]["total_tokens"]

        result = {
            "filename": pdf_path.name,
            "regex": regex_score,
            "ai": ai_score,
            "regex_time": regex_time,
            "ai_time": ai_time,
            "tokens": tokens
        }

        results.append(result)

        print("\nREGEX RESULTS")

        print(f"Accuracy: {regex_score['accuracy']:.2f}%")
        print(f"Processing time: {regex_time:.6f}s")
        print(f"Incorrect fields: {regex_score['incorrect_fields']}")
        print(f"Validation errors: {regex_errors}")

        print("\nGEMINI RESULTS")

        print(f"Accuracy: {ai_score['accuracy']:.2f}%")
        print(f"Processing time: {ai_time:.2f}s")
        print(f"Incorrect fields: {ai_score['incorrect_fields']}")
        print(f"Validation errors: {ai_result['validation_errors']}")
        print(f"Total tokens: {tokens}")

    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)

    if not results:

        print("No completed comparisons.")

        return results

    total_fields = sum(
        result["regex"]["total"]
        for result in results
    )

    regex_correct = sum(
        result["regex"]["correct"]
        for result in results
    )

    ai_correct = sum(
        result["ai"]["correct"]
        for result in results
    )

    regex_accuracy = regex_correct / total_fields * 100

    ai_accuracy = ai_correct / total_fields * 100

    regex_average_time = sum(
        result["regex_time"]
        for result in results
    ) / len(results)

    ai_average_time = sum(
        result["ai_time"]
        for result in results
    ) / len(results)

    token_values = [
        result["tokens"]
        for result in results
    ]

    print(f"Completed comparisons: {len(results)}/{len(TEST_CASES)}")
    print(f"Total evaluated fields: {total_fields}")

    print(f"Regex accuracy: {regex_accuracy:.2f}%")
    print(f"Gemini accuracy: {ai_accuracy:.2f}%")

    print(f"Regex average time: {regex_average_time:.6f}s")
    print(f"Gemini average time: {ai_average_time:.2f}s")

    if all(value is not None for value in token_values):

        print(f"Total AI tokens: {sum(token_values)}")

    else:

        print("Total AI tokens: unavailable")

    print("\nBilling policy: Free tier only.")
    print("No paid API usage authorized.")

    return results


if __name__ == "__main__":
    run_benchmark()
