import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

# ──────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ethos Invest · Sustainable Portfolio Tool",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────
# GLOBAL CSS
# ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300;0,14..32,400;0,14..32,500;0,14..32,600;1,14..32,400&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0e1014;
    color: #c9cdd6;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0a0c10;
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * {
    color: #b8bcc6 !important;
}
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #52c98a !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    opacity: 0.9;
    margin-bottom: 10px;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: #d4d8e2 !important;
    font-size: 13px !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #1a5c38 0%, #217a4a 100%) !important;
    border: 1px solid rgba(82,201,138,0.2) !important;
    border-radius: 10px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em;
    color: #d6f5e6 !important;
    width: 100%;
    padding: 0.6rem;
    box-shadow: 0 1px 12px rgba(33,122,74,0.25);
    transition: all 0.2s ease;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #1f6e43 0%, #268f56 100%) !important;
    box-shadow: 0 2px 16px rgba(33,122,74,0.35);
}

/* ── Page header ── */
.page-header h1 {
    font-family: 'Inter', sans-serif;
    font-size: 28px;
    font-weight: 600;
    color: #eef0f4;
    letter-spacing: -0.03em;
    margin-bottom: 4px;
}
.page-header p {
    font-size: 13px;
    color: #666c7a;
    margin-top: 0;
}

/* ── Section label ── */
.section-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.18em;
    color: #52c98a;
    text-transform: uppercase;
    margin-top: 32px;
    margin-bottom: 12px;
    opacity: 0.85;
}

/* ── Card ── */
.card {
    background: #13161c;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 12px;
    color: #c9cdd6 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.4), 0 0 0 0.5px rgba(255,255,255,0.04) inset;
}
.card * { color: inherit !important; }

