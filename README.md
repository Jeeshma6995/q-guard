Q-Guard – Post-Quantum Cryptography Readiness Scanner

About the Project:

Q-Guard is a Python-based static analysis tool designed to identify potential cryptographic risks in source code related to the development of quantum computing.

As quantum computers advance, traditional cryptographic algorithms such as RSA, ECDH, and ECDSA may become vulnerable to quantum attacks. Q-Guard helps developers identify potentially affected cryptographic patterns and understand the steps needed to prepare for Post-Quantum Cryptography (PQC).

The application provides an interactive dashboard to scan source files, review findings, understand quantum risks, and explore a recommended migration roadmap.

Objectives:

- Identify potential cryptographic patterns in source code.
- Highlight algorithms that may be vulnerable to future quantum attacks.
- Classify and prioritize potential findings for review.
- Provide recommendations for post-quantum migration.
- Help developers understand cryptographic risks through a simple dashboard.

Features:

- **Interactive Dashboard:** Displays scan statistics, findings, and detected algorithm labels.
- **Source Code Scanner:** Scans built-in sample files or uploaded source files.
- **Multiple Language Support:** Supports Python, Java, C, and C header files.
- **Risk Analysis:** Prioritizes potential findings using the project's risk engine.
- **Findings & Reports:** Filter findings and inspect evidence, file locations, confidence, and recommendations.
- **Quantum Risk Guide:** Explains common cryptographic risks and post-quantum algorithms.
- **Migration Roadmap:** Provides suggested review steps based on detected patterns.
- **CSV Export:** Download filtered findings and migration roadmap reports.
- **Dark UI:** Provides a clean, interactive interface using Streamlit.

Technologies Used :

- Python
- Streamlit
- Pandas
- Static Analysis
- Rule-Based Pattern Detection
- HTML and CSS for dashboard styling

Project Structure :

```text
q-guard/
│
├── report/
│   └── Final_report.docx
│
├── samples/
│   ├── sample.c
│   ├── sample.java
│   └── sample.py
│
├── app.py
├── scanner.py
├── risk_engine.py
├── rules.py
├── requirements.txt
├── README.md
└── .gitignore
