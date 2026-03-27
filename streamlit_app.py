import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

# ──────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ethos-Invest · Sustainable Portfolio",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────
# GLOBAL CSS
# ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:wght@500;600&display=swap');

html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif;
    background-color: #f4f7f5;
    color: #1c2b22;
}

[data-testid="stSidebar"] {
    background: #0f2a1d;
    border-right: 1px solid #1f3d2b;
}
[data-testid="stSidebar"] * { color: #dbece0 !important; }
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #6fcf97 !important;
    font-size: 12px !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #163825 !important;
    border: 1px solid #2d5a3f !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #2f7d57, #4caf7a) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    color: white !important;
    width: 100%;
    padding: 0.6rem;
    border: none;
}

.page-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 42px;
    color: #10281c;
    margin-bottom: 4px;
}
.page-header p { color: #5f7d6c; margin-top: 0; }

.section-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.14em;
    color: #3f8f63;
    text-transform: uppercase;
    margin-top: 30px;
    margin-bottom: 10px;
}

.card {
    background: #ffffff;
    border: 1px solid #e2ece6;
    border-radius: 16px;
    padding: 22px;
    box-shadow: 0 6px 18px rgba(16,40,28,0.04);
    margin-bottom: 12px;
    color: #1c2b22; /* Ensure dark text for card content */
}

/* FIX: Specific targeting for labels within cards */
.card .label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: #6b8f7b !important; /* Forces a grey-green visible color */
    margin-bottom: 8px;
    display: block;
}

