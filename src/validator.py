from datetime import date
from decimal import Decimal


ALLOWED_CURRENCIES = {"USD", "BRL", "EUR"}


def validate_invoice(invoice: dict) -> list:
    """Validate financial data and return identified issues."""

    errors = []

    required_fields = [
        "supplier",
        "invoice_number",
        "issue_date",
        "due_date",
        "currency",
        "total_amount"
    ]

    for field in required_fields:
        value = invoice.get(field)

        if value is None or value == "":
            errors.append(f"Missing required field: {field}")

    # Validate currency

    currency = invoice.get("currency")

    if currency not in ALLOWED_CURRENCIES:
        errors.append("Invalid or unsupported currency")

    # Validate financial amount

    amount = invoice.get("total_amount")

    if (
        not isinstance(amount, Decimal)
        or not amount.is_finite()
        or amount <= 0
    ):
        errors.append("Total amount must be a positive decimal")

    # Validate dates

    valid_dates = {}

    for field in ["issue_date", "due_date"]:

        try:
            value = invoice.get(field)
            parsed_date = date.fromisoformat(value)

            if parsed_date.isoformat() != value:
                raise ValueError("Invalid date format")

            valid_dates[field] = parsed_date

        except (ValueError, TypeError):
            errors.append(f"Invalid date: {field}")

    if "issue_date" in valid_dates and "due_date" in valid_dates:

        if valid_dates["due_date"] < valid_dates["issue_date"]:
            errors.append("Due date cannot be before issue date")

    return errors


if __name__ == "__main__":

    from extractor import extract_text, DATA_DIR
    from parser import parse_invoice

    text = extract_text(DATA_DIR / "invoice_001.pdf")

    invoice = parse_invoice(text)

    errors = validate_invoice(invoice)

    print("FINANCIAL VALIDATION")

    if errors:
        for error in errors:
            print(error)
    else:
        print("Invoice successfully validated.")
