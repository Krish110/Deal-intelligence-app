import streamlit as st
import google.generativeai as genai
import os
import json
import time
from pathlib import Path

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Inter Gold · Deal Intelligence",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root variables ── */
:root {
    --ink:     #07070D;
    --deep:    #0F0C1F;
    --rich:    #181330;
    --card:    #1C1840;
    --border:  #2A2550;
    --gold:    #C8961E;
    --lgold:   #EDD270;
    --violet:  #5225C1;
    --lilac:   #9272E0;
    --soft:    #C8B5F5;
    --white:   #FFFFFF;
    --lgray:   #CCCCCC;
    --gray:    #888888;
    --red:     #CC2222;
    --green:   #1A7A4A;
    --amber:   #C8761E;
}

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--ink) !important;
    color: var(--white) !important;
}

.stApp { background-color: var(--ink) !important; }

/* ── Hide default streamlit elements ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 3rem 2rem !important; max-width: 1400px !important; }

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, var(--deep) 0%, var(--rich) 50%, var(--deep) 100%);
    border-bottom: 1px solid var(--border);
    padding: 3rem 2rem 2.5rem 2rem;
    margin: -1rem -2rem 2.5rem -2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; left: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(82,37,193,0.25) 0%, transparent 70%);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -40px; right: -40px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(200,150,30,0.2) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-eyebrow {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.35em;
    color: var(--lilac);
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    font-weight: 900;
    line-height: 1.05;
    margin: 0 0 0.8rem 0;
    background: linear-gradient(135deg, var(--white) 0%, var(--lgold) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 1.05rem;
    color: var(--lgray);
    font-weight: 300;
    max-width: 600px;
    line-height: 1.6;
}

/* ── Upload zone ── */
.upload-zone {
    background: var(--deep);
    border: 2px dashed var(--border);
    border-radius: 16px;
    padding: 2.5rem;
    text-align: center;
    transition: border-color 0.3s;
    margin-bottom: 1.5rem;
}
.upload-zone:hover { border-color: var(--violet); }
.upload-label {
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem;
    color: var(--soft);
    margin-bottom: 0.4rem;
}
.upload-hint {
    font-size: 0.82rem;
    color: var(--gray);
}

/* ── Cards ── */
.intel-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.6rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
}
.intel-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: var(--accent-color, var(--violet));
    border-radius: 4px 0 0 4px;
}
.card-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--gray);
    margin-bottom: 0.6rem;
    font-family: 'DM Sans', sans-serif;
}
.card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--white);
    margin-bottom: 0.8rem;
}
.card-body {
    font-size: 0.92rem;
    color: var(--lgray);
    line-height: 1.75;
}

