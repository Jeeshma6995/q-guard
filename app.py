from pathlib import Path
import tempfile
import pandas as pd
import streamlit as st
from scanner import scan_path
from risk_engine import prioritize, report_summary

st.set_page_config(page_title="Q-Guard | PQC Readiness", page_icon="🛡️", layout="wide")
st.title("🛡️ Q-Guard")
st.subheader("Post-Quantum Cryptography Readiness Scanner")
st.caption(
    "Static-analysis prototype for Python, Java and C source code. "
    "Findings are heuristic indicators, not proof of runtime use or a complete security audit."
)

with st.sidebar:
    st.header("Scan source code")
    mode = st.radio("Input source", ["Built-in demo samples", "Upload source files", "Scan local folder"])
    folder_path = ""
    uploads = []
    if mode == "Scan local folder":
        folder_path = st.text_input("Folder path", value="samples")
        st.caption("Folder must be accessible to the machine running Streamlit.")
    elif mode == "Upload source files":
        uploads = st.file_uploader(
            "Choose .py, .java, .c or .h files",
            type=["py", "java", "c", "h"],
            accept_multiple_files=True,
        )
    run_scan = st.button("🔍 Scan now", type="primary", use_container_width=True)

if "findings" not in st.session_state:
    st.session_state.findings = []
    st.session_state.scanned_files = 0
    st.session_state.scan_error = ""

if run_scan:
    try:
        if mode == "Built-in demo samples":
            path = Path(__file__).parent / "samples"
            count, findings = scan_path(path)
        elif mode == "Scan local folder":
            if not folder_path.strip():
                raise ValueError("Enter a folder path.")
            count, findings = scan_path(folder_path.strip())
        else:
            if not uploads:
                raise ValueError("Upload at least one supported source file.")
            with tempfile.TemporaryDirectory() as tmp:
                for upload in uploads:
                    safe_name = Path(upload.name).name
                    (Path(tmp) / safe_name).write_bytes(upload.getvalue())
                count, findings = scan_path(tmp)

        st.session_state.scanned_files = count
        st.session_state.findings = prioritize(findings)
        st.session_state.scan_error = ""
    except Exception as exc:
        st.session_state.scan_error = str(exc)

if st.session_state.scan_error:
    st.error(st.session_state.scan_error)

findings = st.session_state.findings
summary = report_summary(st.session_state.scanned_files, findings)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Files scanned", summary["files_scanned"])
c2.metric("Potential findings", summary["findings"])
c3.metric("High quantum-risk matches", summary["high_quantum_risk_findings"])
c4.metric("Algorithms detected", len(summary["algorithms_detected"]))

st.divider()
st.markdown("### Findings")

if not findings:
    st.info("Choose an input source and click **Scan now**. Demo samples are included.")
else:
    df = pd.DataFrame(findings)
    filters = st.columns(3)
    algorithms = sorted(df["algorithm"].unique().tolist())
    selected_algorithms = filters[0].multiselect("Algorithm", algorithms, default=algorithms)
    risks = sorted(df["quantum_risk"].unique().tolist())
    selected_risks = filters[1].multiselect("Quantum risk", risks, default=risks)
    languages = sorted(df["language"].unique().tolist())
    selected_languages = filters[2].multiselect("Language", languages, default=languages)

    visible = df[
        df["algorithm"].isin(selected_algorithms)
        & df["quantum_risk"].isin(selected_risks)
        & df["language"].isin(selected_languages)
    ]
    columns = ["file", "line", "language", "algorithm", "quantum_risk", "confidence"]
    st.dataframe(visible[columns], use_container_width=True, hide_index=True)

    st.markdown("### Finding details")
    options = [
        f'{i+1}. {row["algorithm"]} — {Path(row["file"]).name}:{row["line"]}'
        for i, row in visible.reset_index(drop=True).iterrows()
    ]
    if options:
        selected = st.selectbox("Select a finding", options)
        selected_index = int(selected.split(".", 1)[0]) - 1
        item = visible.reset_index(drop=True).iloc[selected_index].to_dict()
        st.markdown(f'**Evidence:** `{item["evidence"]}`')
        st.write(f'**Purpose:** {item["purpose"]}')
        st.write(f'**Confidence:** {item["confidence"]}')
        st.write(f'**Recommendation:** {item["recommendation"]}')

    csv = visible.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered findings (CSV)",
        data=csv,
        file_name="q_guard_findings.csv",
        mime="text/csv",
    )

with st.expander("What this prototype can and cannot tell you"):
    st.markdown("""
- It matches curated API names and patterns in source-code lines.
- A match can be a comment, unused import, test fixture, or unrelated identifier.
- It can miss aliased APIs, wrappers, dynamically constructed calls, dependencies, and code in unsupported languages.
- RSA, finite-field DH, ECDH and ECDSA are vulnerable to a sufficiently capable fault-tolerant quantum computer running Shor's algorithm.
- ML-KEM is for key establishment; ML-DSA and SLH-DSA are for signatures. Migration depends on actual usage and protocol design.
- AES and hash findings need contextual assessment; they should not automatically be classified like RSA/ECC.
- This tool does not automatically modify code and is not a substitute for a security audit.
""")