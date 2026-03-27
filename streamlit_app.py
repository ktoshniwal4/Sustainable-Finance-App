import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="Sustainable Finance Tool", layout="wide")

# ─────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
body {
    background-color: #f4f7f5;
    font-family: 'Inter', sans-serif;
}

h1, h2, h3 {
    color: #10281c;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #e6efe9;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    margin-bottom: 20px;
}

.metric {
    font-size: 26px;
    font-weight: 600;
}

.label {
    font-size: 12px;
    color: #6b8f7b;
}

.section {
    margin-top: 30px;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CORE FUNCTIONS (UNCHANGED)
# ─────────────────────────────────────────────
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
            msci_map = {"ccc": 0.0, "b": 16.7, "bb": 33.4, "bbb": 50.1, "a": 66.8, "aa": 83.5, "aaa": 100.0}
            return msci_map.get(str(score).strip().lower(), 0.0)
        elif agency == "refinitiv":
            r_map = {0: 0.0, 1: 10.0, 2: 25.0, 3: 50.0, 4: 75.0, 5: 95.0}
            return r_map.get(int(float(score)), 0.0)
        elif agency == "s&p":
            return max(0.0, min(100.0, float(score)))
    except:
        return 0.0
    return 0.0

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("🌱 Sustainable Finance Portfolio Tool")
st.caption("Balance return, risk, and ESG preferences in one interactive model")

# ─────────────────────────────────────────────
# SIDEBAR INPUTS
# ─────────────────────────────────────────────
st.sidebar.header("📊 Inputs")

asset1_name = st.sidebar.text_input("Asset 1", "Apple")
asset2_name = st.sidebar.text_input("Asset 2", "Microsoft")

col_r1, col_r2 = st.sidebar.columns(2)

with col_r1:
    r1 = st.number_input(f"{asset1_name} Return %", value=8.0) / 100
    sd1 = st.number_input(f"{asset1_name} Vol %", value=15.0) / 100
    agency1 = st.selectbox("Agency 1", ["S&P", "MSCI", "Sustainalytics", "Refinitiv"])

with col_r2:
    r2 = st.number_input(f"{asset2_name} Return %", value=10.0) / 100
    sd2 = st.number_input(f"{asset2_name} Vol %", value=20.0) / 100
    agency2 = st.selectbox("Agency 2", ["S&P", "MSCI", "Sustainalytics", "Refinitiv"])

rho = st.sidebar.slider("Correlation", -1.0, 1.0, 0.2)
r_free = st.sidebar.number_input("Risk-free %", value=2.0) / 100

# ─────────────────────────────────────────────
# RISK SECTION
# ─────────────────────────────────────────────
st.markdown("## 1. Risk Preference")

gamma = st.slider("Risk Aversion (γ)", -10.0, 10.0, 3.0)

# ─────────────────────────────────────────────
# ESG INPUT
# ─────────────────────────────────────────────
st.markdown("## 2. ESG Scores")

col1, col2 = st.columns(2)

with col1:
    esg1_100 = convert_to_100(
        st.number_input(f"{asset1_name} ESG", value=50.0),
        agency1
    )

with col2:
    esg2_100 = convert_to_100(
        st.number_input(f"{asset2_name} ESG", value=50.0),
        agency2
    )

# ─────────────────────────────────────────────
# ESG PREFERENCE
# ─────────────────────────────────────────────
st.markdown("## 3. ESG Preference")

lambda_choice = st.select_slider(
    "Importance of ESG",
    options=["None", "Small", "Moderate", "Significant"]
)

l_map = {"None": 0.0, "Small": 0.25, "Moderate": 0.75, "Significant": 1.0}
lambda_esg = l_map[lambda_choice]

esg_threshold = min(esg1_100, esg2_100) + lambda_esg * (max(esg1_100, esg2_100) - min(esg1_100, esg2_100))

# ─────────────────────────────────────────────
# CALCULATIONS (UNCHANGED)
# ─────────────────────────────────────────────
weights = np.linspace(0, 1, 1000)
rets = portfolio_return(weights, r1, r2)
vols = portfolio_sd(weights, sd1, sd2, rho)
esgs = portfolio_esg(weights, esg1_100, esg2_100)
sharpes = (rets - r_free) / vols

idx_all = np.argmax(sharpes)
eligible = np.where(esgs >= esg_threshold)[0]

# ─────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────
st.markdown("## 4. Results")

if len(eligible) == 0:
    st.error("No portfolios meet ESG requirement")
else:
    idx_esg = eligible[np.argmax(sharpes[eligible])]

    colA, colB, colC = st.columns(3)

    with colA:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="label">Expected Return</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric">{rets[idx_esg]*100:.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with colB:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="label">Risk (SD)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric">{vols[idx_esg]*100:.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with colC:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="label">ESG Score</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric">{esgs[idx_esg]:.2f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # TABLE
    st.markdown("### Portfolio Comparison")

    df = pd.DataFrame({
        "Metric": ["Return", "Risk", "ESG", "Sharpe"],
        "No ESG": [rets[idx_all], vols[idx_all], esgs[idx_all], sharpes[idx_all]],
        "With ESG": [rets[idx_esg], vols[idx_esg], esgs[idx_esg], sharpes[idx_esg]]
    })

    st.dataframe(df)

    # ───────────── PLOTS ─────────────
    st.markdown("### Charts")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.plot(vols, rets)
    ax1.scatter(vols[idx_all], rets[idx_all])
    ax1.scatter(vols[idx_esg], rets[idx_esg])
    ax1.set_title("Efficient Frontier")

    ax2.plot(esgs, sharpes)
    ax2.axvline(esg_threshold)
    ax2.set_title("ESG vs Sharpe")

    st.pyplot(fig)

    st.info(f"ESG threshold = {esg_threshold:.2f}")