/* ── Verdict banner ── */
.verdict-go {
    background: linear-gradient(135deg, #0A2A1A 0%, #0F3D25 100%);
    border: 1px solid var(--green);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
}
.verdict-caution {
    background: linear-gradient(135deg, #2A1A00 0%, #3D2800 100%);
    border: 1px solid var(--amber);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
}
.verdict-avoid {
    background: linear-gradient(135deg, #2A0A0A 0%, #3D1010 100%);
    border: 1px solid var(--red);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
}
.verdict-title {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 900;
    margin: 0 0 0.5rem 0;
}
.verdict-sub {
    font-size: 0.95rem;
    color: var(--lgray);
    line-height: 1.65;
}

/* ── Section headers ── */
.section-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--white);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.6rem;
    margin: 2rem 0 1.2rem 0;
}

/* ── Approach steps ── */
.step-block {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    align-items: flex-start;
}
.step-num {
    background: var(--violet);
    color: var(--white);
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    font-weight: 700;
    width: 32px; height: 32px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
}
.step-text {
    font-size: 0.93rem;
    color: var(--lgray);
    line-height: 1.7;
}
.step-head { font-weight: 600; color: var(--white); }

/* ── Warning pills ── */
.pill-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.6rem 0; }
.pill {
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    font-family: 'DM Sans', sans-serif;
}
.pill-red   { background: rgba(204,34,34,0.18);  color: #FF8888; border: 1px solid rgba(204,34,34,0.4); }
.pill-gold  { background: rgba(200,150,30,0.18); color: var(--lgold); border: 1px solid rgba(200,150,30,0.4); }
.pill-green { background: rgba(26,122,74,0.18);  color: #66FFAA; border: 1px solid rgba(26,122,74,0.4); }
.pill-blue  { background: rgba(82,37,193,0.2);   color: var(--soft); border: 1px solid rgba(82,37,193,0.4); }

/* ── Metric row ── */
.metric-row {
    display: flex;
    gap: 1rem;
    margin: 1rem 0;
    flex-wrap: wrap;
}
.metric-box {
    background: var(--deep);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.4rem;
    flex: 1;
    min-width: 140px;
}
.metric-val {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--gold);
    line-height: 1;
    margin-bottom: 0.3rem;
}
.metric-lbl {
    font-size: 0.72rem;
    color: var(--gray);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-weight: 600;
}

/* ── Quote block ── */
.quote-block {
    background: var(--deep);
    border-left: 3px solid var(--gold);
    border-radius: 0 10px 10px 0;
    padding: 1.1rem 1.4rem;
    margin: 1rem 0;
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem;
    font-style: italic;
    color: var(--lgold);
    line-height: 1.7;
}

/* ── Streamlit widget overrides ── */
.stFileUploader > div {
    background: var(--deep) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 14px !important;
    color: var(--white) !important;
}
.stFileUploader label { color: var(--soft) !important; font-family: 'DM Sans', sans-serif !important; }
.stButton > button {
    background: linear-gradient(135deg, var(--violet), #3B1FA0) !important;
    color: var(--white) !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.7rem 2rem !important;
    width: 100% !important;
    transition: all 0.3s !important;
    letter-spacing: 0.05em !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #6B3FD1, var(--violet)) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(82,37,193,0.4) !important;
}
.stSelectbox > div > div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--white) !important;
}
.stSpinner > div { color: var(--gold) !important; }
div[data-testid="stMarkdownContainer"] p { color: var(--lgray) !important; }
.stProgress > div > div { background: var(--violet) !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 2rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--ink); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--violet); }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">💎 DiamondCraft India · Surat · IGI Certified Lab-Grown Diamonds</div>
    <div class="hero-title">Deal Intelligence Engine</div>
    <div class="hero-sub">
        Upload any retailer's annual report. Get a complete strategic brief —
        should you pursue the deal, how to approach them, and exactly what to watch out for.
    </div>
