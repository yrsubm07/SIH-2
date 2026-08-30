from __future__ import annotations

import io
import json
from datetime import datetime

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

from rules import RULES, RULES_VERSION, SAMPLE_PRODUCT_TEXT, analyze_product

st.set_page_config(page_title="MetrIQ — Legal Metrology Inspector", page_icon="🇮🇳", layout="wide")

st.markdown("""
<style>
.stApp{background:#f5f7fa;color:#172033}.hero{padding:28px 32px;border-radius:18px;color:white;background:linear-gradient(135deg,#0b1f3a,#12466f 65%,#138a4b);box-shadow:0 10px 30px #0b1f3a22;margin-bottom:20px}.hero h1{margin:4px 0;font-size:36px}.hero p{margin:0;color:#dce8f4}.metric,.finding,.rule{background:white;border:1px solid #e5eaf0;border-radius:14px;padding:16px;margin-bottom:10px}.metric .k{font-size:11px;text-transform:uppercase;color:#667085;letter-spacing:.5px}.metric .v{font-size:26px;font-weight:800;margin-top:4px}.small{font-size:12px;color:#667085}.section{font-size:21px;font-weight:800;margin:24px 0 10px}.good{color:#087443}.bad{color:#b42318}.warn{color:#b54708}.stButton>button{border-radius:10px;font-weight:700}
</style>
""", unsafe_allow_html=True)


def demo_label() -> Image.Image:
    img = Image.new("RGB", (1200, 780), "white")
    d = ImageDraw.Draw(img)
    try:
        b = ImageFont.truetype("DejaVuSans-Bold.ttf", 48)
        h = ImageFont.truetype("DejaVuSans-Bold.ttf", 30)
        p = ImageFont.truetype("DejaVuSans.ttf", 25)
        s = ImageFont.truetype("DejaVuSans.ttf", 19)
    except Exception:
        b = h = p = s = None
    d.rectangle((0,0,1200,18), fill="#ff9933"); d.rectangle((0,18,1200,36), fill="white"); d.rectangle((0,36,1200,54), fill="#138a4b")
    lines=[("BHARAT NATURAL FOODS",b,55,85),("Premium Whole Wheat Biscuits",h,58,155),("NET QUANTITY: 100 g",p,58,220),("MRP ₹50.00 (INCLUSIVE OF ALL TAXES)",p,58,275),("Manufactured & Packed by: Bharat Foods Pvt. Ltd.",p,58,335),("Plot 18, Industrial Area, New Delhi - 110020",s,58,375),("Consumer Care: 1800-123-4567 | care@bharatfoods.in",s,58,425),("Packed: 06/2026   Best Before: 06/2027",s,58,470),("Country of Origin: India",s,58,515)]
    for text,font,x,y in lines: d.text((x,y),text,fill="#111111",font=font)
    d.text((820,200),"₹50",fill="#b42318",font=b); d.rectangle((790,185,1100,285),outline="#b42318",width=5)
    d.text((790,620),"DEMO LABEL — synthetic training image",fill="#667085",font=s)
    return img


def ocr(img: Image.Image):
    try:
        import pytesseract
        text=pytesseract.image_to_string(img)
        if text.strip(): return text,"Tesseract OCR"
    except Exception:
        pass
    return "","OCR unavailable — demo fallback/manual verification"


def status_text(status):
    return {"COMPLIANT":"COMPLIANT","NON-COMPLIANT":"NON-COMPLIANT","REVIEW":"REVIEW REQUIRED"}.get(status,status)

if "history" not in st.session_state: st.session_state.history=[]

st.sidebar.markdown("### 🇮🇳 MetrIQ")
st.sidebar.caption("Legal Metrology Inspection Intelligence")
page=st.sidebar.radio("Navigate",["Inspection Desk","Inspection History","Rules & Method","About"])
st.sidebar.divider(); st.sidebar.markdown("**SIH PS:** 26034"); st.sidebar.markdown(f"**Rules KB:** {RULES_VERSION}")
st.sidebar.caption("AI assists inspection; it does not replace statutory or physical verification.")

st.markdown('<div class="hero"><div>🇮🇳 GOVERNMENT-STYLE INSPECTION WORKFLOW • CONSUMER PROTECTION</div><h1>MetrIQ</h1><p>AI-assisted packaged commodity compliance screening for Legal Metrology (Packaged Commodities) Rules, 2011.</p></div>',unsafe_allow_html=True)

