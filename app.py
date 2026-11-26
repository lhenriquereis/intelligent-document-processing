"""Local portfolio demonstration for intelligent invoice extraction."""
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from benchmark import TEST_CASES, generate_benchmark_pdf
from extractor import extract_text
from hybrid_extractor import extract_invoice_hybrid

st.set_page_config(page_title="Intelligent Document Processing", page_icon="📄", layout="wide")
st.title("Intelligent Document Processing")
st.caption("Python · OCR · Regex · Gemini · Financial validation")

with st.sidebar:
    st.header("Processing options")
    mode = st.radio("Document source", ["Synthetic demo", "Local PDF upload"])
    allow_ai = False
    if mode == "Synthetic demo":
        selected = st.selectbox("Sample invoice", range(len(TEST_CASES)),
                                format_func=lambda i: TEST_CASES[i]["filename"])
        allow_ai = st.checkbox("Enable Gemini fallback (free tier only)", value=False)
        if allow_ai:
            st.warning("Only the built-in synthetic sample may be sent to Gemini. Keep billing disabled.")
        source_id = (mode, selected, allow_ai)
        upload = None
    else:
        upload = st.file_uploader("Upload a synthetic invoice", type=["pdf"])
        st.info("Local processing only. Uploaded files are never sent to Gemini by this app.")
        source_id = (mode, upload.name, upload.size, upload.file_id) if upload else (mode,)
    run = st.button("Process invoice", type="primary", disabled=(mode == "Local PDF upload" and upload is None))

if run:
    st.session_state.pop("idp_result", None)
    try:
        with st.spinner("Extracting and validating invoice..."):
            if mode == "Synthetic demo":
                path = generate_benchmark_pdf(TEST_CASES[selected])
                text = extract_text(path)
                name = path.name
            else:
                name = upload.name
                with TemporaryDirectory() as tmp:
                    path = Path(tmp) / "invoice.pdf"
                    path.write_bytes(upload.getvalue())
                    text = extract_text(path)
            result = extract_invoice_hybrid(text, allow_ai=allow_ai)
            result["filename"] = name
        st.session_state["idp_result"] = (source_id, result)
    except Exception as exc:
        st.error(f"Processing failed ({type(exc).__name__}). Check the PDF and local configuration.")

stored = st.session_state.get("idp_result")
if stored and stored[0] == source_id:
    result = stored[1]
    status = result.get("status", "UNKNOWN")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Extraction method", result.get("method", "—"))
    c2.metric("Validation", status.replace("_", " "))
    c3.metric("AI attempted", "Yes" if result.get("ai_attempted") else "No")
    elapsed = result.get("processing_time_seconds")
    c4.metric("Processing time", f"{elapsed:.3f} s" if elapsed is not None else "—")
    if status == "VALIDATED":
        st.success("Extracted fields satisfy the configured business rules. This is not a payment approval.")
    else:
        st.warning("Review required before business use.")
    st.subheader("Extracted fields")
    st.table([{"Field": key.replace("_", " ").title(), "Value": str(value) if value is not None else "Missing"}
              for key, value in result.get("data", {}).items()])
    errors = result.get("validation_errors", [])
    if errors:
        st.subheader("Validation issues")
        for error in errors:
            st.write(error)
    if result.get("review_reason"):
        st.caption(result["review_reason"])
    payload = json.dumps(result, indent=2, default=str)
    with st.expander("Structured JSON"):
        st.code(payload, language="json")
    st.download_button("Download JSON report", payload, file_name="invoice_result.json", mime="application/json")
else:
    st.info("Choose a sample invoice or upload a synthetic PDF and click Process invoice.")

st.divider()
st.subheader("Measured benchmark")
st.caption("Three synthetic invoices; 21 fields. Timings exclude PDF extraction. Not a production accuracy estimate.")
st.table([
    {"Method": "Regex", "Field accuracy": "66.67%", "AI requests": 0, "AI tokens": 0},
    {"Method": "Gemini", "Field accuracy": "100%", "AI requests": 3, "AI tokens": 762},
    {"Method": "Hybrid", "Field accuracy": "100%", "AI requests": 1, "AI tokens": 255},
])
st.caption("This demo processes individual invoices. Batch deduplication and Excel reporting remain in the original CLI pipeline.")
