from pathlib import Path
from collections import Counter

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from main import process_documents


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


HEADERS = [
    "Filename",
    "Document Type",
    "Status",
    "Supplier",
    "Invoice Number",
    "Issue Date",
    "Due Date",
    "Description",
    "Currency",
    "Total Amount",
    "Duplicate Type",
    "Duplicate Of",
    "Validation Errors",
    "Review Reason",
    "Conflicting Fields",
    "Technical Error",
    "Open Conflict"
]


def append_safe(sheet, values):
    """Write values without interpreting text as formulas."""

    sheet.append(values)

    for cell in sheet[sheet.max_row]:

        if isinstance(cell.value, str):
            cell.data_type = "s"


def format_sheet(sheet):
    """Apply professional spreadsheet formatting."""

    for cell in sheet[1]:

        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="17365D"
        )

        cell.font = Font(
            color="FFFFFF",
            bold=True
        )

        cell.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

    sheet.row_dimensions[1].height = 25

    sheet.freeze_panes = "A2"

    sheet.auto_filter.ref = sheet.dimensions

    status_colors = {
        "VALIDATED": "E2F0D9",
        "DUPLICATE": "FFF2CC",
        "VALIDATION_FAILED": "FCE4D6",
        "REVIEW_REQUIRED": "DDEBF7",
        "ERROR": "FFC7CE"
    }

    for row in sheet.iter_rows(min_row=2):

        for cell in row:

            if (
                isinstance(cell.value, str)
                and cell.value in status_colors
            ):

                cell.fill = PatternFill(
                    fill_type="solid",
                    fgColor=status_colors[cell.value]
                )

    for column in sheet.columns:

        max_length = 0

        for cell in column:

            if cell.value is not None:

                max_length = max(
                    max_length,
                    len(str(cell.value))
                )

        column_letter = get_column_letter(
            column[0].column
        )

        sheet.column_dimensions[column_letter].width = min(
            max(max_length + 3, 15),
            65
        )


def document_to_row(result, conflict_names):
    """Convert a processing result into an Excel row."""

    data = result.get("data", {})

    amount = data.get("total_amount")

    if amount is not None and amount.is_finite():

        amount = float(amount)

    elif amount is not None:

        amount = str(amount)

    return [
        result.get("filename"),
        result.get("document_type"),
        result.get("status"),
        data.get("supplier"),
        data.get("invoice_number"),
        data.get("issue_date"),
        data.get("due_date"),
        data.get("description"),
        data.get("currency"),
        amount,
        result.get("duplicate_type"),
        result.get("duplicate_of"),
        "; ".join(result.get("validation_errors", [])),
        result.get("review_reason"),
        "; ".join(result.get("conflicting_fields", [])),
        result.get("error"),
        "YES" if result["filename"] in conflict_names else "NO"
    ]


def create_document_sheet(
    workbook,
    name,
    results,
    conflict_names
):

    sheet = workbook.create_sheet(name)

    append_safe(sheet, HEADERS)

    for result in results:

        append_safe(
            sheet,
            document_to_row(result, conflict_names)
        )

        sheet.cell(
            row=sheet.max_row,
            column=10
        ).number_format = '#,##0.00'

    format_sheet(sheet)

    return sheet


def export_results(results):

    workbook = Workbook()

    summary_sheet = workbook.active
    summary_sheet.title = "Summary"

    status_counts = Counter(
        result["status"] for result in results
    )

    # Identify original invoices with conflicting copies

    conflict_names = set()

    for result in results:

        if (
            result.get("review_reason")
            == "CONFLICTING_INVOICE_DATA"
        ):

            conflict_names.add(result["filename"])

            if result.get("duplicate_of"):

                conflict_names.add(result["duplicate_of"])

    validated = [
        result for result in results
        if result["status"] == "VALIDATED"
        and result["filename"] not in conflict_names
    ]

    duplicates = [
        result for result in results
        if result["status"] == "DUPLICATE"
    ]

    validation_issues = [
        result for result in results
        if result["status"] == "VALIDATION_FAILED"
    ]

    review_required = [
        result for result in results
        if result["status"] == "REVIEW_REQUIRED"
        or (
            result["status"] == "VALIDATED"
            and result["filename"] in conflict_names
        )
    ]

    errors = [
        result for result in results
        if result["status"] == "ERROR"
    ]

    summary_rows = [
        ["Metric", "Value"],
        ["Total Documents", len(results)],
        ["Rule Validated", status_counts["VALIDATED"]],
        ["Validated Without Conflict", len(validated)],
        ["Duplicates", len(duplicates)],
        ["Validation Failed", len(validation_issues)],
        ["Review Required", len(review_required)],
        ["Technical Errors", len(errors)],
        [
            "File Hash Duplicates",
            sum(
                result.get("duplicate_type") == "FILE_HASH"
                for result in duplicates
            )
        ],
        [
            "Business Key Duplicates",
            sum(
                result.get("duplicate_type") == "BUSINESS_KEY"
                for result in duplicates
            )
        ]
    ]

    for row in summary_rows:

        append_safe(summary_sheet, row)

    format_sheet(summary_sheet)

    report_groups = {
        "All Documents": results,
        "Validated": validated,
        "Duplicates": duplicates,
        "Validation Issues": validation_issues,
        "Review Required": review_required,
        "Errors": errors
    }

    for name, documents in report_groups.items():

        create_document_sheet(
            workbook,
            name,
            documents,
            conflict_names
        )

    output_path = OUTPUT_DIR / "processing_report.xlsx"

    workbook.save(output_path)

    print("\n" + "=" * 60)
    print("EXCEL REPORT GENERATED")
    print("=" * 60)

    print(f"Report: {output_path}")
    print(f"Worksheets: {len(workbook.sheetnames)}")

    return output_path


if __name__ == "__main__":

    results = process_documents()

    export_results(results)
