from __future__ import annotations

import re

RULES_VERSION = "Demo KB v0.1 • focused screening subset"

# IMPORTANT: This is intentionally a small, auditable demonstration subset.
# Legal requirements must be synchronized with the current official Rules,
# amendments, exemptions and notifications before production enforcement use.
RULES = [
    {
        "id": "PC-DECL-01",
        "name": "Manufacturer / packer / importer identity",
        "description": "Check for a recognizable manufacturer, packer or importer declaration and an associated address.",
        "validation": "Text-pattern presence + address heuristic",
    },
    {
        "id": "PC-DECL-02",
        "name": "Net quantity",
        "description": "Check for a net quantity declaration with a numeric value and common unit.",
        "validation": "Quantity regex",
    },
    {
        "id": "PC-DECL-03",
        "name": "MRP declaration",
        "description": "Check for a recognizable MRP / maximum retail price declaration.",
        "validation": "MRP / ₹ / Rs regex",
    },
    {
        "id": "PC-DECL-04",
        "name": "Consumer care details",
        "description": "Check for consumer-care contact information such as a phone number or email.",
        "validation": "Phone/email heuristic",
    },
    {
        "id": "PC-DECL-05",
        "name": "Date / packing information",
        "description": "Check for a recognizable packed/manufactured date declaration.",
        "validation": "Date keyword + month/year or numeric date heuristic",
    },
    {
        "id": "PC-DECL-06",
        "name": "Country of origin",
        "description": "Screen for country-of-origin text when applicable to the product scenario.",
        "validation": "Origin keyword heuristic; applicability requires product context",
    },
]

SAMPLE_PRODUCT_TEXT = """BHARAT NATURAL FOODS
Premium Whole Wheat Biscuits
NET QUANTITY: 100 g
MRP ₹50.00 (INCLUSIVE OF ALL TAXES)
Manufactured & Packed by: Bharat Foods Pvt. Ltd.
Plot 18, Industrial Area, New Delhi - 110020
Consumer Care: 1800-123-4567 | care@bharatfoods.in
Packed: 06/2026   Best Before: 06/2027
Country of Origin: India"""


def _has(pattern: str, text: str) -> bool:
    return bool(re.search(pattern, text, flags=re.I | re.M))


def _check(name: str, rule: str, ok: bool, detail: str, review: bool = False) -> dict:
    status = "REVIEW" if review else "PASS" if ok else "FAIL"
    return {"name": name, "rule": rule, "status": status, "detail": detail}


def analyze_product(text: str) -> dict:
    text = (text or "").strip()
    if not text:
        return {
            "status": "REVIEW", "score": 0, "checked": len(RULES),
            "checks": [], "violations": [{"title": "No usable label text", "finding": "OCR/extracted text is empty.", "rule": "INPUT", "evidence": "No text evidence available.", "confidence": "High", "action": "Capture a sharper label image or enter text for verification."}],
        }

    checks = []
    violations = []

    identity = _has(r"(?:manufactur(?:ed|er)|packed\s+by|importer)", text)
    address = _has(r"(?:address|road|rd\.?|area|industrial|delhi|mumbai|lucknow|bengaluru|kolkata|pune|noida|\b\d{6}\b)", text)
    checks.append(_check("Manufacturer / packer / importer", "PC-DECL-01", identity and address, "Identity and address pattern detected." if identity and address else "Identity/address evidence is incomplete."))
    if not identity or not address:
        violations.append({"title":"Identity / address declaration", "finding":"A recognizable manufacturer/packer/importer declaration or associated address could not be fully established from the supplied text.", "rule":"PC-DECL-01", "evidence":"Missing keyword/address pattern in extracted text.", "confidence":"Medium", "action":"Inspect the package panel and verify against the current applicable requirement."})

    qty = _has(r"(?:net\s*quantity|net\s*wt|net\s*weight)\s*[:\-]?\s*\d+(?:\.\d+)?\s*(?:kg|g|mg|l|ml|mL|L|cm|mm|pcs?|pieces?)\b", text)
    checks.append(_check("Net quantity", "PC-DECL-02", qty, "Numeric quantity + unit detected." if qty else "No clear net-quantity pattern detected."))
    if not qty:
        violations.append({"title":"Net quantity", "finding":"No clear numeric net-quantity declaration was extracted.", "rule":"PC-DECL-02", "evidence":"Quantity regex did not match.", "confidence":"Medium", "action":"Verify the principal display panel."})

    mrp = _has(r"(?:m\.?r\.?p\.?|maximum\s+retail\s+price|₹|rs\.?\s*)\s*[:\-]?\s*(?:₹|rs\.?\s*)?\d+(?:\.\d{1,2})?", text)
    checks.append(_check("MRP", "PC-DECL-03", mrp, "MRP / rupee-price pattern detected." if mrp else "No clear MRP pattern detected."))
    if not mrp:
        violations.append({"title":"MRP declaration", "finding":"No clear MRP / price declaration was extracted.", "rule":"PC-DECL-03", "evidence":"MRP/price regex did not match.", "confidence":"Medium", "action":"Verify the package label and applicable declaration format."})

    contact = _has(r"(?:consumer\s*care|customer\s*care|helpline|toll\s*free)", text) and (_has(r"\b\d{7,12}\b", text) or _has(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text))
    checks.append(_check("Consumer care details", "PC-DECL-04", contact, "Consumer-care label plus phone/email detected." if contact else "No complete consumer-care contact pattern detected."))
    if not contact:
        violations.append({"title":"Consumer care details", "finding":"A consumer-care label with a recognizable contact detail was not established.", "rule":"PC-DECL-04", "evidence":"Consumer-care + phone/email heuristic did not match.", "confidence":"Medium", "action":"Verify contact details on the package."})

    date = _has(r"(?:packed|packing|manufactured|mfg|mfd)\s*[:\-]?\s*(?:\d{1,2}[/-])?(?:0?[1-9]|1[0-2])[/-]\d{2,4}", text) or _has(r"(?:packed|packing|manufactured|mfg|mfd)\s*[:\-]?\s*\d{1,2}[/-]\d{4}", text)
    checks.append(_check("Date / packing information", "PC-DECL-05", date, "Packing/manufacturing date pattern detected." if date else "Date declaration is unclear from extracted text."))
    if not date:
        violations.append({"title":"Packing / manufacturing date", "finding":"No clear packing/manufacturing date pattern was extracted.", "rule":"PC-DECL-05", "evidence":"Date keyword + date pattern did not match.", "confidence":"Medium", "action":"Zoom into the date/batch panel and physically verify."})

    origin = _has(r"(?:country\s+of\s+origin|made\s+in|product\s+of)\s*[:\-]?\s*[A-Za-z ]+", text)
    checks.append(_check("Country of origin", "PC-DECL-06", origin, "Origin statement detected; applicability depends on product context." if origin else "Origin statement not detected; applicability needs review." , review=not origin))

    passed = sum(1 for c in checks if c["status"] == "PASS")
    review_count = sum(1 for c in checks if c["status"] == "REVIEW")
    score = round((passed / len(checks)) * 100)
    if violations:
        status = "NON-COMPLIANT"
    elif review_count:
        status = "REVIEW"
    else:
        status = "COMPLIANT"

    return {"status": status, "score": score, "checked": len(checks), "checks": checks, "violations": violations}