.metric-tile {
    background: #ffffff;
    border: 1px solid #e6efe9;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 10px;
}
.metric-tile .label { font-size: 11px; color: #6b8f7b; margin-bottom: 4px; }
.metric-tile .value { font-size: 28px; font-weight: 600; color: #10281c; }
.metric-tile .sub   { font-size: 11px; color: #9cb8a8; margin-top: 2px; }

.bar-row { margin-bottom: 4px; }
.bar-label-row {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    font-weight: 500;
    margin-bottom: 4px;
}
.bar-track {
    height: 18px;
    background: #edf4ef;
    border-radius: 100px;
    overflow: hidden;
}
.bar-fill { height: 18px; border-radius: 100px; }

.cmp-table { 
    width: 100%; 
    border-collapse: collapse; 
    font-size: 13px; 
    background: #0b1a12;
}

.cmp-table th {
    background: linear-gradient(90deg, #0f2a1d, #123524);
    color: #b7d7c4;
    padding: 10px 14px;
    text-align: left;
    font-weight: 500;
    border-bottom: 1px solid #1f3d2b;
}

.cmp-table td { 
    padding: 10px 14px; 
    border-bottom: 1px solid #13271c;
    color: #dbece0;
}

.cmp-table tr:hover td {
    background: rgba(111, 207, 151, 0.06);
}

.chip {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.02em;
}

.chip-pos { 
    background: rgba(34,197,94,0.12);
    color: #16a34a !important;
}

.chip-neg { 
    background: rgba(239,68,68,0.12);
    color: #dc2626 !important;
}

.chip-neu { 
    background: rgba(148,163,184,0.12);
    color: #475569 !important;
}

hr.fancy-divider {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, #2f7d57, #7cc9a6, transparent);
    margin: 28px 0;
}

.info-box {
    background: #edf7f1;
    border-left: 4px solid #3f8f63;
    padding: 14px 18px;
    border-radius: 0 10px 10px 0;
    color: #1c4a30;
    font-size: 14px;
    margin: 10px 0;
}
.warn-box {
    background: #fff6e5;
    border-left: 4px solid #e6a700;
    padding: 14px 18px;
    border-radius: 0 10px 10px 0;
    color: #5a3e00;
    font-size: 14px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────
# CORE LOGIC
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
               color:#7ec984;letter-spacing:0.02em;">🌿 EcoVest</span><br>
  <span style="font-size:11px;color:#4a6b4e;letter-spacing:0.1em;
               text-transform:uppercase;">Sustainable Portfolio Tool</span>
</div>
""", unsafe_allow_html=True)
sb.markdown("---")

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

# Risk Preference
sb.markdown("### Risk Preference")
gamma_mode = sb.radio("Determine your Risk Aversion (γ):",
                      ["Manual Entry", "Questionnaire"], key="gamma_mode")

if gamma_mode == "Manual Entry":
    gamma = sb.slider("Gamma", -10.0, 10.0, 3.0, 0.5)
else:
    q1 = sb.selectbox("Q1. Attitude toward risk?", ["1. Avoid risk", "2. Low-risk steady", "3. Moderate", "4. High return focus", "5. High-risk seeker"])
    q2 = sb.selectbox("Q2. Prefer slow but steady growth?", ["1. Strongly Agree", "2. Agree", "3. Neutral", "4. Disagree", "5. Strongly Disagree"])
    q3 = sb.selectbox("Q3. Reaction to 20% portfolio drop?", ["1. Sell all", "2. Sell some", "3. Do nothing", "4. Stay course", "5. Buy more"])
    q4 = sb.selectbox("Q4. Comfort with high-risk/reward investments?", ["1. Very little", "2. < 25%", "3. ~50%", "4. > 50%", "5. All of it"])
    q5 = sb.selectbox("Q5. Prefer small guaranteed over large uncertain?", ["1. Strongly Agree", "2. Agree", "3. Neutral", "4. Disagree", "5. Strongly Disagree"])
    avg_score = (int(q1[0]) + int(q2[0]) + int(q3[0]) + int(q4[0]) + int(q5[0])) / 5
    if avg_score <= 1.5: gamma, label = 8.0, "Very Cautious"
    elif avg_score <= 2.3: gamma, label = 4.0, "Cautious"
    elif avg_score <= 3.2: gamma, label = 0.0, "Moderate"
    elif avg_score <= 4.1: gamma, label = -4.0, "Adventurous"
    else: gamma, label = -8.0, "Very Adventurous"
    sb.success(f"Profile: **{label}**")

sb.markdown("---")
sb.markdown("### ESG Preference")
lambda_choice = sb.select_slider("Willingness to sacrifice return:", options=["None", "Small", "Moderate", "Significant"])
l_map = {"None": 0.0, "Small": 0.25, "Moderate": 0.75, "Significant": 1.0}
lambda_esg = l_map[lambda_choice]

sb.markdown("---")
sb.markdown("### ESG Scores")
esg_method = sb.radio("Entry Method", ["Overall ESG Score", "Separate E, S, and G Pillars"])

weights_ok = True
w_e = w_s = w_g = 33

if esg_method == "Separate E, S, and G Pillars":
    cw1, cw2, cw3 = sb.columns(3)
    w_e = cw1.number_input("E %", 0, 100, 34)
    w_s = cw2.number_input("S %", 0, 100, 33)
    w_g = cw3.number_input("G %", 0, 100, 33)
    weights_ok = (w_e + w_s + w_g) == 100

def get_agency_input(name, agency, key_pref):
    if agency == "MSCI":
        val = sb.selectbox(f"{name} Rating", ["CCC","B","BB","BBB","A","AA","AAA"], index=3, key=f"{key_pref}_m")
    elif agency == "Refinitiv":
        val = sb.number_input(f"{name} (0–5)", 0, 5, 3, key=f"{key_pref}_r")
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

sb.markdown(f"**{asset2_name}**")
if esg_method == "Overall ESG Score":
    esg2_100 = get_agency_input(asset2_name, agency2, "o2")
else:
    e2 = get_agency_input(f"{asset2_name} E", agency2, "p2e")
    s2 = get_agency_input(f"{asset2_name} S", agency2, "p2s")
    g2 = get_agency_input(f"{asset2_name} G", agency2, "p2g")
    esg2_100 = (w_e/100)*e2 + (w_s/100)*s2 + (w_g/100)*g2

sb.markdown("---")
run = sb.button("Calculate Portfolio ›")


# ──────────────────────────────────────────────────────────
# MAIN PAGE
# ──────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h1>🌱 Sustainable Finance<br>Portfolio Tool</h1>
  <p>Compare investments based on financial performance, risk, and ESG alignment.</p>
</div>
""", unsafe_allow_html=True)

if not run:
    st.markdown('<div class="info-box">👈 Fill in your details and click <strong>Calculate Portfolio</strong>.</div>', unsafe_allow_html=True)
    st.stop()

if not weights_ok:
    st.error("Weights must sum to 100%")
    st.stop()

# Calculations
esg_threshold = min(esg1_100, esg2_100) + lambda_esg * (max(esg1_100, esg2_100) - min(esg1_100, esg2_100))
weights  = np.linspace(0, 1, 1000)
rets     = portfolio_return(weights, r1, r2)
vols     = portfolio_sd(weights, sd1, sd2, rho)
esgs     = portfolio_esg(weights, esg1_100, esg2_100)
sharpes  = (rets - r_free) / vols

idx_all  = np.argmax(sharpes)
eligible = np.where(esgs >= esg_threshold)[0]

if len(eligible) == 0:
    st.error("No portfolios satisfy the ESG threshold.")
    st.stop()

idx_esg = eligible[np.argmax(sharpes[eligible])]

w1_esg = weights[idx_esg]; ret_esg = rets[idx_esg]; vol_esg = vols[idx_esg]; esg_opt = esgs[idx_esg]; sh_esg = sharpes[idx_esg]
w1_all = weights[idx_all]; ret_all = rets[idx_all]; vol_all = vols[idx_all]; esg_all = esgs[idx_all]; sh_all = sharpes[idx_all]

d_ret, d_sd, d_esg = ret_esg - ret_all, vol_esg - vol_all, esg_opt - esg_all

# SECTION 1
st.markdown('<div class="section-label">ESG Optimal Portfolio</div>', unsafe_allow_html=True)
c_alloc, c_ring, c_metrics = st.columns([2.4, 1.2, 2.4])
with c_alloc:
    st.markdown(f'<div class="card"><span class="label">Asset Allocation</span>{alloc_bar_html(w1_esg, 1-w1_esg, asset1_name, asset2_name)}</div>', unsafe_allow_html=True)
with c_ring:
    st.markdown(progress_ring_html(esg_opt, "Portfolio ESG"), unsafe_allow_html=True)
with c_metrics:
    st.markdown(metric_tile("Expected Return", f"{ret_esg*100:.2f}%", "Annualised"), unsafe_allow_html=True)
    st.markdown(metric_tile("Risk (Std Dev)", f"{vol_esg*100:.2f}%", "Annualised"), unsafe_allow_html=True)
    st.markdown(metric_tile("Sharpe Ratio", f"{sh_esg:.4f}", "Risk-adjusted"), unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# SECTION 2
st.markdown('<div class="section-label">Portfolio Comparison</div>', unsafe_allow_html=True)
st.markdown(f"""
<table class="cmp-table">
  <thead><tr><th>Metric</th><th>✅ ESG-Constrained</th><th>📈 Unconstrained</th></tr></thead>
  <tbody>
    <tr><td>Expected return</td><td>{ret_esg*100:.2f}%</td><td>{ret_all*100:.2f}%</td></tr>
    <tr><td>Risk (Std Dev)</td><td>{vol_esg*100:.2f}%</td><td>{vol_all*100:.2f}%</td></tr>
    <tr><td>ESG score</td><td>{esg_opt:.2f}</td><td>{esg_all:.2f}</td></tr>
    <tr><td>Sharpe ratio</td><td>{sh_esg:.4f}</td><td>{sh_all:.4f}</td></tr>
  </tbody>
</table>""", unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# SECTION 3 - THE FIXED LABELS
st.markdown('<div class="section-label">Impact of ESG Constraint</div>', unsafe_allow_html=True)
ic1, ic2, ic3 = st.columns(3)
with ic1:
    st.markdown(f'<div class="card" style="text-align:center;"><span class="label">Return change</span>{chip_html(d_ret*100, " pp")}<div style="font-size:11px;color:#9ca3af;margin-top:6px;">vs unconstrained</div></div>', unsafe_allow_html=True)
with ic2:
    st.markdown(f'<div class="card" style="text-align:center;"><span class="label">Risk change</span>{chip_html(d_sd*100, " pp")}<div style="font-size:11px;color:#9ca3af;margin-top:6px;">vs unconstrained</div></div>', unsafe_allow_html=True)
with ic3:
    st.markdown(f'<div class="card" style="text-align:center;"><span class="label">ESG score gain</span>{chip_html(d_esg, " pts", decimals=1)}<div style="font-size:11px;color:#9ca3af;margin-top:6px;">vs unconstrained</div></div>', unsafe_allow_html=True)

# Charts Section
st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Visual Analysis</div>', unsafe_allow_html=True)

plt.rcParams.update({"axes.grid": True, "grid.alpha": 0.2})
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig.patch.set_facecolor("#f4f7f5")

# Frontier
w_plot = np.linspace(-0.2, 1.2, 100)
ax1.plot(portfolio_sd(w_plot, sd1, sd2, rho), portfolio_return(w_plot, r1, r2), color="#94a3b8", ls="--")
ax1.scatter(vol_all, ret_all, color="#64748b", s=100, label="Unconstrained")
ax1.scatter(vol_esg, ret_esg, color="#16a34a", s=100, label="ESG Optimal")
ax1.set_title("Efficient Frontier")
ax1.legend()

# Trade-off
ax2.plot(esgs, sharpes, color="#ef4444")
ax2.axvline(esg_threshold, color="#f59e0b", ls=":")
ax2.set_title("Sharpe Ratio vs ESG Score")

st.pyplot(fig)

st.markdown('<div style="text-align:center;font-size:12px;color:#94a3b8;padding:20px;">EcoVest · Not Financial Advice</div>', unsafe_allow_html=True)