if page=="Inspection Desk":
    st.markdown('<div class="section">🔍 New Inspection</div>',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    inspector=a.text_input("Inspector name","Demo Inspector"); location=b.text_input("Inspection location","New Delhi"); product_id=c.text_input("Product / SKU ID","DEMO-BF-100G")
    uploaded=st.file_uploader("Upload product / label image",type=["png","jpg","jpeg","webp"])
    demo=st.button("🇮🇳 Run Demo Scan",type="primary",use_container_width=True)
    image=None; source=""
    if uploaded: image=Image.open(uploaded).convert("RGB"); source=uploaded.name
    elif demo: image=demo_label(); source="synthetic_demo_label.png"
    if image:
        left,right=st.columns([1.05,1])
        with left: st.image(image,caption=source,use_container_width=True)
        with right:
            st.markdown("#### 1. Extract declarations")
            extracted,engine=ocr(image)
            if demo and not extracted.strip(): extracted=SAMPLE_PRODUCT_TEXT; engine="Built-in demo extraction pipeline"
            text=st.text_area("OCR / extracted text — editable for verification",extracted,height=270)
            st.caption(engine)
            analyze=st.button("Analyze compliance →",type="primary",use_container_width=True)
        if analyze:
            result=analyze_product(text)
            inspection={"inspection_id":f"INSP-{datetime.now():%Y%m%d-%H%M%S}","timestamp":datetime.now().isoformat(timespec="seconds"),"product_id":product_id,"location":location,"inspector":inspector,"status":result["status"],"score":result["score"],"violations":len(result["violations"])}
            st.session_state.last_result=result; st.session_state.last_report={**inspection,"problem_statement":"SIH 26034","rules_version":RULES_VERSION,"result":result}; st.session_state.history.insert(0,inspection)
    if "last_result" in st.session_state:
        r=st.session_state.last_result
        st.markdown('<div class="section">2. Compliance decision</div>',unsafe_allow_html=True)
        m1,m2,m3,m4=st.columns(4)
        cls="good" if r["status"]=="COMPLIANT" else "bad" if r["status"]=="NON-COMPLIANT" else "warn"
        m1.markdown(f'<div class="metric"><div class="k">Status</div><div class="v {cls}">{status_text(r["status"])}</div></div>',unsafe_allow_html=True)
        m2.markdown(f'<div class="metric"><div class="k">Compliance score</div><div class="v">{r["score"]}%</div></div>',unsafe_allow_html=True)
        m3.markdown(f'<div class="metric"><div class="k">Rules checked</div><div class="v">{r["checked"]}</div></div>',unsafe_allow_html=True)
        m4.markdown(f'<div class="metric"><div class="k">Issues</div><div class="v bad">{len(r["violations"])}</div></div>',unsafe_allow_html=True)
        st.markdown('<div class="section">3. Declaration matrix</div>',unsafe_allow_html=True)
        for item in r["checks"]:
            icon={"PASS":"✅","FAIL":"❌","REVIEW":"⚠️"}[item["status"]]
            x,y,z=st.columns([.07,.35,.38,.2]) if False else st.columns([.07,.35,.38,.20])
            x.markdown(f"### {icon}"); y.markdown(f"**{item['name']}**"); z.markdown(f"{item['detail']}  \n`{item['rule']}`")
        st.markdown('<div class="section">4. Evidence-backed findings</div>',unsafe_allow_html=True)
        if r["violations"]:
            for i,v in enumerate(r["violations"],1):
                st.markdown(f'<div class="finding"><b>{i}. {v["title"]}</b><br><b>Finding:</b> {v["finding"]}<br><b>Rule:</b> <code>{v["rule"]}</code><br><b>Evidence:</b> {v["evidence"]}<br><b>Confidence:</b> {v["confidence"]} • <b>Action:</b> {v["action"]}</div>',unsafe_allow_html=True)
        else: st.success("No rule-triggered issues detected. Physical verification may still be required.")
        st.markdown('<div class="section">5. Export</div>',unsafe_allow_html=True)
        st.download_button("Download JSON inspection report",json.dumps(st.session_state.last_report,indent=2),file_name="metriq_inspection.json",mime="application/json")

elif page=="Inspection History":
    st.markdown('<div class="section">🗂️ Inspection history</div>',unsafe_allow_html=True)
    if not st.session_state.history: st.info("No inspections in this browser session yet. Run the Demo Scan first.")
    for h in st.session_state.history:
        icon="🟢" if h["status"]=="COMPLIANT" else "🔴" if h["status"]=="NON-COMPLIANT" else "🟠"
        st.markdown(f'<div class="metric">{icon} <b>{h["inspection_id"]}</b> — {h["product_id"]} — <b>{h["status"]}</b><br><span class="small">{h["timestamp"]} • {h["location"]} • Score {h["score"]}% • {h["violations"]} issue(s)</span></div>',unsafe_allow_html=True)

elif page=="Rules & Method":
    st.markdown('<div class="section">⚖️ Rules knowledge base</div>',unsafe_allow_html=True)
    st.warning("Prototype screening subset only. Do not treat this demo as an authoritative statutory determination. Synchronize the production rules corpus with current official Rules, amendments, exemptions and notifications.")
    for r in RULES:
        st.markdown(f'<div class="rule"><b>{r["id"]} — {r["name"]}</b><br>{r["description"]}<br><span class="small">Validation: {r["validation"]}</span></div>',unsafe_allow_html=True)

else:
    st.markdown('<div class="section">🇮🇳 About MetrIQ</div>',unsafe_allow_html=True)
    st.write("MetrIQ is a Python-first proof of concept for assisted inspection of packaged commodities. It deliberately separates AI extraction from deterministic compliance rules so findings remain explainable and auditable.")
    st.markdown("**Core principles**")
    st.markdown("- Evidence first: findings should trace to visible/extracted evidence.\n- Human in the loop: ambiguous cases become REVIEW, not fake certainty.\n- Versioned rules: legal logic stays separate from UI.\n- No secret/API key required for the built-in demo.\n- Physical measurements from photographs are estimates unless calibrated.")
    st.markdown("**Planned production upgrades**")
    st.markdown("1. OCR bounding boxes + layout detection  \n2. Camera capture and perspective correction  \n3. Calibrated font/character-height analysis  \n4. E-commerce listing comparison  \n5. PostgreSQL/object storage repository  \n6. RBAC + audit logs  \n7. Versioned official legal corpus and amendment workflow")

st.markdown('<div class="small" style="margin-top:30px">MetrIQ • SIH 26034 • Prototype • AI-assisted screening only • 🇮🇳</div>',unsafe_allow_html=True)
