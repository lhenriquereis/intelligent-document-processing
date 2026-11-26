"""Offline tests for the hybrid extraction routing policy."""
from decimal import InvalidOperation

import pytest
import hybrid_extractor as hybrid
from benchmark import TEST_CASES

STANDARD = TEST_CASES[0]["text"]
ALTERNATIVE = TEST_CASES[1]["text"]
MISSING_SUPPLIER = TEST_CASES[2]["text"]


@pytest.fixture(autouse=True)
def block_real_api_calls(monkeypatch):
    def blocked(*args, **kwargs):
        pytest.fail("Unexpected real API call")
    monkeypatch.setattr(hybrid, "extract_invoice_with_ai", blocked)


def test_standard_uses_regex():
    result = hybrid.extract_invoice_hybrid(STANDARD, allow_ai=True)
    assert result["method"] == "REGEX"
    assert result["status"] == "VALIDATED"
    assert result["ai_attempted"] is False
    assert result["data"] == TEST_CASES[0]["expected"]


def test_missing_supplier_does_not_trigger_ai():
    result = hybrid.extract_invoice_hybrid(MISSING_SUPPLIER, allow_ai=True)
    assert result["method"] == "REGEX"
    assert result["status"] == "VALIDATION_FAILED"
    assert result["ai_attempted"] is False
    assert result["data"]["supplier"] is None


def test_ai_disabled_by_default():
    result = hybrid.extract_invoice_hybrid(ALTERNATIVE)
    assert result["status"] == "REVIEW_REQUIRED"
    assert result["ai_attempted"] is False
    assert result["review_reason"] == "INSUFFICIENT_EXTRACTION_AI_DISABLED"


def test_ai_fallback_success(monkeypatch):
    calls = []
    def mock_ai(text):
        calls.append(text)
        return {"data": TEST_CASES[1]["expected"].copy(), "status": "VALIDATED",
                "validation_errors": [], "metrics": {"total_tokens": 0}}
    monkeypatch.setattr(hybrid, "extract_invoice_with_ai", mock_ai)
    result = hybrid.extract_invoice_hybrid(ALTERNATIVE, allow_ai=True)
    assert result["method"] == "GEMINI"
    assert result["status"] == "VALIDATED"
    assert result["data"] == TEST_CASES[1]["expected"]
    assert calls == [ALTERNATIVE]


def test_ai_failure(monkeypatch):
    def mock_failure(text):
        raise ConnectionError("Simulated failure")
    monkeypatch.setattr(hybrid, "extract_invoice_with_ai", mock_failure)
    result = hybrid.extract_invoice_hybrid(ALTERNATIVE, allow_ai=True)
    assert result["status"] == "REVIEW_REQUIRED"
    assert result["review_reason"] == "AI_FALLBACK_FAILED"
    assert result["ai_attempted"] is True


def test_parser_decimal_exception(monkeypatch):
    def invalid_amount(text):
        raise InvalidOperation("Simulated invalid amount")
    monkeypatch.setattr(hybrid, "parse_invoice", invalid_amount)
    result = hybrid.extract_invoice_hybrid(STANDARD, allow_ai=True)
    assert result["status"] == "REVIEW_REQUIRED"
    assert result["ai_attempted"] is False
    assert "Invalid monetary amount" in result["validation_errors"]