/* ── Metric tile ── */
.metric-tile {
    background: #13161c;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.4);
    position: relative;
    overflow: hidden;
}
.metric-tile::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #1f6b42, #52c98a, transparent);
    border-radius: 14px 14px 0 0;
}
.metric-tile .label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #555c6a !important;
    margin-bottom: 8px;
}
.metric-tile .value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px;
    font-weight: 500;
    color: #eef0f4 !important;
    letter-spacing: -0.03em;
}
.metric-tile .sub {
    font-size: 11px;
    color: #484e5c !important;
    margin-top: 6px;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Bar rows ── */
.bar-row { margin-bottom: 10px; }
.bar-label-row {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    font-weight: 500;
    margin-bottom: 6px;
    color: #8a909e !important;
    font-family: 'JetBrains Mono', monospace;
}
.bar-track {
    height: 5px;
    background: rgba(255,255,255,0.06);
    border-radius: 999px;
    overflow: hidden;
}
.bar-fill {
    height: 5px;
    border-radius: 999px;
    background: linear-gradient(90deg, #1f6b42, #52c98a);
}

/* ── Comparison table ── */
.cmp-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    color: #b8bcc6 !important;
}
.cmp-table th {
    background: transparent;
    color: #52c98a !important;
    padding: 10px 16px;
    text-align: left;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    border-bottom: 1px solid rgba(82,201,138,0.2);
}
.cmp-table td {
    padding: 9px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    color: #b8bcc6 !important;
    background: transparent;
}
.cmp-table tr:nth-child(even) td {
    background: rgba(255,255,255,0.02);
    color: #b8bcc6 !important;
}
.cmp-table tr:hover td {
    background: rgba(82,201,138,0.04);
}
.cmp-table tr:last-child td { border-bottom: none; }

/* ── Chips ── */
.chip {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.02em;
}
.chip-pos { background: rgba(82,201,138,0.12); color: #52c98a !important; border: 1px solid rgba(82,201,138,0.2); }
.chip-neg { background: rgba(224,90,90,0.12); color: #e05a5a !important; border: 1px solid rgba(224,90,90,0.2); }
.chip-neu { background: rgba(255,255,255,0.05); color: #7a8090 !important; border: 1px solid rgba(255,255,255,0.08); }

/* ── Divider ── */
hr.fancy-divider {
    border: none;
    height: 1px;
    background: rgba(255,255,255,0.06);
    margin: 28px 0;
}

/* ── Info / warn boxes ── */
.info-box {
    background: rgba(82,201,138,0.06);
    border: 1px solid rgba(82,201,138,0.15);
    border-left: 3px solid #52c98a;
    padding: 13px 16px;
    border-radius: 0 10px 10px 0;
    color: #9adcb8 !important;
    font-size: 13px;
    margin: 10px 0;
}
.warn-box {
    background: rgba(220,170,60,0.06);
    border: 1px solid rgba(220,170,60,0.15);
    border-left: 3px solid #dcaa3c;
    padding: 13px 16px;
    border-radius: 0 10px 10px 0;
    color: #d4b060 !important;
    font-size: 13px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)
# ──────────────────────────────────────────────────────────
# CORE LOGIC (from original top code — unchanged)
# ──────────────────────────────────────────────────────────
def portfolio_return(w1, r1, r2):
    return w1 * r1 + (1 - w1) * r2

def portfolio_sd(w1, sd1, sd2, rho):
    return np.sqrt(w1**2 * sd1**2 + (1-w1)**2 * sd2**2 + 2*rho*w1*(1-w1)*sd1*sd2)

def portfolio_esg(w1, esg1, esg2):
    return w1 * esg1 + (1 - w1) * esg2

def convert_to_100(score, agency):
    agency = agency.lower()
    try:
        if agency == "sustainalytics":
            s = float(score)
            return max(0.0, min(100.0, 100 - (s / 50) * 100)) if s < 50 else 0.0
        elif agency == "msci":
            msci_map = {"ccc": 0.0, "b": 16.7, "bb": 33.4, "bbb": 50.1,
                        "a": 66.8, "aa": 83.5, "aaa": 100.0}
            return msci_map.get(str(score).strip().lower(), 0.0)
        elif agency == "refinitiv":
            r_map = {0: 0.0, 1: 10.0, 2: 25.0, 3: 50.0, 4: 75.0, 5: 95.0}
            return r_map.get(int(float(score)), 0.0)
        elif agency == "s&p":
            return max(0.0, min(100.0, float(score)))
    except:
        return 0.0
    return 0.0


# ──────────────────────────────────────────────────────────
# UI HELPERS
# ──────────────────────────────────────────────────────────
def esg_hex(score: float) -> str:
    score = max(0.0, min(100.0, score))
    if score <= 50:
        t = score / 50.0
        r = 239; g = int(68 + t * (180 - 68)); b = int(68 + t * (8 - 68))
    else:
        t = (score - 50.0) / 50.0
        r = int(234 + t * (34 - 234))
        g = int(180 + t * (197 - 180))
        b = int(8   + t * (94 - 8))
    return f"#{r:02x}{g:02x}{b:02x}"

def progress_ring_html(score: float, subtitle: str = "ESG Score") -> str:
    col  = esg_hex(score)
    R    = 52
    circ = 2 * np.pi * R
    dash = (score / 100) * circ
    gap  = circ - dash
    return f"""
    <div style="display:flex;flex-direction:column;align-items:center;gap:6px;padding:8px 0;">
      <svg width="148" height="148" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="{R}" fill="none" stroke="{col}33" stroke-width="13"/>
        <circle cx="60" cy="60" r="{R}" fill="none" stroke="{col}" stroke-width="13"
                stroke-dasharray="{dash:.2f} {gap:.2f}" stroke-linecap="round"
                transform="rotate(-90 60 60)"/>
        <text x="60" y="55" text-anchor="middle" font-family="Inter,sans-serif"
              font-size="22" font-weight="700" fill="{col}">{score:.1f}</text>
        <text x="60" y="71" text-anchor="middle" font-family="Inter,sans-serif"
              font-size="11" fill="#94a3b8">/ 100</text>
      </svg>
      <span style="font-size:12px;font-weight:600;letter-spacing:0.08em;
                   text-transform:uppercase;color:#6b7b6e;">{subtitle}</span>
    </div>"""

def alloc_bar_html(w1, w2, name1, name2):
    c1, c2 = "#2e7d36", "#3b82f6"
    p1 = f"{w1*100:.1f}%"; p2 = f"{w2*100:.1f}%"
    return f"""
    <div class="bar-row">
      <div class="bar-label-row">
        <span style="color:{c1};">{name1}</span>
        <span style="color:{c1};">{p1}</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width:{p1};background:{c1};"></div>
      </div>
    </div>
    <div class="bar-row" style="margin-top:12px;">
      <div class="bar-label-row">
        <span style="color:{c2};">{name2}</span>
        <span style="color:{c2};">{p2}</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width:{p2};background:{c2};"></div>
      </div>
    </div>"""

def metric_tile(label, value, sub=""):
    sub_html = f'<div class="sub">{sub}</div>' if sub else ""
    return f"""
    <div class="metric-tile">
      <div class="label">{label}</div>
      <div class="value">{value}</div>
      {sub_html}
    </div>"""

def chip_html(value, suffix="", decimals=2):
    fmt = f"{value:+.{decimals}f}{suffix}"
    cls = "chip-pos" if value > 0.001 else ("chip-neg" if value < -0.001 else "chip-neu")
    return f'<span class="chip {cls}">{fmt}</span>'


# ──────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────
sb = st.sidebar

sb.markdown("""
<div style="padding:18px 0 10px;text-align:center;">
  <span style="font-family:'Playfair Display',serif;font-size:26px;
               color:#7ec984;letter-spacing:0.02em;">🌿 Ethos Invest</span><br>
  <span style="font-size:11px;color:#4a6b4e;letter-spacing:0.1em;
               text-transform:uppercase;">Sustainable Portfolio Tool</span>
</div>
""", unsafe_allow_html=True)
sb.markdown("---")

# ── Assets ────────────────────────────────────────────────
sb.markdown("### Assets & Market Data")

asset1_name = sb.text_input("Asset 1 Name", "Apple")
asset2_name = sb.text_input("Asset 2 Name", "Microsoft")

sb.markdown(f"**{asset1_name}**")
col_r1, col_v1 = sb.columns(2)
r1  = col_r1.number_input(f"Return %",    value=8.0,  key="r1")  / 100
sd1 = col_v1.number_input(f"Volatility %", value=15.0, key="sd1") / 100
agency1 = sb.selectbox(f"{asset1_name} Rating Agency",
                       ["S&P", "MSCI", "Sustainalytics", "Refinitiv"], key="ag1")

sb.markdown(f"**{asset2_name}**")
col_r2, col_v2 = sb.columns(2)
r2  = col_r2.number_input(f"Return %",    value=10.0, key="r2")  / 100
sd2 = col_v2.number_input(f"Volatility %", value=20.0, key="sd2") / 100
agency2 = sb.selectbox(f"{asset2_name} Rating Agency",
                       ["S&P", "MSCI", "Sustainalytics", "Refinitiv"], key="ag2")

sb.markdown("**Market Parameters**")
rho    = sb.slider("Correlation Coefficient (ρ)", -1.0, 1.0, 0.2, 0.01)
r_free = sb.number_input("Risk-free Rate %", value=2.0) / 100
sb.markdown("---")

# ── Risk Preference ───────────────────────────────────────
sb.markdown("### Risk Preference")
gamma_mode = sb.radio("Determine your Risk Aversion (γ):",
                      ["Manual Entry", "Questionnaire"], key="gamma_mode")

if gamma_mode == "Manual Entry":
    gamma = sb.slider("Gamma  (−10 = risk-loving · 0 = neutral · +10 = risk-averse)",
                      -10.0, 10.0, 3.0, 0.5)
else:
    sb.caption("Answer all 5 questions honestly.")
    q1 = sb.selectbox("Q1. Attitude toward risk?",
        ["1. Avoid risk", "2. Low-risk steady", "3. Moderate",
         "4. High return focus", "5. High-risk seeker"])
    q2 = sb.selectbox("Q2. Prefer slow but steady growth?",
        ["1. Strongly Agree", "2. Agree", "3. Neutral", "4. Disagree", "5. Strongly Disagree"])
    q3 = sb.selectbox("Q3. Reaction to 20% portfolio drop?",
        ["1. Sell all", "2. Sell some", "3. Do nothing", "4. Stay course", "5. Buy more"])
    q4 = sb.selectbox("Q4. Comfort with high-risk/reward investments?",
        ["1. Very little", "2. < 25%", "3. ~50%", "4. > 50%", "5. All of it"])
    q5 = sb.selectbox("Q5. Prefer small guaranteed over large uncertain?",
        ["1. Strongly Agree", "2. Agree", "3. Neutral", "4. Disagree", "5. Strongly Disagree"])

    avg_score = (int(q1[0]) + int(q2[0]) + int(q3[0]) + int(q4[0]) + int(q5[0])) / 5
    if   avg_score <= 1.5: gamma, label = 8.0,  "Very Cautious"
    elif avg_score <= 2.3: gamma, label = 4.0,  "Cautious"
    elif avg_score <= 3.2: gamma, label = 0.0,  "Moderate / Risk-Neutral"
    elif avg_score <= 4.1: gamma, label = -4.0, "Adventurous"
    else:                  gamma, label = -8.0, "Very Adventurous"
    sb.success(f"Profile: **{label}** · γ = {gamma}")

sb.markdown("---")

# ── ESG Preference ────────────────────────────────────────
sb.markdown("### ESG Preference")
lambda_choice = sb.select_slider(
    "Willingness to sacrifice return for ESG alignment:",
    options=["None", "Small", "Moderate", "Significant"])
l_map     = {"None": 0.0, "Small": 0.25, "Moderate": 0.75, "Significant": 1.0}
lambda_esg = l_map[lambda_choice]
sb.markdown("---")

# ── ESG Scores ────────────────────────────────────────────
sb.markdown("### ESG Scores")
esg_method = sb.radio("How would you like to enter ESG data?",
                      ["Overall ESG Score", "Separate E, S, and G Pillars"])

weights_ok = True
w_e = w_s = w_g = 33

if esg_method == "Separate E, S, and G Pillars":
    sb.markdown("**Pillar Weights (must sum to 100%)**")
    cw1, cw2, cw3 = sb.columns(3)
    w_e = cw1.number_input("E %", 0, 100, 34, key="we")
    w_s = cw2.number_input("S %", 0, 100, 33, key="ws")
    w_g = cw3.number_input("G %", 0, 100, 33, key="wg")
    weights_ok = (w_e + w_s + w_g) == 100
    if not weights_ok:
        sb.warning(f"Weights sum to {w_e+w_s+w_g}% — must equal 100%.")

def get_agency_input(name, agency, key_pref):
    if agency == "MSCI":
        val = sb.selectbox(f"{name} MSCI Rating",
                           ["CCC","B","BB","BBB","A","AA","AAA"], index=3, key=f"{key_pref}_m")
    elif agency == "Refinitiv":
        val = sb.number_input(f"{name} Score (0–5)", 0, 5, 3, key=f"{key_pref}_r")
    else:
        val = sb.number_input(f"{name} Score", value=50.0, key=f"{key_pref}_s")
    return convert_to_100(val, agency)

sb.markdown(f"**{asset1_name}**")
if esg_method == "Overall ESG Score":
    esg1_100 = get_agency_input(asset1_name, agency1, "o1")
else:
    e1 = get_agency_input(f"{asset1_name} E", agency1, "p1e")
    s1 = get_agency_input(f"{asset1_name} S", agency1, "p1s")
    g1 = get_agency_input(f"{asset1_name} G", agency1, "p1g")
    esg1_100 = (w_e/100)*e1 + (w_s/100)*s1 + (w_g/100)*g1
sb.caption(f"Normalised: **{esg1_100:.1f} / 100**")

sb.markdown(f"**{asset2_name}**")
if esg_method == "Overall ESG Score":
    esg2_100 = get_agency_input(asset2_name, agency2, "o2")
else:
    e2 = get_agency_input(f"{asset2_name} E", agency2, "p2e")
    s2 = get_agency_input(f"{asset2_name} S", agency2, "p2s")
    g2 = get_agency_input(f"{asset2_name} G", agency2, "p2g")
    esg2_100 = (w_e/100)*e2 + (w_s/100)*s2 + (w_g/100)*g2
sb.caption(f"Normalised: **{esg2_100:.1f} / 100**")

sb.markdown("---")
run = sb.button("Calculate Portfolio ›", key="run")


# ──────────────────────────────────────────────────────────
# MAIN PAGE HEADER
# ──────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h1>🌱 Ethos Invest Portfolio Analysis Tool</h1>
  <p>Compare investments based on financial performance, risk, and ESG alignment.</p>
</div>
""", unsafe_allow_html=True)

if not run:
    st.markdown("""
    <div class="info-box">
      👈  Fill in your asset details and preferences in the sidebar, then click
      <strong>Calculate Portfolio</strong> to see your results.
    </div>""", unsafe_allow_html=True)
    st.stop()

if not weights_ok:
    st.markdown("""
    <div class="warn-box">
      ⚠️ ESG pillar weights must sum to 100%. Please adjust them in the sidebar.
    </div>""", unsafe_allow_html=True)
    st.stop()


# ──────────────────────────────────────────────────────────
# CALCULATIONS (original logic — unchanged)
# ──────────────────────────────────────────────────────────
esg_threshold = min(esg1_100, esg2_100) + lambda_esg * (max(esg1_100, esg2_100) - min(esg1_100, esg2_100))

weights  = np.linspace(0, 1, 1000)
rets     = portfolio_return(weights, r1, r2)
vols     = portfolio_sd(weights, sd1, sd2, rho)
esgs     = portfolio_esg(weights, esg1_100, esg2_100)
sharpes  = (rets - r_free) / vols

idx_all  = np.argmax(sharpes)
eligible = np.where(esgs >= esg_threshold)[0]

if len(eligible) == 0:
    st.error("No portfolios satisfy the ESG threshold. "
             "Try reducing your ESG preference.")
    st.stop()

idx_esg = eligible[np.argmax(sharpes[eligible])]

w1_all  = weights[idx_all];  w1_esg = weights[idx_esg]
ret_all = rets[idx_all];     ret_esg = rets[idx_esg]
vol_all = vols[idx_all];     vol_esg = vols[idx_esg]
esg_all = esgs[idx_all];     esg_opt = esgs[idx_esg]
sh_all  = sharpes[idx_all];  sh_esg  = sharpes[idx_esg]

d_ret = ret_esg - ret_all
d_sd  = vol_esg - vol_all
d_esg = esg_opt - esg_all

# Minimum variance portfolio
w1_mv = (sd2**2 - rho*sd1*sd2) / (sd1**2 + sd2**2 - 2*rho*sd1*sd2)
w1_mv = float(np.clip(w1_mv, 0, 1))
ret_mv = portfolio_return(w1_mv, r1, r2)
vol_mv = portfolio_sd(w1_mv, sd1, sd2, rho)
esg_mv = portfolio_esg(w1_mv, esg1_100, esg2_100)
sh_mv  = (ret_mv - r_free) / vol_mv if vol_mv > 0 else 0

# ──────────────────────────────────────────────────────────
# SECTION 1 · ESG OPTIMAL PORTFOLIO (FIXED)
# ──────────────────────────────────────────────────────────
st.markdown('<div class="section-label">ESG Optimal Portfolio</div>', unsafe_allow_html=True)

col_alloc, col_ring, col_metrics = st.columns([2.4, 1.2, 2.4])

# ── Allocation Card ───────────────────────────────────────
with col_alloc:
    with st.container():
        st.markdown(f"""
        <div class="card">
            <div style="font-weight:600;margin-bottom:12px;">Asset Allocation</div>
            {alloc_bar_html(w1_esg, 1 - w1_esg, asset1_name, asset2_name)}
        </div>
        """, unsafe_allow_html=True)

# ── ESG Ring ──────────────────────────────────────────────
with col_ring:
    with st.container():
        st.markdown(progress_ring_html(esg_opt, "Portfolio ESG"), unsafe_allow_html=True)

# ── Metrics ───────────────────────────────────────────────
with col_metrics:
    with st.container():
        st.markdown(metric_tile("Expected Return",  f"{ret_esg*100:.2f}%", "Annualised"), unsafe_allow_html=True)
        st.markdown(metric_tile("Risk (Std Dev)",   f"{vol_esg*100:.2f}%", "Annualised"), unsafe_allow_html=True)
        st.markdown(metric_tile("Sharpe Ratio",     f"{sh_esg:.4f}",       "Risk-adjusted return"), unsafe_allow_html=True)

# spacer to prevent collapse
st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────
# SECTION 2 · PORTFOLIO COMPARISON TABLE
# ──────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Portfolio Comparison</div>', unsafe_allow_html=True)

table_rows = [
    (f"{asset1_name} weight",   f"{w1_esg*100:.2f}%",      f"{w1_all*100:.2f}%",      f"{w1_mv*100:.2f}%"),
    (f"{asset2_name} weight",   f"{(1-w1_esg)*100:.2f}%",  f"{(1-w1_all)*100:.2f}%",  f"{(1-w1_mv)*100:.2f}%"),
    ("Expected return",          f"{ret_esg*100:.2f}%",     f"{ret_all*100:.2f}%",     f"{ret_mv*100:.2f}%"),
    ("Risk (Std Dev)",           f"{vol_esg*100:.2f}%",     f"{vol_all*100:.2f}%",     f"{vol_mv*100:.2f}%"),
    ("ESG score (0–100)",        f"{esg_opt:.2f}",          f"{esg_all:.2f}",          f"{esg_mv:.2f}"),
    ("Sharpe ratio",             f"{sh_esg:.4f}",           f"{sh_all:.4f}",           f"{sh_mv:.4f}"),
]

table_html = """
<table class="cmp-table">
  <thead><tr>
    <th>Metric</th>
    <th>✅ ESG-Constrained</th>
    <th>📈 Unconstrained</th>
    <th>🛡️ Min Variance</th>
  </tr></thead>
  <tbody>
"""
for r in table_rows:
    table_html += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>"
table_html += "</tbody></table>"
st.markdown(table_html, unsafe_allow_html=True)

st.markdown('<div class="section-label">Allocation Breakdown</div>', unsafe_allow_html=True)

bar_col1, bar_col2, bar_col3 = st.columns(3)

def alloc_card_html(title, w1, w2, name1, name2):
    c1, c2 = "#52c98a", "#3b82f6"
    p1 = f"{w1*100:.1f}%"
    p2 = f"{w2*100:.1f}%"
    return f"""
    <div class="card">
      <div style="font-size:11px;font-weight:600;letter-spacing:0.12em;
                  text-transform:uppercase;color:#52c98a;margin-bottom:14px;">
        {title}
      </div>
      <div class="bar-row">
        <div class="bar-label-row">
          <span style="color:{c1};">{name1}</span>
          <span style="color:{c1};font-family:'JetBrains Mono',monospace;">{p1}</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" style="width:{p1};background:linear-gradient(90deg,#1f6b42,{c1});"></div>
        </div>
      </div>
      <div class="bar-row" style="margin-top:12px;">
        <div class="bar-label-row">
          <span style="color:{c2};">{name2}</span>
          <span style="color:{c2};font-family:'JetBrains Mono',monospace;">{p2}</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" style="width:{p2};background:linear-gradient(90deg,#1e40af,{c2});"></div>
        </div>
      </div>
    </div>"""

with bar_col1:
    st.markdown(
        alloc_card_html("✅ ESG Constrained", w1_esg, 1-w1_esg, asset1_name, asset2_name),
        unsafe_allow_html=True)

with bar_col2:
    st.markdown(
        alloc_card_html("📈 Unconstrained", w1_all, 1-w1_all, asset1_name, asset2_name),
        unsafe_allow_html=True)

with bar_col3:
    st.markdown(
        alloc_card_html("🛡️ Min Variance", w1_mv, 1-w1_mv, asset1_name, asset2_name),
        unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)
# ──────────────────────────────────────────────────────────
# SECTION 3 · IMPACT OF ESG CONSTRAINT
# ──────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Impact of ESG Constraint</div>', unsafe_allow_html=True)

ic1, ic2, ic3 = st.columns(3)
with ic1:
    st.markdown(f"""
    <div class="card" style="text-align:center;">
      <div class="label" style="text-align:center;margin-bottom:8px;">Return change</div>
      {chip_html(d_ret * 100, " pp")}
      <div style="font-size:11px;color:#9ca3af;margin-top:6px;">vs unconstrained</div>
    </div>""", unsafe_allow_html=True)
with ic2:
    st.markdown(f"""
    <div class="card" style="text-align:center;">
      <div class="label" style="text-align:center;margin-bottom:8px;">Risk change</div>
      {chip_html(d_sd * 100, " pp")}
      <div style="font-size:11px;color:#9ca3af;margin-top:6px;">vs unconstrained</div>
    </div>""", unsafe_allow_html=True)
with ic3:
    st.markdown(f"""
    <div class="card" style="text-align:center;">
      <div class="label" style="text-align:center;margin-bottom:8px;">ESG score gain</div>
      {chip_html(d_esg, " pts", decimals=1)}
      <div style="font-size:11px;color:#9ca3af;margin-top:6px;">vs unconstrained</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if idx_all == idx_esg:
    st.markdown("""
    <div class="info-box">
      The unconstrained optimal portfolio already meets your ESG threshold —
      applying the constraint has no material effect on the allocation.
    </div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="info-box">
      Your ESG preference requires a minimum portfolio score of <strong>{esg_threshold:.2f}</strong>.
      The portfolio was adjusted to meet this, shifting weight towards the higher-rated asset.
      The chips above show the cost (return / risk) and benefit (ESG score) of that tilt.
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────
# SECTION 4 · CHARTS (original chart logic — restyled)
# ──────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Charts</div>', unsafe_allow_html=True)

plt.rcParams.update({
    "font.family":       "sans-serif",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "grid.alpha":        0.25,
    "grid.linestyle":    "--",
})

# Frontier data (wide range for display)
w_plot  = np.linspace(-0.5, 1.5, 500)
r_plot  = portfolio_return(w_plot, r1, r2)
v_plot  = portfolio_sd(w_plot, sd1, sd2, rho)

sd_max   = max(v_plot) * 1.05
sd_range = np.linspace(0, sd_max, 300)
cml_all  = r_free + ((ret_all - r_free) / vol_all) * sd_range
cml_esg  = r_free + ((ret_esg - r_free) / vol_esg) * sd_range

chart_col1, chart_col2 = st.columns(2)

# Chart 1: Efficient Frontier & CML
with chart_col1:
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    fig1.patch.set_facecolor("#f7faf7")
    ax1.set_facecolor("#f7faf7")

    ax1.plot(v_plot, r_plot, color="#94a3b8", lw=1.5, alpha=0.5, label="Full frontier")
    ax1.plot(sd_range, cml_all, "--", color="#94a3b8", lw=1.5, label="CML (unconstrained)")
    ax1.plot(sd_range, cml_esg, "--", color="#16a34a", lw=1.5, label="CML (ESG)")
    ax1.scatter(0,       r_free,  marker="s", s=80,  color="#0d1f0f",
                zorder=5, label="Risk-free asset")
    ax1.scatter(vol_all, ret_all, marker="*", s=220, color="#64748b",
                edgecolors="white", linewidths=0.8, zorder=6, label="Optimal (unconstrained)")
    ax1.scatter(vol_esg, ret_esg, marker="*", s=220, color="#16a34a",
                edgecolors="white", linewidths=0.8, zorder=7, label="Optimal (ESG)")

    ax1.annotate("Unconstrained", (vol_all, ret_all),
                 xytext=(-6, -16), textcoords="offset points", fontsize=8, color="#64748b")
    ax1.annotate("ESG optimal",   (vol_esg, ret_esg),
                 xytext=(8, 6),   textcoords="offset points", fontsize=8, color="#16a34a")

    ax1.set_xlim(0, max(v_plot) * 1.02)
    ax1.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax1.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax1.set_xlabel("Risk (Standard Deviation)", fontsize=11)
    ax1.set_ylabel("Expected Return",           fontsize=11)
    ax1.set_title("Efficient Frontier & Capital Market Lines",
                  fontsize=13, fontweight="bold", color="#0d1f0f")
    ax1.legend(fontsize=7.5)
    plt.tight_layout()
    st.pyplot(fig1)
    st.caption("Stars mark the tangency (highest Sharpe) portfolio for each case.")

# Chart 2: ESG–Sharpe Trade-off
with chart_col2:
    fig2, ax2 = plt.subplots(figsize=(6, 5))
    fig2.patch.set_facecolor("#f7faf7")
    ax2.set_facecolor("#f7faf7")

    ax2.plot(esgs, sharpes, color="#ef4444", lw=2.5, label="ESG–Sharpe frontier")
    ax2.axvline(esg_threshold, color="#f59e0b", lw=1.5, linestyle=":",
                label=f"ESG threshold ({esg_threshold:.1f})")
    ax2.scatter(esg_all, sh_all, marker="*", s=220, color="#64748b",
                edgecolors="white", linewidths=0.8, zorder=5, label="Optimal (unconstrained)")
    ax2.scatter(esg_opt, sh_esg, marker="*", s=220, color="#16a34a",
                edgecolors="white", linewidths=0.8, zorder=6, label="Optimal (ESG)")

    ax2.annotate("Unconstrained", (esg_all, sh_all),
                 xytext=(-6, -16), textcoords="offset points", fontsize=8, color="#64748b")
    ax2.annotate("ESG optimal",   (esg_opt, sh_esg),
                 xytext=(8, 6),   textcoords="offset points", fontsize=8, color="#16a34a")

    ax2.set_xlabel("Portfolio ESG Score (0–100)", fontsize=11)
    ax2.set_ylabel("Sharpe Ratio",                fontsize=11)
    ax2.set_title("ESG–Sharpe Ratio Trade-off",
                  fontsize=13, fontweight="bold", color="#0d1f0f")
    ax2.legend(fontsize=7.5)
    plt.tight_layout()
    st.pyplot(fig2)
    st.caption("Amber dotted line marks your minimum ESG threshold.")


# ──────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;font-size:12px;color:#94a3b8;padding:16px 0;">
  Ethos Invest · Sustainable Finance Portfolio Tool ·
  For illustrative purposes only — not financial advice.
</div>
""", unsafe_allow_html=True)
