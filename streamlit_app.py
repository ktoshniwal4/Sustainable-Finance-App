import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

# --- INITIALIZATION ---
if 'step' not in st.session_state:
    st.session_state.step = "setup"
if 'gamma' not in st.session_state:
    st.session_state.gamma = None
if 'q_scores' not in st.session_state:
    st.session_state.q_scores = []

# --- CORE LOGIC FUNCTIONS ---
def portfolio_return(w1, r1, r2):
    return w1 * r1 + (1 - w1) * r2

def portfolio_sd(w1, sd1, sd2, rho):
    return np.sqrt(w1**2 * sd1**2 + (1-w1)**2 * sd2**2 + 2*rho*w1*(1-w1)*sd1*sd2)

def portfolio_esg(w1, esg1, esg2):
    return w1 * esg1 + (1 - w1) * esg2

def convert_to_100(score, agency):
    agency = agency.lower()
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
    return 0.0

# --- APP INTERFACE ---
st.title("🌱 Sustainable Finance Portfolio Tool")

# --- SIDEBAR: ASSET & MARKET DATA ---
st.sidebar.header("Asset Information")
asset1_name = st.sidebar.text_input("Asset 1 Name", "Asset A")
asset2_name = st.sidebar.text_input("Asset 2 Name", "Asset B")

col1, col2 = st.sidebar.columns(2)
with col1:
    r1 = st.number_input(f"{asset1_name} Return %", value=8.0) / 100
    sd1 = st.number_input(f"{asset1_name} Vol %", value=15.0) / 100
    agency1 = st.selectbox(f"{asset1_name} Agency", ["MSCI", "Sustainalytics", "Refinitiv", "S&P"])
with col2:
    r2 = st.number_input(f"{asset2_name} Return %", value=10.0) / 100
    sd2 = st.number_input(f"{asset2_name} Vol %", value=20.0) / 100
    agency2 = st.selectbox(f"{asset2_name} Agency", ["MSCI", "Sustainalytics", "Refinitiv", "S&P"])

st.sidebar.divider()
rho = st.sidebar.slider("Correlation (rho)", -1.0, 1.0, 0.2)
r_free = st.sidebar.number_input("Risk-free Rate %", value=2.0) / 100

# --- STEP 1: RISK AVERSION (GAMMA) ---
st.header("1. Risk Preference")
gamma_mode = st.radio("Do you know your Gamma?", ["Yes, I'll enter it", "No, help me decide (Questionnaire)"])

if gamma_mode == "Yes, I'll enter it":
    st.session_state.gamma = st.slider("Gamma Value (-10 to 10)", -10.0, 10.0, 3.0)
else:
    st.info("Please answer the following to determine your risk profile:")
    q1 = st.selectbox("Q1. General attitude toward risk?", ["1. Avoid risk", "2. Low-risk steady", "3. Moderate", "4. High return focus", "5. High-risk seeker"])
    q2 = st.selectbox("Q2. Preference for slow/steady growth?", ["1. Strongly Agree", "2. Agree", "3. Neutral", "4. Disagree", "5. Strongly Disagree"])
    q3 = st.selectbox("Q3. Reaction to 20% drop?", ["1. Sell all", "2. Sell some", "3. Wait", "4. Stay course", "5. Buy more"])
    
    avg_score = (int(q1[0]) + int(q2[0]) + int(q3[0])) / 3
    if avg_score <= 1.5: st.session_state.gamma = 8.0
    elif avg_score <= 2.3: st.session_state.gamma = 4.0
    elif avg_score <= 3.2: st.session_state.gamma = 0.0
    elif avg_score <= 4.1: st.session_state.gamma = -4.0
    else: st.session_state.gamma = -8.0
    st.success(f"Calculated Gamma: {st.session_state.gamma}")

# --- STEP 2: ESG INPUTS ---
st.header("2. ESG Scores")
esg_method = st.radio("Input Method", ["Overall Score", "Separate E, S, G Pillars"])

def get_esg_val(name, agency, key_pref):
    if agency == "MSCI":
        val = st.selectbox(f"{name} MSCI Rating", ["CCC", "B", "BB", "BBB", "A", "AA", "AAA"], index=3, key=f"{key_pref}_m")
    elif agency == "Refinitiv":
        val = st.number_input(f"{name} Score (0-5)", 0, 5, 3, key=f"{key_pref}_r")
    else:
        val = st.number_input(f"{name} Score", value=50.0, key=f"{key_pref}_s")
    return convert_to_100(val, agency)

col_a, col_b = st.columns(2)
with col_a:
    esg1_100 = get_esg_val(asset1_name, agency1, "a1")
with col_b:
    esg2_100 = get_esg_val(asset2_name, agency2, "a2")

# --- STEP 3: ESG PREFERENCE ---
st.header("3. ESG Preference")
lambda_choice = st.select_slider("Willingness to sacrifice return for ESG:", 
                                 options=["None", "Small", "Moderate", "Significant"])
l_map = {"None": 0.0, "Small": 0.25, "Moderate": 0.75, "Significant": 1.0}
lambda_esg = l_map[lambda_choice]
esg_threshold = min(esg1_100, esg2_100) + lambda_esg * (max(esg1_100, esg2_100) - min(esg1_100, esg2_100))

# --- CALCULATIONS ---
weights = np.linspace(0, 1, 1000)
rets = portfolio_return(weights, r1, r2)
vols = portfolio_sd(weights, sd1, sd2, rho)
esgs = portfolio_esg(weights, esg1_100, esg2_100)
sharpes = (rets - r_free) / vols

# Optimal Indices
idx_all = np.argmax(sharpes)
eligible = np.where(esgs >= esg_threshold)[0]

if len(eligible) == 0:
    st.error("No portfolios meet the ESG threshold!")
else:
    idx_esg = eligible[np.argmax(sharpes[eligible])]

    # --- RESULTS TABLES ---
    st.header("4. Results")
    res_df = pd.DataFrame({
        "Metric": ["Asset 1 Weight", "Asset 2 Weight", "Return", "Risk", "ESG Score", "Sharpe"],
        "Unconstrained": [f"{weights[idx_all]*100:.2f}%", f"{(1-weights[idx_all])*100:.2f}%", f"{rets[idx_all]*100:.2f}%", f"{vols[idx_all]*100:.2f}%", f"{esgs[idx_all]:.2f}", f"{sharpes[idx_all]:.4f}"],
        "ESG Constrained": [f"{weights[idx_esg]*100:.2f}%", f"{(1-weights[idx_esg])*100:.2f}%", f"{rets[idx_esg]*100:.2f}%", f"{vols[idx_esg]*100:.2f}%", f"{esgs[idx_esg]:.2f}", f"{sharpes[idx_esg]:.4f}"]
    })
    st.table(res_df)

    # --- PLOTS ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Frontier
    ax1.plot(vols, rets, color="gray", alpha=0.3)
    ax1.plot(vols[eligible], rets[eligible], color="green", label="ESG Eligible")
    ax1.scatter(vols[idx_all], rets[idx_all], marker="*", s=200, color="blue", label="Optimal")
    ax1.scatter(vols[idx_esg], rets[idx_esg], marker="*", s=200, color="green", label="Optimal (ESG)")
    ax1.set_title("Efficient Frontier")
    ax1.legend()

    # ESG-Sharpe
    ax2.plot(esgs, sharpes, color="red")
    ax2.axvline(esg_threshold, color="black", linestyle="--")
    ax2.set_title("ESG-Sharpe Tradeoff")
    
    st.pyplot(fig)