</div>
""", unsafe_allow_html=True)

# ── System prompt ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are a senior B2B sales strategist and market intelligence analyst for DiamondCraft India — a Surat-based manufacturer of IGI-certified lab-grown diamond (LGD) jewellery. 

YOUR COMPANY:
- Inter Gold India, (world's diamond manufacturing capital)
- Products: IGI/GIA certified lab-grown diamond jewellery — solitaire studs, pendants, rings, tennis bracelets, bridal sets
- Positioning: Real certified diamonds at 60-80% lower cost than mined, solar-powered CVD facility, full traceability
- Target price range: €30–€1,000 wholesale depending on format
- Delivery: DDP (Delivered Duty Paid) to Europe, UK, Australia
- Capabilities: White-label manufacturing, own brand, bulk supply
- Certifications: IGI, GIA, BIS Hallmark, GJEPC member
- Key advantage: India-Australia ECTA (0% duty), UK-India FTA (imminent), EU-India FTA (pending)

YOUR TASK:
Analyse the uploaded annual report from a retailer's perspective and produce a structured deal intelligence brief. You must extract signals specifically relevant to whether this retailer should stock lab-grown diamond jewellery from DiamondCraft India.

Look for:
1. Jewellery/accessories category mentions — size, growth, strategy
2. Sustainability commitments — ESG targets, ethical sourcing pledges
3. Financial health — revenue trends, margin pressure, debt levels
4. Geographic expansion — which markets they are entering or exiting
5. Consumer insights — who their shopper is, what she buys, average basket
6. Competitor mentions — do they reference Pandora, Swarovski, fine jewellery brands?
7. Category gaps — what are they NOT doing that they should be?
8. Strategic priorities — what are their 3-5 year ambitions?
9. Supply chain signals — are they diversifying away from existing suppliers?
10. Risk flags — financial distress, legal issues, market exit signals

OUTPUT FORMAT:
Return a valid JSON object with exactly this structure. No text before or after the JSON.

{
  "company_name": "string",
  "report_year": "string",
  "verdict": "GO" | "PROCEED WITH CAUTION" | "AVOID",
  "verdict_reason": "One powerful sentence explaining the verdict",
  "confidence_score": number between 1-10,
  "deal_potential": "HIGH" | "MEDIUM" | "LOW",
  "estimated_year1_eur": "string e.g. €200,000 – €500,000",
  "estimated_year3_eur": "string e.g. €800,000 – €2,000,000",
  "jewellery_signals": {
    "has_jewellery_category": true | false,
    "jewellery_revenue_mentioned": "string or null",
    "jewellery_growth_trend": "GROWING" | "STABLE" | "DECLINING" | "NOT MENTIONED",
    "lgd_mentioned": true | false,
    "competitor_brands_mentioned": ["string array of any jewellery brands mentioned"],
    "key_quote": "Most relevant direct quote from the report about jewellery/accessories, or null"
  },
  "esg_signals": {
    "has_sustainability_commitments": true | false,
    "esg_score": 1-10,
    "relevant_commitments": ["array of ESG commitments relevant to LGD pitch"],
    "lgd_esg_fit": "string explaining how LGD fits their ESG agenda"
  },
  "financial_health": {
    "revenue_trend": "GROWING" | "STABLE" | "DECLINING",
    "margin_pressure": true | false,
    "financial_risk_flags": ["array of any financial concerns"],
    "counterparty_risk": "LOW" | "MEDIUM" | "HIGH"
  },
  "shopper_profile": {
    "primary_demographic": "string",
    "avg_basket_size": "string or null",
    "jewellery_buyer_insight": "string describing their jewellery buyer based on report"
  },
  "approach_strategy": {
    "entry_point": "string — who to contact and how",
    "opening_line": "string — the single best opening line for this specific retailer based on what you found in their report",
    "pitch_angle": "string — primary angle to use",
    "secondary_angle": "string — backup angle",
    "timing": "string — when to approach based on their fiscal calendar/strategy cycle"
  },
  "cautions": [
    {
      "flag": "string — short flag name",
      "severity": "HIGH" | "MEDIUM" | "LOW",
      "detail": "string — what to watch out for and why"
    }
  ],
  "opportunities": [
    {
      "opportunity": "string — short name",
      "strength": "HIGH" | "MEDIUM" | "LOW",
      "detail": "string — specific opportunity identified from the report"
    }
  ],
  "negotiation_leverage": ["array of specific points from their report you can use as leverage in negotiation"],
  "deal_structure_recommendation": "string — recommended deal structure for this specific retailer",
  "red_lines": ["array of things you must NOT say or do with this specific retailer"],
  "first_meeting_agenda": ["array of 4-5 agenda points for the first buyer meeting, specific to this retailer"]
}"""

# ── Helper: PDF to base64 ─────────────────────────────────────
def upload_pdf_to_gemini(uploaded_file):
    """Upload PDF bytes to Gemini Files API and return the file object."""
    genai.configure(api_key=st.secrets["AIzaSyACJ_nIa23Tys1zfAFK88KlTMJu0gh6DPg"])
    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()
    # Write to a temp file — Gemini Files API needs a file path
    tmp_path = f"/tmp/{uploaded_file.name}"
    with open(tmp_path, "wb") as f:
        f.write(pdf_bytes)
    gemini_file = genai.upload_file(tmp_path, mime_type="application/pdf")
    return gemini_file

