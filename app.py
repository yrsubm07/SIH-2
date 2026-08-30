from __future__ import annotations

import io
import json
import re
from datetime import datetime
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

from rules import analyze_product, SAMPLE_PRODUCT_TEXT, RULES_VERSION

st.set_page_config(
    page_title="MetrIQ — Legal Metrology Inspector",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Theme ----------
st.markdown(
    """
    <style>
    :root { --navy:#0b1f3a; --saffron:#f59e0b; --green:#138a4b; --ink:#172033; --muted:#667085; --paper:#f6f8fb; }
    .stApp { background: #f6f8fb; color: var(--ink); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg,#0b1f3a 0%,#102d50 55%,#0b1f3a 100%); }
    [data-testid="stSidebar"] * { color: #fff !important; }
    .hero { background: linear-gradient(135deg,#0b1f3a 0%,#123e69 65%,#138a4b 100%); padding: 28px 32px; border-radius: 18px; color:#fff; margin-bottom: 18px; box-shadow: 0 10px 35px rgba(11,31,58,.16); }
    .hero h1 { margin:0; font-size: 34px; letter-spacing:-.7px; }
    .hero p { margin:.45rem 0 0; color:#d9e7f6; font-size:15px; }
    .flag { display:inline-flex; gap:7px; align-items:center; font-weight:700; font-size:12px; letter-spacing:.4px; text-transform:uppercase; }
    .card { background:#fff; border:1px solid #e5eaf0; border-radius:14px; padding:18px; box-shadow:0 3px 15px rgba(16,24,40,.05); }
    .metric { background:#fff; border:1px solid #e5eaf0; border-radius:14px; padding:16px; }
    .metric .k { color:#667085; font-size:12px; text-transform:uppercase; letter-spacing:.5px; }
    .metric .v { font-size:27px; font-weight:800; margin-top:4px; }
    .ok { color:#087443; } .bad { color:#b42318; } .warn { color:#b54708; }
    .section-title { font-size:20px; font-weight:800; margin:22px 0 10px; }
    .small { color:#667085; font-size:12px; }
    .pill { display:inline-block; padding:5px 10px; border-radius:999px; font-size:12px; font-weight:700; background:#eef4fb; color:#174a7c; }
    .evidence { background:#fff8e8; border-left:4px solid #f59e0b; padding:12px 14px; border-radius:8px; }
    .footer { margin-top:30px; padding-top:15px; border-top:1px solid #e5eaf0; color:#667085; font-size:12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Helpers ----------
def make_demo_label() -> Image.Image:
    img = Image.new("RGB", (1200, 780), "white")
    d = ImageDraw.Draw(img)
    try:
        bold = ImageFont.truetype("DejaVuSans-Bold.ttf", 48)
        h1 = ImageFont.truetype("DejaVuSans-Bold.ttf", 30)
        body = ImageFont.truetype("DejaVuSans.ttf", 25)
        tiny = ImageFont.truetype("DejaVuSans.ttf", 19)
    except Exception:
        bold = h1 = body = tiny = None
    # India-inspired tricolour header.
    d.rectangle((0,0,1200,18), fill="#ff9933")
    d.rectangle((0,18,1200,36), fill="#ffffff")
    d.rectangle((0,36,1200,54), fill="#138a4b")
    d.text((55,85), "BHARAT NATURAL FOODS", fill="#0b1f3a", font=bold)
    d.text((58,155), "Premium Whole Wheat Biscuits", fill="#333333", font=h1)
    d.text((58,220), "NET QUANTITY: 100 g", fill="#111111", font=body)
    d.text((58,275), "MRP ₹50.00 (INCLUSIVE OF ALL TAXES)", fill="#111111", font=body)
    d.text((58,335), "Manufactured & Packed by: Bharat Foods Pvt. Ltd.", fill="#111111", font=body)
    d.text((58,375), "Plot 18, Industrial Area, New Delhi - 110020", fill="#111111", font=tiny)
    d.text((58,425), "Consumer Care: 1800-123-4567 | care@bharatfoods.in", fill="#111111", font=tiny)
    d.text((58,470), "Packed: 06/2026   Best Before: 06/2027", fill="#111111", font=tiny)
    d.text((58,515), "Country of Origin: India", fill="#111111", font=tiny)
    d.text((820,200), "₹50", fill="#b42318", font=bold)
    d.rectangle((790,185,1100,285), outline="#b42318", width=5)
    d.text((790,620), "DEMO LABEL — synthetic training image", fill="#667085", font=tiny)
    return img


def image_bytes(img: Image.Image) -> bytes:
    b = io.BytesIO(); img.save(b, format="PNG"); return b.getvalue()


def run_ocr(img: Image.Image) -> tuple[str, str]:
    """Best-effort OCR. The app remains usable when Tesseract is unavailable."""
    try:
        import pytesseract
        text = pytesseract.image_to_string(img)
        if text.strip():
            return text, "Tesseract OCR"
    except Exception:
        pass
    return "", "OCR unavailable — use extracted text/manual verification"


def result_label(result):
    return "COMPLIANT" if result["status"] == "COMPLIANT" else ("REVIEW REQUIRED" if result["status"] == "REVIEW" else "NON-COMPLIANT")

# ---------- State ----------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------- Sidebar ----------
st.sidebar.markdown("### 🇮🇳 MetrIQ")
st.sidebar.caption("Legal Metrology Inspection Intelligence")
page = st.sidebar.radio("Navigate", ["Inspection Desk", "Inspection History", "Rules & Method", "About"])
st.sidebar.divider()
st.sidebar.markdown("**PS:** SIH 26034")
st.sidebar.markdown(f"**Rules KB:** {RULES_VERSION}")
st.sidebar.caption("AI assists inspection; it does not replace statutory or physical verification.")

# ---------- Hero ----------
st.markdown(
    '<div class="hero"><div class="flag">🇮🇳 Government of India • Consumer Protection</div><h1>MetrIQ</h1><p>AI-assisted packaged commodity compliance inspection for Legal Metrology (Packaged Commodities) Rules, 2011.</p></div>',
    unsafe_allow_html=True,
)

if page == "Inspection Desk":
    st.markdown("### 🔍 New Inspection")
    c1, c2, c3 = st.columns(3)
    with c1:
        inspector = st.text_input("Inspector name", "Demo Inspector")
    with c2:
        location = st.text_input("Inspection location", "New Delhi")
    with c3:
        product_id = st.text_input("Product / SKU ID", "DEMO-BF-100G")

    uploaded = st.file_uploader("Upload product / label image", type=["png", "jpg", "jpeg", "webp"])
    use_demo = st.button("🇮🇳 Run Demo Scan", type="primary", use_container_width=True)

    image = None
    source = ""
    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        source = uploaded.name
    elif use_demo:
        image = make_demo_label()
        source = "synthetic_demo_label.png"

    if image:
        left, right = st.columns([1.05, 1])
        with left:
            st.image(image, caption=source, use_container_width=True)
        with right:
            st.markdown("#### 1. Extract label declarations")
            extracted, engine = run_ocr(image)
            if use_demo and not extracted.strip():
                extracted = SAMPLE_PRODUCT_TEXT
                engine = "Demo extraction pipeline"
            text = st.text_area("OCR / extracted text (editable for verification)", extracted, height=280)
            st.caption(engine)
            run = st.button("Analyze compliance →", type="primary", use_container_width=True)

        if run:
            result = analyze_product(text)
            st.session_state.last_result = result
            st.session_state.last_image = image
            st.session_state.history.insert(0, {
                "inspection_id": f"INSP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "product_id": product_id,
                "location": location,
                "inspector": inspector,
                "status": result["status"],
                "score": result["score"],
                "violations": len(result["violations"]),
            })

    if "last_result" in st.session_state:
        result = st.session_state.last_result
        st.markdown('<div class="section-title">2. Compliance decision</div>', unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="metric"><div class="k">Status</div><div class="v {"ok" if result["status"]=="COMPLIANT" else "bad" if result["status"]=="NON-COMPLIANT" else "warn"}">{result_label(result)}</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric"><div class="k">Compliance score</div><div class="v">{result["score"]}%</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric"><div class="k">Rules checked</div><div class="v">{result["checked"]}</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric"><div class="k">Issues</div><div class="v bad">{len(result["violations"])}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">3. Declaration matrix</div>', unsafe_allow_html=True)
        for item in result["checks"]:
            icon = "✅" if item["status"] == "PASS" else "⚠️" if item["status"] == "REVIEW" else "❌"
            cols = st.columns([0.07, 0.35, 0.35, 0.23])
            cols[0].markdown(f"### {icon}")
            cols[1].markdown(f"**{item['name']}**")
            cols[2].markdown(item["detail"])
            cols[3].markdown(f"`{item['rule']}`")

        st.markdown('<div class="section-title">4. Evidence-backed findings</div>', unsafe_allow_html=True)
        if result["violations"]:
            for i, v in enumerate(result["violations"], 1):
                st.markdown(f"#### {i}. {v['title']}")
                st.markdown(f"**Finding:** {v['finding']}")
                st.markdown(f"**Rule reference:** `{v['rule']}`")
                st.markdown(f"**Evidence:** {v['evidence']}")
                st.markdown(f"**Confidence:** {v['confidence']} • **Action:** {v['action']}")
        else:
            st.success("No rule-triggered issues detected in the supplied text. Physical verification may still be required.")

        st.markdown('<div class="section-title">5. Export inspection record</div>', unsafe_allow_html=True)
        report = {
            "inspection_id": st.session_state.history[0]["inspection_id"] if st.session_state.history else None,
            "problem_statement": "SIH 26034",
            "rules_version": RULES_VERSION,
            "inspector": inspector,
            "location": location,
            "product_id": product_id,
            "result": result,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "disclaimer": "AI-assisted screening. Final statutory determination and physical measurements remain with the authorized enforcement process.",
        }
        st.download_button("Download JSON inspection report", json.dumps(report, indent=2), file_name="metriq_inspection.json", mime="application/json")

elif page == "Inspection History":
    st.markdown("### 🗂️ Inspection history")
    if not st.session_state.history:
        st.info("No inspections in this browser session yet. Run the Demo Scan first.")
    else:
        for h in st.session_state.history:
            icon = "🟢" if h["status"] == "COMPLIANT" else "🔴" if h["status"] == "NON-COMPLIANT" else "🟠"
            st.markdown(f"<div class='card'>{icon} <b>{h['inspection_id']}</b> — {h['product_id']} — <b>{h['status']}</b><br><span class='small'>{h['timestamp']} • {h['location']} • Score {h['score']}% • {h['violations']} issue(s)</span></div>", unsafe_allow_html=True)

elif page == "Rules & Method":
    st.markdown("### ⚖️ Rules knowledge base")
    st.warning("This prototype encodes a focused screening subset for demonstration. It is not a substitute for the current official Rules, amendments, exemptions, notifications, or an authorized legal determination.")
    for r in result_rules_for_display():
        st.markdown(f"**{r['id']} — {r['name']}**")
        st.write(r['description'])
        st.caption(f"Validation: {r['validation']}")
        st.divider()

elif page == "About":
    st.markdown("### 🇮🇳 MetrIQ — SIH 26034 demo")
    st.markdown("MetrIQ is a Python-first proof of concept for assisted inspection of packaged commodities. Its architecture separates **AI extraction** from **deterministic compliance rules**, so an inspector can trace a finding back to evidence and a rule identifier.")
    st.markdown("#### Design principles")
    st.markdown("- Evidence first: every finding should be explainable.\n- Human-in-the-loop: ambiguous cases become **REVIEW**, not fake certainty.\n- Rule versioning: legal logic is kept separately from the UI.\n- India-first workflow: inspector, location, product, evidence and report are first-class objects.\n- Portable demo: no paid API key is required for the built-in demo scan.")
    st.markdown("#### Roadmap")
    st.markdown("1. Production OCR + layout detection\n2. Camera capture and multi-side package stitching\n3. Calibrated font/character-height measurement\n4. E-commerce listing comparison\n5. PostgreSQL + object storage repository\n6. Role-based authentication and audit logs\n7. Versioned official rule corpus and amendment workflow")


def result_rules_for_display():
    from rules import RULES
    return RULES

st.markdown('<div class="footer">MetrIQ • SIH 26034 • Prototype for demonstration only • 🇮🇳 Built with Python + Streamlit</div>', unsafe_allow_html=True)
