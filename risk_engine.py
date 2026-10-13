"""Small policy layer; rules are intentionally transparent and reviewable."""

def summarize(findings):
    counts = {}
    for finding in findings:
        key = finding["quantum_risk"]
        counts[key] = counts.get(key, 0) + 1
    return counts

def prioritize(findings):
    """Sort public-key quantum-vulnerable findings before context-dependent ones."""
    priority = {
        "High": 0,
        "Legacy / context-dependent": 1,
        "Context-dependent": 2,
        "Generally retain; context-dependent": 3,
    }
    return sorted(
        findings,
        key=lambda f: (priority.get(f["quantum_risk"], 4), f["file"], f["line"])
    )

def report_summary(scanned_files, findings):
    algorithms = sorted({f["algorithm"] for f in findings})
    high = sum(f["quantum_risk"] == "High" for f in findings)
    return {
        "files_scanned": scanned_files,
        "findings": len(findings),
        "high_quantum_risk_findings": high,
        "algorithms_detected": algorithms,
    }