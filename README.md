# MetrIQ 🇮🇳 — SIH 26034 Demo

AI-assisted inspection prototype for **SIH Problem Statement 26034**: checking compliance of packaged commodities under the Legal Metrology (Packaged Commodities) Rules, 2011.

> **Handoff-safe project contract:** This README is the source of truth for the current architecture, run commands, boundaries, and next steps. Any AI coding agent (Antigravity, Codex, Cursor, Claude Code, etc.) should read this file before changing the project.

## Current status

The `sih26034-demo` branch contains a Python-first Streamlit proof of concept with:

- 🇮🇳 India / government-style inspection UI
- Product/label image upload
- Built-in synthetic demo label for deterministic demos without API keys
- Best-effort Tesseract OCR with graceful fallback
- Editable extracted text for human verification
- Deterministic compliance rules engine
- Declaration matrix with PASS / FAIL / REVIEW states
- Evidence-backed violation explanations
- Compliance score
- Browser-session inspection history
- JSON inspection report export
- Rules & Method page with explicit prototype limitations

## Architecture

```text
Image / Label
     ↓
OCR / Extraction
     ↓
Structured facts
     ↓
Deterministic Rules Engine  ← versioned legal knowledge base
     ↓
Compliance Decision
     ↓
Evidence + Findings + Score
     ↓
Inspector Report / History
```

### Important design rule

**Do not make an LLM the legal authority.** AI should extract/normalize evidence. The compliance result should be produced by deterministic, versioned rules that can be audited and mapped to official legal sources.

## Files

```text
app.py          Streamlit UI + inspection workflow
rules.py        Auditable demo rules + extraction checks
requirements.txt
.gitignore
README.md       This handoff / project contract
```

## Run locally

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

### OCR note

`pytesseract` is included as an optional OCR bridge. On Windows, the **Tesseract executable itself** may need to be installed separately and placed on PATH. The built-in **Run Demo Scan** works without Tesseract because it uses a synthetic label and deterministic demo extraction fallback.

## Demo flow

1. Open **Inspection Desk**.
2. Enter inspector/location/product ID if desired.
3. Click **🇮🇳 Run Demo Scan**.
4. Click **Analyze compliance →**.
5. Review declaration matrix and evidence-backed findings.
6. Open **Inspection History** to see the record.
7. Download the JSON inspection report.

For an uploaded image, the extracted OCR text is intentionally editable. This is a human-in-the-loop safety feature, not a shortcut around validation.

## Legal / accuracy boundary

The current rules engine is a **focused demonstration subset**, not a complete legal implementation. It must not be presented as an authoritative statutory compliance decision.

Before production use:

- Synchronize the rules corpus with the current official Legal Metrology Act/Rules, amendments, exemptions and notifications.
- Add effective dates and rule versions.
- Store the official source reference for every validation rule.
- Add product-category applicability and exceptions.
- Distinguish automated evidence extraction from legal determination.
- Require physical verification for measurements that cannot be reliably inferred from a photograph.
- Maintain an audit trail for rule changes and inspector overrides.

Official source starting point: https://consumeraffairs.gov.in/pages/legal-metrology-act

## Next high-value build steps

### Phase 1 — stronger computer vision

- OCR bounding boxes
- document/label layout detection
- declaration-region highlighting
- perspective correction
- confidence scoring per extracted field

### Phase 2 — physical measurement assistance

Use a calibrated reference or known package dimension to estimate character height and declaration placement. Never claim millimetre-level accuracy from an arbitrary photograph without calibration.

### Phase 3 — e-commerce inspection

Accept a product listing, extract listing text/images, and compare listing declarations against package evidence. Flag mismatches such as MRP/quantity discrepancies.

### Phase 4 — production backend

```text
React / mobile client
        ↓
FastAPI
        ↓
CV + OCR workers
        ↓
Rules service
        ↓
PostgreSQL + object storage
        ↓
Audit / reporting layer
```

Add RBAC, immutable inspection IDs, evidence storage, audit logs and report signing only after the core inspection engine is stable.

## AI-agent handoff rules

When another AI agent joins this repository:

1. Read this README first.
2. Inspect the existing files before replacing architecture.
3. Preserve the separation between **extraction** and **legal rules**.
4. Do not silently remove the demo fallback.
5. Do not add secret/API keys to source control.
6. Do not claim legal certainty from OCR alone.
7. Prefer small, testable modules over a single giant file as the project grows.
8. Update this README when architecture, commands, dependencies, or major features change.
9. Keep commits focused and descriptive.
10. Before changing legal rules, verify them against the current official source.

## Branching recommendation

Use `main` for stable work and feature branches such as:

```text
feature/ocr-layout
feature/rules-engine
feature/ecommerce-scan
feature/reporting
feature/backend
```

Merge only after the demo still runs locally.

## Problem statement

**SIH 26034 — Software System to check compliance of Packaged Commodities under Legal Metrology (Packaged Commodities) Rules, 2011 by scanning products, images and labels.**

Organization: Department of Consumer Affairs, Ministry of Consumer Affairs, Food & Public Distribution.