# ── Helper: Call Claude ───────────────────────────────────────
def analyse_report(gemini_file, retailer_hint: str = "") -> dict:
    """Send uploaded PDF file + prompt to Gemini and parse JSON response."""
    genai.configure(api_key=st.secrets["AIzaSyACJ_nIa23Tys1zfAFK88KlTMJu0gh6DPg"])

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        system_instruction=SYSTEM_PROMPT
    )

    user_prompt = f"""Analyse this annual report and return the JSON intelligence brief.
{f'Retailer context hint: {retailer_hint}' if retailer_hint else ''}
Remember: return ONLY valid JSON, no text before or after."""

    response = model.generate_content(
        [gemini_file, user_prompt],
        generation_config=genai.GenerationConfig(
            max_output_tokens=4000,
            temperature=0.2
        )
    )

    raw = response.text.strip()
    # Strip markdown fences if Gemini wraps in ```json ... ```
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip().rstrip("```").strip()
    return json.loads(raw)

# ── Helper: Render verdict ────────────────────────────────────
def render_verdict(data: dict):
    verdict = data.get("verdict", "PROCEED WITH CAUTION")
    reason  = data.get("verdict_reason", "")
    conf    = data.get("confidence_score", 5)
    y1      = data.get("estimated_year1_eur", "—")
    y3      = data.get("estimated_year3_eur", "—")
    dp      = data.get("deal_potential", "MEDIUM")

    cls = {"GO": "verdict-go", "AVOID": "verdict-avoid"}.get(verdict, "verdict-caution")
    icon = {"GO": "✅", "AVOID": "🚫"}.get(verdict, "⚠️")
    col  = {"GO": "#66FFAA", "AVOID": "#FF6666"}.get(verdict, "#FFD080")

    st.markdown(f"""
    <div class="{cls}">
        <div class="verdict-title" style="color:{col}">{icon} &nbsp;{verdict}</div>
        <div class="verdict-sub">{reason}</div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-box">
            <div class="metric-val">{conf}/10</div>
            <div class="metric-lbl">Confidence Score</div>
        </div>
        <div class="metric-box">
            <div class="metric-val">{dp}</div>
            <div class="metric-lbl">Deal Potential</div>
        </div>
        <div class="metric-box">
            <div class="metric-val" style="font-size:1.2rem">{y1}</div>
            <div class="metric-lbl">Est. Year 1 Revenue</div>
        </div>
        <div class="metric-box">
            <div class="metric-val" style="font-size:1.2rem">{y3}</div>
            <div class="metric-lbl">Est. Year 3 Upside</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Helper: Render section ────────────────────────────────────
def section(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

def intel_card(label: str, title: str, body: str, accent: str = "#5225C1"):
    st.markdown(f"""
    <div class="intel-card" style="--accent-color:{accent}">
        <div class="card-label">{label}</div>
        <div class="card-title">{title}</div>
        <div class="card-body">{body}</div>
    </div>
    """, unsafe_allow_html=True)

def pills(items: list, pill_class: str = "pill-blue"):
    if not items:
        return
    html = '<div class="pill-row">'
    for item in items:
        html += f'<span class="pill {pill_class}">{item}</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# ── Helper: Render full brief ─────────────────────────────────
def render_brief(data: dict):
    company = data.get("company_name", "Retailer")
    year    = data.get("report_year", "")

    st.markdown(f"<h2 style='font-family:Playfair Display,serif;color:var(--lgold);margin-bottom:0.2rem'>{company} · {year}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:var(--gray);font-size:0.85rem;margin-bottom:1.5rem'>Annual Report Intelligence Brief · DiamondCraft LGD Deal Analysis</p>", unsafe_allow_html=True)

    # ── 1. VERDICT ──
    section("01 · Deal Verdict")
    render_verdict(data)

    # ── 2. JEWELLERY SIGNALS ──
    section("02 · Jewellery & Category Signals")
    js = data.get("jewellery_signals", {})
    col1, col2 = st.columns(2)
    with col1:
        has_jwl = js.get("has_jewellery_category", False)
        lgd_ment = js.get("lgd_mentioned", False)
        trend = js.get("jewellery_growth_trend", "NOT MENTIONED")
        trend_color = {"GROWING":"#66FFAA","STABLE":"#FFD080","DECLINING":"#FF6666","NOT MENTIONED":"#888888"}.get(trend,"#888888")
        intel_card(
            "JEWELLERY CATEGORY",
            "Category Presence" if has_jwl else "No Jewellery Category Found",
            f"Jewellery category: {'<span style=\"color:#66FFAA\">✓ Present</span>' if has_jwl else '<span style=\"color:#FF6666\">✗ Not found</span>'}<br>"
            f"LGD mentioned: {'<span style=\"color:#66FFAA\">✓ Yes</span>' if lgd_ment else '<span style=\"color:#888\">No</span>'}<br>"
            f"Growth trend: <span style=\"color:{trend_color}\">{trend}</span><br>"
            f"Revenue: {js.get('jewellery_revenue_mentioned') or 'Not disclosed'}",
            "#C8961E"
        )
    with col2:
        competitors = js.get("competitor_brands_mentioned", [])
        intel_card(
            "COMPETITOR INTELLIGENCE",
            "Jewellery Brands in Their Ecosystem",
            f"Brands mentioned in report:<br>" + (", ".join(f"<span style='color:var(--lgold)'>{c}</span>" for c in competitors) if competitors else "<span style='color:var(--gray)'>None identified</span>"),
            "#9272E0"
        )

    quote = js.get("key_quote")
    if quote:
        st.markdown(f'<div class="quote-block">"{quote}"</div>', unsafe_allow_html=True)

    # ── 3. ESG SIGNALS ──
    section("03 · ESG & Sustainability Fit")
    esg = data.get("esg_signals", {})
    esg_score = esg.get("esg_score", 5)
    bar_color = "#66FFAA" if esg_score >= 7 else ("#FFD080" if esg_score >= 4 else "#FF6666")
    commitments = esg.get("relevant_commitments", [])
    lgd_fit = esg.get("lgd_esg_fit", "")

    st.markdown(f"""
    <div class="intel-card" style="--accent-color:{bar_color}">
        <div class="card-label">ESG ALIGNMENT SCORE</div>
        <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem">
            <div style="font-family:'Playfair Display',serif;font-size:2.5rem;font-weight:700;color:{bar_color}">{esg_score}/10</div>
            <div style="flex:1;background:var(--border);border-radius:4px;height:8px">
                <div style="width:{esg_score*10}%;background:{bar_color};height:8px;border-radius:4px;transition:width 1s"></div>
            </div>
        </div>
        <div class="card-body">{lgd_fit}</div>
    </div>
    """, unsafe_allow_html=True)

    if commitments:
        st.markdown("<p style='color:var(--gray);font-size:0.82rem;margin:0.5rem 0 0.3rem'>ESG commitments relevant to LGD pitch:</p>", unsafe_allow_html=True)
        pills(commitments, "pill-green")

    # ── 4. FINANCIAL HEALTH ──
    section("04 · Financial Health & Counterparty Risk")
    fin = data.get("financial_health", {})
    rev_trend = fin.get("revenue_trend", "STABLE")
    risk = fin.get("counterparty_risk", "MEDIUM")
    risk_col = {"LOW":"#66FFAA","MEDIUM":"#FFD080","HIGH":"#FF6666"}.get(risk,"#FFD080")
    rev_col  = {"GROWING":"#66FFAA","STABLE":"#FFD080","DECLINING":"#FF6666"}.get(rev_trend,"#FFD080")
    flags = fin.get("financial_risk_flags", [])

    col1, col2 = st.columns(2)
    with col1:
        intel_card("REVENUE TREND", f"<span style='color:{rev_col}'>{rev_trend}</span>", "Based on reported figures in annual report.", rev_col)
    with col2:
        intel_card("COUNTERPARTY RISK", f"<span style='color:{risk_col}'>{risk}</span>", "Risk of non-payment or commercial instability.", risk_col)

    if flags:
        st.markdown("<p style='color:var(--gray);font-size:0.82rem;margin:0.5rem 0 0.3rem'>Risk flags identified:</p>", unsafe_allow_html=True)
        pills(flags, "pill-red")

    # ── 5. SHOPPER PROFILE ──
    section("05 · Their Shopper — Is She Your Buyer?")
    sp = data.get("shopper_profile", {})
    intel_card(
        "SHOPPER INTELLIGENCE",
        sp.get("primary_demographic", "Not specified"),
        f"Average basket: {sp.get('avg_basket_size') or 'Not disclosed'}<br><br>"
        f"{sp.get('jewellery_buyer_insight', 'No jewellery buyer insight available from report.')}",
        "#5225C1"
    )

    # ── 6. APPROACH STRATEGY ──
    section("06 · Your Approach Strategy")
    ap = data.get("approach_strategy", {})

    st.markdown(f'<div class="quote-block">{ap.get("opening_line", "")}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        intel_card("PRIMARY PITCH ANGLE", ap.get("pitch_angle", "")[:60]+"...", ap.get("pitch_angle", ""), "#C8961E")
    with col2:
        intel_card("SECONDARY ANGLE", ap.get("secondary_angle", "")[:60]+"...", ap.get("secondary_angle", ""), "#9272E0")

    intel_card("WHO TO CONTACT & WHEN", ap.get("entry_point", ""), ap.get("timing", ""), "#5225C1")

    # ── 7. OPPORTUNITIES ──
    section("07 · Opportunities Identified in Their Report")
    opps = data.get("opportunities", [])
    for opp in opps:
        strength = opp.get("strength", "MEDIUM")
        scol = {"HIGH":"#C8961E","MEDIUM":"#9272E0","LOW":"#888888"}.get(strength,"#9272E0")
        intel_card(
            f"OPPORTUNITY · {strength} STRENGTH",
            opp.get("opportunity", ""),
            opp.get("detail", ""),
            scol
        )

    # ── 8. CAUTIONS ──
    section("08 · Cautions & Red Flags")
    cautions = data.get("cautions", [])
    for c in cautions:
        sev = c.get("severity", "MEDIUM")
        scol = {"HIGH":"#CC2222","MEDIUM":"#C8761E","LOW":"#888888"}.get(sev,"#C8761E")
        flag_icon = {"HIGH":"🔴","MEDIUM":"🟡","LOW":"⚪"}.get(sev,"🟡")
        intel_card(
            f"{flag_icon} {sev} SEVERITY",
            c.get("flag", ""),
            c.get("detail", ""),
            scol
        )

    # ── 9. NEGOTIATION LEVERAGE ──
    section("09 · Your Negotiation Leverage")
    leverage = data.get("negotiation_leverage", [])
    if leverage:
        for i, point in enumerate(leverage, 1):
            st.markdown(f"""
            <div style="display:flex;gap:1rem;margin-bottom:0.8rem;align-items:flex-start">
                <div style="background:var(--gold);color:var(--ink);font-family:'Playfair Display',serif;font-weight:700;
                    width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;
                    flex-shrink:0;font-size:0.85rem">{i}</div>
                <div style="font-size:0.93rem;color:var(--lgray);line-height:1.7;padding-top:3px">{point}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── 10. RED LINES ──
    section("10 · What NOT to Say or Do")
    red_lines = data.get("red_lines", [])
    if red_lines:
        for rl in red_lines:
            st.markdown(f"""
            <div style="display:flex;gap:0.8rem;margin-bottom:0.6rem;align-items:flex-start">
                <span style="color:#FF4444;font-size:1rem;flex-shrink:0">✗</span>
                <div style="font-size:0.92rem;color:var(--lgray);line-height:1.7">{rl}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── 11. DEAL STRUCTURE ──
    section("11 · Recommended Deal Structure")
    intel_card(
        "DEAL RECOMMENDATION",
        "How to structure this partnership",
        data.get("deal_structure_recommendation", ""),
        "#C8961E"
    )

    # ── 12. FIRST MEETING AGENDA ──
    section("12 · First Buyer Meeting Agenda")
    agenda = data.get("first_meeting_agenda", [])
    if agenda:
        for i, item in enumerate(agenda, 1):
            st.markdown(f"""
            <div style="display:flex;gap:1rem;margin-bottom:0.8rem;align-items:flex-start">
                <div style="background:var(--violet);color:var(--white);font-family:'Playfair Display',serif;font-weight:700;
                    width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;
                    flex-shrink:0;font-size:0.88rem">{i}</div>
                <div style="font-size:0.93rem;color:var(--lgray);line-height:1.7;padding-top:4px">{item}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Footer ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align:center;padding:1.5rem;border-top:1px solid var(--border);margin-top:2rem">
        <div style="font-family:'Playfair Display',serif;font-size:1rem;color:var(--gold);margin-bottom:0.3rem">DiamondCraft India · Surat</div>
        <div style="font-size:0.78rem;color:var(--gray)">IGI Certified Lab-Grown Diamond Jewellery · partnerships@diamondcraftindia.com</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════

# Session state
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "analysing" not in st.session_state:
    st.session_state.analysing = False

# ── Upload section ────────────────────────────────────────────
col_upload, col_info = st.columns([1.6, 1])

with col_upload:
    st.markdown('<div class="card-label" style="margin-bottom:0.6rem">UPLOAD ANNUAL REPORT</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Drop the retailer's annual report PDF here",
        type=["pdf"],
        label_visibility="collapsed"
    )

    retailer_hint = st.text_input(
        "Retailer name (optional — helps the AI orient faster)",
        placeholder="e.g. H&M, Zalando, John Lewis...",
        label_visibility="visible"
    )

    if uploaded:
        file_size_mb = uploaded.size / (1024*1024)
        st.markdown(f"""
        <div style="background:var(--deep);border:1px solid var(--border);border-radius:10px;
            padding:0.8rem 1.2rem;margin:0.5rem 0;display:flex;align-items:center;gap:0.8rem">
            <span style="font-size:1.2rem">📄</span>
            <div>
                <div style="font-size:0.9rem;color:var(--white);font-weight:500">{uploaded.name}</div>
                <div style="font-size:0.75rem;color:var(--gray)">{file_size_mb:.1f} MB · PDF</div>
            </div>
            <span style="margin-left:auto;color:#66FFAA;font-size:0.8rem">✓ Ready</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💎 Analyse Annual Report", type="primary"):
            st.session_state.analysing = True
            st.session_state.analysis = None

with col_info:
    st.markdown("""
    <div class="intel-card" style="--accent-color:#C8961E;height:fit-content">
        <div class="card-label">WHAT YOU GET</div>
        <div class="card-title">12-Point Deal Brief</div>
        <div class="card-body">
            <div style="margin-bottom:0.5rem">✓ &nbsp;<strong>GO / CAUTION / AVOID</strong> verdict</div>
            <div style="margin-bottom:0.5rem">✓ &nbsp;Jewellery category signals</div>
            <div style="margin-bottom:0.5rem">✓ &nbsp;ESG alignment score</div>
            <div style="margin-bottom:0.5rem">✓ &nbsp;Financial health check</div>
            <div style="margin-bottom:0.5rem">✓ &nbsp;Shopper profile match</div>
            <div style="margin-bottom:0.5rem">✓ &nbsp;Approach strategy & opening line</div>
            <div style="margin-bottom:0.5rem">✓ &nbsp;Opportunities from their own report</div>
            <div style="margin-bottom:0.5rem">✓ &nbsp;Cautions & red flags</div>
            <div style="margin-bottom:0.5rem">✓ &nbsp;Your negotiation leverage</div>
            <div style="margin-bottom:0.5rem">✓ &nbsp;What NOT to say</div>
            <div style="margin-bottom:0.5rem">✓ &nbsp;Recommended deal structure</div>
            <div>✓ &nbsp;First meeting agenda</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Analysis runner ───────────────────────────────────────────
if st.session_state.analysing and uploaded is not None:
    st.markdown("<hr>", unsafe_allow_html=True)

    progress_container = st.empty()
    status_container   = st.empty()

    steps = [
        (0.10, "Reading the annual report..."),
        (0.25, "Scanning jewellery & accessories sections..."),
        (0.40, "Extracting ESG commitments..."),
        (0.55, "Analysing financial health & risk flags..."),
        (0.70, "Building approach strategy..."),
        (0.85, "Identifying negotiation leverage..."),
        (0.95, "Compiling your deal intelligence brief..."),
    ]

    try:
        gemini_file = upload_pdf_to_gemini(uploaded)

        for pct, msg in steps:
            progress_container.progress(pct)
            status_container.markdown(
                f"<p style='color:var(--lilac);font-size:0.9rem;text-align:center'>⟳ &nbsp;{msg}</p>",
                unsafe_allow_html=True
            )
            time.sleep(0.4)

        result = analyse_report(gemini_file, retailer_hint)
        st.session_state.analysis = result
        st.session_state.analysing = False

        progress_container.progress(1.0)
        status_container.markdown(
            "<p style='color:#66FFAA;font-size:0.9rem;text-align:center'>✓ &nbsp;Analysis complete</p>",
            unsafe_allow_html=True
        )
        time.sleep(0.8)
        progress_container.empty()
        status_container.empty()
        st.rerun()

    except json.JSONDecodeError as e:
        st.session_state.analysing = False
        st.error(f"The AI returned an unexpected format. Please try again. ({e})")
    except Exception as e:
        st.session_state.analysing = False
        st.error(f"Analysis failed: {str(e)}")

# ── Render result ─────────────────────────────────────────────
if st.session_state.analysis:
    st.markdown("<hr>", unsafe_allow_html=True)
    render_brief(st.session_state.analysis)

    # Download JSON
    st.markdown("<br>", unsafe_allow_html=True)
    company_name = st.session_state.analysis.get("company_name", "retailer").replace(" ", "_")
    st.download_button(
        label="⬇  Download Full Brief as JSON",
        data=json.dumps(st.session_state.analysis, indent=2),
        file_name=f"DiamondCraft_DealBrief_{company_name}.json",
        mime="application/json",
        use_container_width=True
    )

# ── Empty state ───────────────────────────────────────────────
if not uploaded and not st.session_state.analysis:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem;color:var(--gray)">
        <div style="font-size:3rem;margin-bottom:1rem">📋</div>
        <div style="font-family:'Playfair Display',serif;font-size:1.3rem;color:var(--soft);margin-bottom:0.5rem">
            Drop in any retailer's annual report
        </div>
        <div style="font-size:0.9rem;line-height:1.7;max-width:480px;margin:0 auto">
            Works with H&M, Zalando, John Lewis, El Corte Inglés, Otto, Inditex —
            or any retailer you are evaluating. Upload the PDF and get a complete
            deal intelligence brief in under 60 seconds.
        </div>
    </div>
    """, unsafe_allow_html=True)
