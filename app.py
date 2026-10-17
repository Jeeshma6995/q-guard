from pathlib import Path
import tempfile

import pandas as pd
import streamlit as st

from scanner import scan_path
from risk_engine import prioritize, report_summary


# ---------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="Q-Guard | PQC Readiness",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Remove Streamlit's default light header strip and keep the whole app dark. */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: #0b1220 !important;
        color: #e8eefb !important;
    }
    [data-testid="stHeader"], [data-testid="stToolbar"] {
        background: rgba(11, 18, 32, 0) !important;
        color: #e8eefb !important;
    }
    [data-testid="stHeader"] { height: 0rem !important; }
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 0.75rem !important;
    }
    [data-testid="stHeader"], header[data-testid="stHeader"] {
    background: transparent !important;
    height: 3rem !important;
    min-height: 3rem !important;
    display: flex !important;
    }
    [data-testid="stAppViewContainer"] > .main { background: #0b1220 !important; }
    .stApp > header { background: transparent !important; }
    [data-testid="stDecoration"] { display: none !important; }
    .main, .main .block-container {
        background: transparent !important;
        color: #e8eefb !important;
    }
    /* Ensure default text widgets retain readable contrast on the dark canvas. */
    .stMarkdown, .stText, .stCaption, p, label, [data-testid="stWidgetLabel"] {
        color: #e8eefb;
    }
    [data-testid="stSidebar"] {
        background: #0b1426 !important;
        border-right: 1px solid rgba(120, 160, 220, 0.18);
    }
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span { color: #e8eefb !important; }
    [data-testid="stSidebar"] * { color: #e8eefb; }
    .qg-hero {
        padding: 1.35rem 1.5rem;
        border: 1px solid rgba(96, 165, 250, .25);
        border-radius: 18px;
        background: linear-gradient(120deg, rgba(30, 64, 120, .55), rgba(15, 23, 42, .85));
        margin-bottom: 1.1rem;
    }
    .qg-eyebrow {
        color: #7dd3fc;
        font-size: .78rem;
        font-weight: 700;
        letter-spacing: .13em;
        text-transform: uppercase;
    }
    .qg-title {
        font-size: 2.15rem;
        font-weight: 800;
        line-height: 1.15;
        margin: .25rem 0 .45rem 0;
        color: #f8fafc;
    }
    .qg-subtitle { color: #c1cee3; font-size: 1rem; }
    .qg-panel {
        padding: 1rem 1.1rem;
        border-radius: 15px;
        border: 1px solid rgba(148, 163, 184, .18);
        background: rgba(15, 27, 47, .88);
        min-height: 116px;
    }
    .qg-panel-label {
        color: #aabbd4;
        font-size: .86rem;
        margin-bottom: .55rem;
    }
    .qg-panel-value {
        color: #f8fafc;
        font-size: 1.9rem;
        font-weight: 800;
        line-height: 1.2;
    }
    .qg-panel-note { color: #7dd3fc; font-size: .78rem; margin-top: .45rem; }
    .qg-status-card { display: flex; flex-direction: column; gap: .8rem; min-height: 0; }
    .qg-status-banner { color: #f8fafc; padding: .75rem .85rem; border-radius: 10px; font-weight: 750; }
    .qg-status-row { display: flex; justify-content: space-between; align-items: flex-start; gap: .8rem; padding-bottom: .55rem; border-bottom: 1px solid rgba(148,163,184,.18); }
    .qg-status-row span { color: #cbd5e1; }
    .qg-status-row strong { color: #f8fafc; text-align: right; overflow-wrap: anywhere; }
    .qg-status-note { color: #cbd5e1; font-size: .85rem; line-height: 1.45; }
    .qg-algorithms-card { color: #f8fafc; line-height: 1.6; overflow-wrap: anywhere; }
    .qg-section {
        color: #f1f5f9;
        font-size: 1.25rem;
        font-weight: 750;
        margin: .6rem 0 .25rem 0;
    }
    .qg-muted { color: #aabbd4; font-size: .88rem; }
    div[data-testid="stMetric"] {
        background: rgba(15, 27, 47, .88);
        border: 1px solid rgba(148, 163, 184, .18);
        border-radius: 14px;
        padding: 1rem;
    }
    div[data-testid="stMetricLabel"] { color: #b7c7df; }
    div[data-testid="stMetricValue"] { color: #f8fafc; }
    div[data-testid="stDataFrame"], div[data-testid="stTable"] {
        border: 1px solid #334155;
        border-radius: 12px;
        overflow: hidden;
        background: #f8fafc !important;
    }
    /* File uploader dropzone and controls: force accessible contrast. */
    [data-testid="stFileUploader"] section {
        background: #17243a !important; border: 1px solid #64748b !important;
        border-radius: 12px !important;
    }
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] section * { color: #f8fafc !important; }
    [data-testid="stFileUploader"] button {
        background: #e2e8f0 !important; color: #172033 !important;
        border: 1px solid #94a3b8 !important;
    }
    [data-testid="stFileUploader"] small { color: #cbd5e1 !important; }
    /* Inputs and select boxes: dark field with light, readable text. */
    [data-baseweb="select"] > div, [data-baseweb="input"] > div,
    [data-testid="stFileUploader"] section {
        background: #17243a !important;
        color: #f8fafc !important;
        border-color: #64748b !important;
    }
    [data-baseweb="select"] *, [data-baseweb="input"] input,
    [data-testid="stFileUploader"] *, [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input, textarea {
        color: #f8fafc !important;
    }
    [data-baseweb="popover"], [data-baseweb="menu"],
    [role="listbox"], [role="option"] {
        background: #17243a !important;
        color: #f8fafc !important;
    }
    [role="option"]:hover { background: #263b59 !important; }
    [data-testid="stMetricLabel"] p, [data-testid="stMetricValue"] div {
        color: #f8fafc !important;
    }
    [data-testid="stAlert"] { color: #f8fafc !important; }
    .stButton > button[kind="primary"] {
        background: #2563eb;
        border: 1px solid #3b82f6;
        border-radius: 10px;
        font-weight: 700;
    }
    .stDownloadButton > button {
        border-radius: 9px;
        border: 1px solid #3b82f6;
    }
    hr { border-color: rgba(148, 163, 184, .2); }

    /* Make the file uploader visibly readable */
[data-testid="stFileUploader"] {
    background-color: #102b3a !important;
    border: 2px solid #35c9d0 !important;
    border-radius: 14px !important;
    padding: 14px !important;
}

/* Make the upload dropzone visible */
[data-testid="stFileUploader"] section {
    background-color: #183c4c !important;
    border: 2px dashed #35c9d0 !important;
    border-radius: 12px !important;
}

/* Fix invisible Browse files button */
[data-testid="stFileUploader"] button {
    background-color: #00bcd4 !important;
    color: #071923 !important;
    border: 1px solid #00e5ff !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}

/* Ensure uploader instructions are readable */
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] section div {
    color: #f5f7fa !important;
}

/* Keep the upload icon visible */
[data-testid="stFileUploader"] svg {
    fill: #35c9d0 !important;
    color: #35c9d0 !important;
}
/* Make uploaded file names readable */
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {
    background-color: #183c4c !important;
    border: 1px solid #35c9d0 !important;
    border-radius: 8px !important;
}

/* Force readable text inside uploaded-file rows */
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] * {
    color: #ffffff !important;
}

/* Keep file names clearly visible */
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] small,
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] span,
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] p {
    color: #ffffff !important;
    opacity: 1 !important;
}

/* Keep file action icons visible */
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] svg {
    color: #35c9d0 !important;
    fill: #35c9d0 !important;
}
/* Fix pale boxes and invisible text throughout Q-Guard */
.stAlert,
[data-testid="stAlert"],
[data-testid="stExpander"],
[data-testid="stExpander"] details,
[data-testid="stExpander"] summary,
[data-testid="stMarkdownContainer"] blockquote {
    color: #f5f7fa !important;
}

/* Keep alert and information-box text readable */
.stAlert p,
[data-testid="stAlert"] p,
[data-testid="stAlert"] span {
    color: #f5f7fa !important;
}

/* Make expanders dark with readable text */
[data-testid="stExpander"] details {
    background-color: #102b3a !important;
    border: 1px solid #35c9d0 !important;
    border-radius: 10px !important;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    color: #f5f7fa !important;
}

/* Fix pale information boxes created with custom HTML */
.qguard-info,
.info-box,
.quantum-risk-box {
    background-color: #183c4c !important;
    color: #f5f7fa !important;
    border: 1px solid #35c9d0 !important;
    border-radius: 10px !important;
    padding: 14px !important;
}

.qguard-info *,
.info-box *,
.quantum-risk-box * {
    color: #f5f7fa !important;
}

/* Keep expandable boxes dark in every interaction state */
[data-testid="stExpander"],
[data-testid="stExpander"] details,
[data-testid="stExpander"] details[open],
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary:hover,
[data-testid="stExpander"] summary:focus,
[data-testid="stExpander"] summary:active {
    background-color: #102b3a !important;
    color: #f5f7fa !important;
}

/* Keep the clickable heading readable */
[data-testid="stExpander"] summary *,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    color: #f5f7fa !important;
}

/* Keep the expanded content dark with readable text */
[data-testid="stExpander"] details > div,
[data-testid="stExpander"] details > div > div,
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    background-color: #102b3a !important;
    color: #f5f7fa !important;
}

/* Prevent text from fading or turning dark */
[data-testid="stExpander"] p,
[data-testid="stExpander"] li,
[data-testid="stExpander"] strong,
[data-testid="stExpander"] span {
    color: #f5f7fa !important;
    opacity: 1 !important;
}

/* Preserve visible borders */
[data-testid="stExpander"] details {
    border: 1px solid #35c9d0 !important;
    border-radius: 10px !important;
}

/* Fix invisible evidence text boxes in Findings & Reports */
[data-testid="stCode"],
[data-testid="stCode"] pre,
[data-testid="stCode"] code,
.stCode,
.stCode pre,
.stCode code {
    background-color: #102b3a !important;
    color: #f5f7fa !important;
    border: 1px solid #35c9d0 !important;
    border-radius: 8px !important;
}

/* Force readable text inside nested code elements */
[data-testid="stCode"] *,
.stCode * {
    color: #f5f7fa !important;
    opacity: 1 !important;
}

/* Preserve whitespace and make evidence readable */
[data-testid="stCode"] pre,
.stCode pre {
    white-space: pre-wrap !important;
    overflow-wrap: anywhere !important;
}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "findings" not in st.session_state:
    st.session_state.findings = []
if "scanned_files" not in st.session_state:
    st.session_state.scanned_files = 0
if "scan_error" not in st.session_state:
    st.session_state.scan_error = ""
if "has_scanned" not in st.session_state:
    st.session_state.has_scanned = False
if "last_scan_source" not in st.session_state:
    st.session_state.last_scan_source = "Not scanned yet"


# ---------------------------------------------------------
# SIDEBAR: SCANNER INPUTS + APP NAVIGATION
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## 🛡️ Q-Guard")
    st.caption("Scan • Detect • Stay Ahead")
    st.divider()

    page = st.radio(
        "Navigation",
        ["Dashboard", "Scan Files", "Findings & Reports", "Quantum Risk Guide", "Migration Roadmap"],
        index=0,
    )

    st.divider()
    st.markdown("### Scan source")
    mode = st.radio(
        "Input source",
        ["Built-in demo samples", "Upload source files"],
        key="input_mode",
    )

    uploads = []

    if mode == "Upload source files":
        uploads = st.file_uploader(
            "Choose source files",
            type=["py", "java", "c", "h"],
            accept_multiple_files=True,
            help="Supported extensions: .py, .java, .c and .h",
        )

    run_scan = st.button(
        "🔍 Scan now",
        type="primary",
        use_container_width=True,
    )

    st.divider()
    st.caption("Q-Guard • Post-Quantum Cryptography Readiness")
    st.caption("Static-analysis prototype — findings need human review.")


# ---------------------------------------------------------
# RUN THE EXISTING SCANNER
# ---------------------------------------------------------
if run_scan:
    try:
        with st.spinner("Scanning source code and analysing potential findings..."):
            if mode == "Built-in demo samples":
                path = Path(__file__).parent / "samples"
                count, raw_findings = scan_path(path)

            else:
                if not uploads:
                    raise ValueError("Upload at least one supported source file.")

                with tempfile.TemporaryDirectory() as tmp:
                    for upload in uploads:
                        safe_name = Path(upload.name).name
                        destination = Path(tmp) / safe_name
                        destination.write_bytes(upload.getvalue())

                    count, raw_findings = scan_path(tmp)

            st.session_state.scanned_files = count
            st.session_state.findings = prioritize(raw_findings)
            st.session_state.scan_error = ""
            st.session_state.has_scanned = True
            st.session_state.last_scan_source = mode

    except Exception as exc:
        st.session_state.scan_error = str(exc)

if st.session_state.scan_error:
    st.error(f"Scan could not be completed: {st.session_state.scan_error}")

findings = st.session_state.findings
summary = report_summary(st.session_state.scanned_files, findings)
df = pd.DataFrame(findings)


# ---------------------------------------------------------
# SHARED DASHBOARD HELPERS
# ---------------------------------------------------------
def metric_card(label, value, note, icon):
    st.markdown(
        f"""
        <div class="qg-panel">
            <div class="qg-panel-label">{icon} &nbsp; {label}</div>
            <div class="qg-panel-value">{value}</div>
            <div class="qg-panel-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_metrics():
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Files scanned", summary["files_scanned"], "Files processed", "📄")
    with c2:
        metric_card("Potential findings", summary["findings"], "Matches to review", "🔎")
    with c3:
        metric_card(
            "High quantum-risk matches",
            summary["high_quantum_risk_findings"],
            "Based on scanner classifications",
            "⚛️",
        )
    with c4:
        metric_card(
            "Algorithms detected",
            len(summary["algorithms_detected"]),
            "Distinct algorithm labels",
            "🔐",
        )


def show_readable_dataframe(dataframe, **kwargs):
    """Render tables with dark text on a light background for reliable contrast."""
    if dataframe is None:
        st.info("No data to display.")
        return
    try:
        styled = dataframe.style.set_properties(
            **{"color": "#172033", "background-color": "#f8fafc"}
        ).set_table_styles([
            {"selector": "th", "props": [
                ("color", "#ffffff"), ("background-color", "#1e3a5f"),
                ("font-weight", "700"), ("border-color", "#cbd5e1")
            ]},
            {"selector": "td", "props": [
                ("color", "#172033"), ("background-color", "#f8fafc"),
                ("border-color", "#cbd5e1")
            ]},
        ])
        st.dataframe(styled, **kwargs)
    except Exception:
        # Fallback keeps the app usable on older pandas/Streamlit versions.
        st.dataframe(dataframe, **kwargs)


def show_finding_filters(dataframe, key_prefix="findings"):
    if dataframe.empty:
        st.info("No findings to display yet. Run a scan to populate this section.")
        return pd.DataFrame()

    # Use safe defaults if a finding record is missing an expected field.
    display_df = dataframe.copy()
    for column in ["file", "line", "language", "algorithm", "quantum_risk", "confidence"]:
        if column not in display_df.columns:
            display_df[column] = "Unknown"

    a, b, c = st.columns(3)
    algorithms = sorted(display_df["algorithm"].fillna("Unknown").astype(str).unique())
    risks = sorted(display_df["quantum_risk"].fillna("Unknown").astype(str).unique())
    languages = sorted(display_df["language"].fillna("Unknown").astype(str).unique())

    with a:
        selected_algorithms = st.multiselect(
            "Algorithm",
            algorithms,
            default=algorithms,
            key=f"{key_prefix}_algorithms",
        )
    with b:
        selected_risks = st.multiselect(
            "Quantum risk",
            risks,
            default=risks,
            key=f"{key_prefix}_risks",
        )
    with c:
        selected_languages = st.multiselect(
            "Language",
            languages,
            default=languages,
            key=f"{key_prefix}_languages",
        )

    visible = display_df[
        display_df["algorithm"].fillna("Unknown").astype(str).isin(selected_algorithms)
        & display_df["quantum_risk"].fillna("Unknown").astype(str).isin(selected_risks)
        & display_df["language"].fillna("Unknown").astype(str).isin(selected_languages)
    ].copy()

    columns = ["file", "line", "language", "algorithm", "quantum_risk", "confidence"]
    show_readable_dataframe(visible[columns], use_container_width=True, hide_index=True)

    if not visible.empty:
        st.markdown("#### Finding details")
        reset = visible.reset_index(drop=True)
        options = [
            f'{i + 1}. {row.get("algorithm", "Unknown")} — '
            f'{Path(str(row.get("file", "unknown"))).name}:{row.get("line", "?")}'
            for i, row in reset.iterrows()
        ]
        selected = st.selectbox(
            "Select a finding to inspect",
            options,
            key=f"{key_prefix}_selected_finding",
        )
        selected_index = options.index(selected)
        item = reset.iloc[selected_index].to_dict()

        detail_left, detail_right = st.columns(2)
        with detail_left:
            st.markdown("**Location**")
            st.code(f'{item.get("file", "Unknown")} : line {item.get("line", "?")}')
            st.markdown("**Evidence**")
            st.code(str(item.get("evidence", "No evidence field provided.")))
            st.markdown("**Purpose**")
            st.write(item.get("purpose", "No purpose description provided."))
        with detail_right:
            st.markdown("**Quantum risk**")
            st.write(item.get("quantum_risk", "Unknown"))
            st.markdown("**Confidence**")
            st.write(item.get("confidence", "Unknown"))
            st.markdown("**Recommendation**")
            st.write(item.get("recommendation", "No recommendation provided."))

    csv_data = visible.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered findings (CSV)",
        data=csv_data,
        file_name="q_guard_findings.csv",
        mime="text/csv",
        key=f"{key_prefix}_download",
    )
    return visible


# ---------------------------------------------------------
# MIGRATION ROADMAP HELPERS
# ---------------------------------------------------------
def _finding_text(item):
    """Combine common finding fields for conservative, explainable matching."""
    fields = [
        item.get("algorithm", ""), item.get("evidence", ""),
        item.get("purpose", ""), item.get("recommendation", ""),
        item.get("quantum_risk", ""),
    ]
    return " ".join(str(value) for value in fields if value is not None).lower()


def migration_advice(item):
    """Return advisory next steps based on the algorithm/pattern named by a finding."""
    text = _finding_text(item)
    algorithm = str(item.get("algorithm", "Unknown"))
    risk = str(item.get("quantum_risk", "Unknown"))

    # Prioritise asymmetric algorithms affected by Shor's algorithm.
    if any(token in text for token in ("rsa", "ecdsa", "ecdh", "elliptic curve", "diffie-hellman", "diffie hellman", "dh_key")):
        priority = "High"
        why = ("This match appears related to public-key cryptography that may be vulnerable "
               "to a sufficiently capable fault-tolerant quantum computer. A match alone "
               "does not prove the code is active or exposed.")
        steps = [
            "Confirm whether the matched code is active and used in a security-sensitive path.",
            "Trace where it is used: key exchange, certificates, signatures, stored keys, or a dependency.",
            "Inventory affected protocols, certificates, libraries, and external integrations.",
            "Design a standards-aligned migration plan; evaluate ML-KEM for key establishment and ML-DSA or SLH-DSA for signatures where appropriate.",
            "Test interoperability, performance, key/certificate lifecycle, and rollback before production rollout.",
        ]
    elif any(token in text for token in ("ml-kem", "kyber")):
        priority = "Review"
        why = "The match appears to reference a post-quantum key-encapsulation mechanism; verify correct implementation and actual use rather than treating the name alone as proof of readiness."
        steps = [
            "Confirm the implementation and standardized algorithm version used by the project.",
            "Check library provenance, configuration, and whether the algorithm is actually used for key establishment.",
            "Review protocol integration, interoperability, error handling, and key lifecycle.",
            "Record the evidence and have the implementation reviewed against current standards and vendor guidance.",
        ]
    elif any(token in text for token in ("ml-dsa", "dilithium", "slh-dsa", "sphincs")):
        priority = "Review"
        why = "The match appears to reference a post-quantum signature algorithm; verify that it is implemented and used correctly in the intended signing/verification path."
        steps = [
            "Confirm the standardized algorithm and implementation version.",
            "Trace signing and verification paths, including certificates and protocol support.",
            "Check signature/key sizes, performance, interoperability, and key management.",
            "Document the evidence and validate the design against current standards and vendor guidance.",
        ]
    elif any(token in text for token in ("aes", "sha", "hash", "symmetric", "hmac")):
        priority = "Context review"
        why = "Symmetric cryptography and hashes should not automatically be treated like RSA/ECC. Risk depends on the primitive, key/digest size, purpose, and threat model."
        steps = [
            "Confirm the exact primitive, key size or digest size, and security purpose.",
            "Check whether the code protects long-lived confidential data or derives/validates keys.",
            "Review current organizational cryptographic policy and applicable standards before changing parameters.",
            "Avoid replacing algorithms solely because a static match was detected; document the reasoning.",
        ]
    else:
        priority = "Manual review"
        why = "The scanner returned a match, but the available fields do not identify a sufficiently specific algorithm or use case to prescribe a safe migration."
        steps = [
            "Inspect the source line and surrounding code to identify the actual cryptographic operation.",
            "Determine whether the match is active code, a comment, a test, or an unused import.",
            "Trace dependencies and the protocol or data protected by the operation.",
            "Ask a security reviewer to assign a risk level and select a standards-aligned replacement if needed.",
        ]

    return {"priority": priority, "why": why, "steps": steps, "algorithm": algorithm, "risk": risk}


def build_migration_plan(dataframe):
    """Create a roadmap table from findings without modifying source code."""
    if dataframe.empty:
        return pd.DataFrame()
    rows = []
    for _, series in dataframe.iterrows():
        item = series.to_dict()
        advice = migration_advice(item)
        rows.append({
            "Priority": advice["priority"],
            "File": str(item.get("file", "Unknown")),
            "Line": item.get("line", "?"),
            "Algorithm / match": advice["algorithm"],
            "Scanner risk label": advice["risk"],
            "First action": advice["steps"][0],
        })
    priority_order = {"High": 0, "Review": 1, "Context review": 2, "Manual review": 3}
    result = pd.DataFrame(rows)
    result["_order"] = result["Priority"].map(priority_order).fillna(4)
    return result.sort_values(["_order", "File", "Line"]).drop(columns="_order").reset_index(drop=True)


# ---------------------------------------------------------
# PAGE: DASHBOARD
# ---------------------------------------------------------
if page == "Dashboard":
    st.markdown(
        """
        <div class="qg-hero">
            <div class="qg-eyebrow">Security overview</div>
            <div class="qg-title">🛡️ Q-Guard Dashboard</div>
            <div class="qg-subtitle">
                Scan source code, inspect cryptographic patterns, and review potential
                post-quantum migration risks in one place.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    show_metrics()

    st.write("")
    left, right = st.columns([1.05, 1.45], gap="large")

    with left:
        st.markdown('<div class="qg-section">📡 Scan status</div>', unsafe_allow_html=True)
        if st.session_state.has_scanned and not st.session_state.scan_error:
            status_title = "A scan has completed."
            status_note = "The scan finished; review matches before treating them as risks."
            status_color = "#14532d"
        else:
            status_title = "No completed scan yet."
            status_note = "Choose a source in the sidebar and select Scan now."
            status_color = "#17243a"
        # One self-contained HTML card: Streamlit widgets cannot be wrapped by
        # opening and closing HTML divs across separate st.* calls.
        st.markdown(
            f'''<div class="qg-panel qg-status-card">
                <div class="qg-status-banner" style="background:{status_color};">{status_title}</div>
                <div class="qg-status-row"><span>Input source</span><strong>{st.session_state.last_scan_source if st.session_state.has_scanned else 'Not scanned yet'}</strong></div>
                <div class="qg-status-row"><span>Files processed</span><strong>{summary['files_scanned']}</strong></div>
                <div class="qg-status-row"><span>Findings returned</span><strong>{summary['findings']}</strong></div>
                <div class="qg-status-note">{status_note}</div>
            </div>''',
            unsafe_allow_html=True,
        )

        st.write("")
        st.markdown('<div class="qg-section">🔐 Algorithms detected</div>', unsafe_allow_html=True)
        algorithms = summary.get("algorithms_detected", [])
        algorithm_text = ", ".join(str(a) for a in algorithms) if algorithms else "Algorithm labels will appear here after a scan returns findings."
        st.markdown(
            f'<div class="qg-panel qg-algorithms-card">{algorithm_text}</div>',
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="qg-section">📊 Findings overview</div>', unsafe_allow_html=True)
        if not df.empty and "quantum_risk" in df.columns:
            risk_counts = (
                df["quantum_risk"]
                .fillna("Unknown")
                .astype(str)
                .value_counts()
                .rename_axis("Quantum risk")
                .reset_index(name="Findings")
            )
            st.bar_chart(risk_counts.set_index("Quantum risk"), use_container_width=True)

            if "algorithm" in df.columns:
                alg_counts = (
                    df["algorithm"]
                    .fillna("Unknown")
                    .astype(str)
                    .value_counts()
                    .rename_axis("Algorithm")
                    .reset_index(name="Findings")
                )
                st.markdown("**Findings by algorithm**")
                st.bar_chart(alg_counts.set_index("Algorithm"), use_container_width=True)
        else:
            st.info("Charts will populate from real scan findings after your first scan.")

    st.divider()
    st.markdown('<div class="qg-section">🚩 Latest findings</div>', unsafe_allow_html=True)
    if df.empty:
        st.caption("No findings to preview. Run a scan to see results here.")
    else:
        preview_columns = [
            c for c in ["file", "line", "language", "algorithm", "quantum_risk", "confidence"]
            if c in df.columns
        ]
        show_readable_dataframe(df[preview_columns].head(8), use_container_width=True, hide_index=True)
        st.caption("For full filtering, evidence, and recommendations, open Findings & Reports.")

    with st.expander("What this prototype can and cannot tell you"):
        st.markdown(
            """
            - It matches curated API names and patterns in source-code lines.
            - A match can be a comment, unused import, test fixture, or unrelated identifier.
            - It can miss aliased APIs, wrappers, dynamically constructed calls, dependencies,
              and code in unsupported languages.
            - RSA, finite-field DH, ECDH and ECDSA are vulnerable to a sufficiently capable
              fault-tolerant quantum computer running Shor's algorithm.
            - ML-KEM is for key establishment; ML-DSA and SLH-DSA are for signatures.
              Migration depends on actual usage and protocol design.
            - AES and hash findings need contextual assessment; they should not automatically
              be classified like RSA/ECC.
            - This tool does not automatically modify code and is not a substitute for a
              security audit.
            """
        )


# ---------------------------------------------------------
# PAGE: SCAN FILES
# ---------------------------------------------------------
elif page == "Scan Files":
    st.markdown('<div class="qg-section">🔍 Scan source files</div>', unsafe_allow_html=True)
    st.write(
        "Choose the scan source from the sidebar, then click **Scan now**. "
        "Supported source extensions are Python, Java, C, and header files."
    )
    show_metrics()

    if st.session_state.has_scanned and not st.session_state.scan_error:
        st.success(f"Last completed scan source: {st.session_state.last_scan_source}")
        if not df.empty:
            st.markdown("#### Quick results")
            cols = [c for c in ["file", "line", "algorithm", "quantum_risk"] if c in df.columns]
            show_readable_dataframe(df[cols], use_container_width=True, hide_index=True)
        else:
            st.info("The last scan returned no findings. This does not guarantee the code is secure.")
    else:
        st.info("No scan completed yet. Use the source controls in the sidebar.")


# ---------------------------------------------------------
# PAGE: FINDINGS & REPORTS
# ---------------------------------------------------------
elif page == "Findings & Reports":
    st.markdown('<div class="qg-section">🧾 Findings & reports</div>', unsafe_allow_html=True)
    st.write("Filter the scanner output, inspect evidence, and export the visible findings.")
    show_finding_filters(df, key_prefix="report")


# ---------------------------------------------------------
# PAGE: QUANTUM RISK GUIDE
# ---------------------------------------------------------
elif page == "Quantum Risk Guide":
    st.markdown('<div class="qg-section">⚛️ Quantum risk guide</div>', unsafe_allow_html=True)
    st.write(
        "This guide provides general context for interpreting scanner matches. "
        "A source-code match alone does not prove that an algorithm is used in production."
    )

    with st.expander("Public-key cryptography: RSA, DH, ECDH and ECDSA", expanded=True):
        st.write(
            "A sufficiently capable fault-tolerant quantum computer running Shor's algorithm "
            "could break widely used RSA and elliptic-curve or finite-field discrete-log "
            "cryptography. Review how each match is used, the protocol involved, and the "
            "migration requirements before assigning operational severity."
        )

    with st.expander("Post-quantum algorithms"):
        st.markdown(
            """
            - **ML-KEM:** key establishment (formerly known through the Kyber family).
            - **ML-DSA:** digital signatures (formerly known through the Dilithium family).
            - **SLH-DSA:** stateless hash-based digital signatures.
            """
        )

    with st.expander("Symmetric cryptography and hashes"):
        st.write(
            "AES and hash functions need contextual assessment. Do not automatically treat "
            "their presence as equivalent to an RSA or elliptic-curve vulnerability. "
            "Key sizes, security goals, and actual usage matter."
        )

    with st.expander("How to interpret Q-Guard results"):
        st.markdown(
            """
            1. Review the file, line number, and evidence for each match.
            2. Confirm whether the code is active, reachable, and used in a security-sensitive path.
            3. Check surrounding protocol and configuration context.
            4. Prioritize migration based on exposure, data lifetime, dependencies, and standards.
            5. Validate recommendations with your security team before changing production code.
            """
        )

    st.warning(
        "Q-Guard is a static-analysis prototype. Its heuristic findings are indicators for "
        "review, not proof of runtime use or a complete security audit."
    )


# ---------------------------------------------------------
# PAGE: QUANTUM MIGRATION ROADMAP
# ---------------------------------------------------------
elif page == "Migration Roadmap":
    st.markdown('<div class="qg-section">🧭 Quantum migration roadmap</div>', unsafe_allow_html=True)
    st.write(
        "Turn scan matches into a prioritised review plan. This page gives advisory next steps; "
        "it does not automatically edit code or certify that a system is quantum-safe."
    )

    if not st.session_state.has_scanned:
        st.info("Run a scan first from the sidebar. The roadmap will use that scan's findings.")
    elif df.empty:
        st.success("The last scan returned no findings, so there are no match-specific migration actions to list.")
        st.warning("No findings does not prove that the project is quantum-safe; static analysis can miss cryptographic usage.")
    else:
        plan = build_migration_plan(df)
        high_count = int((plan["Priority"] == "High").sum())
        review_count = int(plan["Priority"].isin(["Review", "Context review", "Manual review"]).sum())
        c1, c2, c3 = st.columns(3)
        c1.metric("Findings to review", len(plan))
        c2.metric("High-priority candidates", high_count)
        c3.metric("Context/manual reviews", review_count)

        st.markdown("#### Recommended order of work")
        st.markdown(
            "1. **Validate findings** — inspect the file, line, evidence, and surrounding code.\n"
            "2. **Map real usage** — identify active paths, protocols, dependencies, and data lifetime.\n"
            "3. **Prioritise exposure** — focus on vulnerable public-key cryptography protecting long-lived or sensitive assets.\n"
            "4. **Plan migration** — evaluate standards-aligned post-quantum options and interoperability.\n"
            "5. **Test and document** — test performance, compatibility, key management, and rollout/rollback before deployment."
        )
        st.caption("The priority is a triage suggestion based on text matches, not a formal risk rating.")

        st.markdown("#### Prioritised roadmap")
        show_readable_dataframe(plan, use_container_width=True, hide_index=True)

        priority_choices = list(plan["Priority"].dropna().astype(str).unique())
        selected_priority = st.selectbox(
            "Inspect findings by priority",
            ["All priorities"] + priority_choices,
            key="roadmap_priority_filter",
        )
        detail_plan = plan if selected_priority == "All priorities" else plan[plan["Priority"] == selected_priority]

        for row_number, row in detail_plan.iterrows():
            match = df[
                (df.get("file", pd.Series(index=df.index, dtype=str)).astype(str) == str(row["File"]))
                & (df.get("line", pd.Series(index=df.index, dtype=str)).astype(str) == str(row["Line"]))
                & (df.get("algorithm", pd.Series(index=df.index, dtype=str)).astype(str) == str(row["Algorithm / match"]))
            ]
            item = match.iloc[0].to_dict() if not match.empty else {"file": row["File"], "line": row["Line"], "algorithm": row["Algorithm / match"], "quantum_risk": row["Scanner risk label"]}
            advice = migration_advice(item)
            label = f'{row["Priority"]} — {Path(str(row["File"])).name}:{row["Line"]} — {row["Algorithm / match"]}'
            with st.expander(label):
                left, right = st.columns(2)
                with left:
                    st.markdown("**Why this was flagged**")
                    st.write(advice["why"])
                    st.markdown("**Evidence from the scan**")
                    st.code(str(item.get("evidence", "No evidence field was returned by the scanner.")))
                    st.markdown("**Purpose reported by scanner**")
                    st.write(item.get("purpose", "Not provided by the scanner."))
                with right:
                    st.markdown("**Suggested next steps**")
                    for step in advice["steps"]:
                        st.markdown(f"- {step}")
                    st.markdown("**Existing scanner recommendation**")
                    st.write(item.get("recommendation", "No recommendation field was returned by the scanner."))

        st.download_button(
            "⬇️ Download migration roadmap (CSV)",
            data=plan.to_csv(index=False).encode("utf-8"),
            file_name="q_guard_migration_roadmap.csv",
            mime="text/csv",
            key="roadmap_download",
        )

    st.warning(
        "Static-analysis matches are heuristic indicators, not proof of runtime use or a complete security audit. "
        "Validate every finding with the surrounding code and your security requirements before making changes."
    )
