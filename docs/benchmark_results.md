# AI vs. Traditional Automation Benchmark

## Executive Summary

This benchmark evaluates traditional rule-based extraction
against a Large Language Model for financial document
processing.

## Methodology

- Three synthetic financial documents
- Seven evaluated fields per document
- Twenty-one evaluated fields in total
- Traditional method: Python and Regex
- AI method: Gemini 3.1 Flash-Lite
- Financial validation: deterministic business rules
- Evaluation method: exact field matching

## Results

| Metric | Regex | Gemini |
|---|---:|---:|
| Field Accuracy | 66.67% | 100.00% |
| Correct Fields | 14/21 | 21/21 |
| Average Processing Time | 0.000327s | 31.50s |
| Total AI Tokens | 0 | 762 |

## Results by Document

| Document | Regex Accuracy | AI Accuracy | AI Latency |
|---|---:|---:|---:|
| Standard Invoice | 100% | 100% | 2.03s |
| Alternative Invoice | 0% | 100% | 36.91s |
| Missing Supplier | 100% | 100% | 55.54s |

## Key Findings

- Traditional extraction performs well on known formats.
- AI extraction handles alternative document structures.
- Both methods correctly identified missing supplier data.
- AI improved field-level accuracy by 33.33 percentage
  points in this benchmark.
- Traditional extraction was substantially faster.
- AI response latency varied considerably.

## Recommended Architecture

A hybrid processing pipeline combining rule-based extraction
with optional AI fallback.

Traditional automation should remain the first processing
layer. AI should be used selectively for unfamiliar
document formats.

All extracted information must undergo deterministic
financial validation.

## Cost Management

The experiment used the Gemini API free tier.

No paid API usage was authorized.

## Limitations

- Small synthetic dataset.
- Only one AI model evaluated.
- Limited document diversity.
- Results cannot be generalized to all financial documents.
- API latency may vary across requests.
- Structured output does not guarantee factual accuracy.
- PDF extraction time is excluded from the comparison.

## Data Privacy

All documents and financial information used in this
benchmark are synthetic.

No confidential corporate information was processed.
