import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

# --- CONFIGURATION ---
st.set_page_config(page_title="Sustainable Finance Portfolio Tool", layout="wide")

# --- CORE LOGIC FUNCTIONS ---
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

# --- APP INTERFACE ---
st.title("🌱 Sustainable Finance Portfolio Tool")
st.markdown("Compare investments based on financial performance, risk, and ESG alignment.")

# --- SIDEBAR: ASSET & MARKET DATA ---
st.sidebar.header("Asset & Market Information")
asset1_name = st.sidebar.text_input("Asset 1 Name", "Apple")
asset2_name = st.sidebar.text_input("Asset 2 Name", "Microsoft")

col_r1, col_r2 = st.sidebar.columns(2)
with col_r1:
    r1 = st.number_input(f"{asset1_name} Return %", value=8.0) / 100
    sd1 = st.number_input(f"{asset1_name} Vol %", value=15.0) / 100
    agency1 = st.selectbox(f"{asset1_name} Agency", ["S&P", "MSCI", "Sustainalytics", "Refinitiv"])
with col_r2:
    r2 = st.number_input(f"{asset2_name} Return %", value=10.0) / 100
    sd2 = st.number_input(f"{asset2_name} Vol %", value=20.0) / 100
    agency2 = st.selectbox(f"{asset2_name} Agency", ["S&P", "MSCI", "Sustainalytics", "Refinitiv"])

rho = st.sidebar.slider("Correlation Coefficient (ρ)", -1.0, 1.0, 0.2)
r_free = st.sidebar.number_input("Risk-free Rate %", value=2.0) / 100

# --- STEP 1: RISK AVERSION (GAMMA) ---
st.header("1. Risk Preference")
gamma_mode = st.radio("Determine your Risk Aversion (Gamma):", ["Manual Entry", "Questionnaire"])

if gamma_mode == "Manual Entry":
    gamma = st.slider("Gamma Value (-10 = Risk Loving, 0 = Neutral, 10 = Averse)", -10.0, 10.0, 3.0)
else:
    with st.expander("Risk Assessment Questionnaire", expanded=True):
        q1 = st.selectbox("Q1. Attitude toward risk?", ["1. Avoid risk", "2. Low-risk steady", "3. Moderate", "4. High return focus", "5. High-risk seeker"])
        q2 = st.selectbox("Q2. Prefer slow but steady growth?", ["1. Strongly Agree", "2. Agree", "3. Neutral", "4. Disagree", "5. Strongly Disagree"])
        q3 = st.selectbox("Q3. Reaction to 20% portfolio drop?", ["1. Sell all", "2. Sell some", "3. Do nothing", "4. Stay course", "5. Buy more"])
        q4 = st.selectbox("Q4. Comfort with high-risk/reward investments?", ["1. Very little", "2. < 25%", "3. ~50%", "4. > 50%", "5. All of it"])
        q5 = st.selectbox("Q5. Prefer small guaranteed over large uncertain?", ["1. Strongly Agree", "2. Agree", "3. Neutral", "4. Disagree", "5. Strongly Disagree"])
        
        avg_score = (int(q1[0]) + int(q2[0]) + int(q3[0]) + int(q4[0]) + int(q5[0])) / 5
        if avg_score <= 1.5: gamma, label = 8.0, "Very Cautious"
        elif avg_score <= 2.3: gamma, label = 4.0, "Cautious"
        elif avg_score <= 3.2: gamma, label = 0.0, "Moderate / Risk-Neutral"
        elif avg_score <= 4.1: gamma, label = -4.0, "Adventurous"
        else: gamma, label = -8.0, "Very Adventurous"
        st.success(f"Calculated Profile: {label} (Gamma: {gamma})")

# --- STEP 2: ESG INPUTS ---
st.header("2. ESG Scores")
esg_method = st.radio("How would you like to enter ESG data?", ["Overall ESG Score", "Separate E, S, and G Pillars"])

def get_agency_input(name, agency, key_pref):
    if agency == "MSCI":
        val = st.selectbox(f"{name} MSCI Rating", ["CCC", "B", "BB", "BBB", "A", "AA", "AAA"], index=3, key=f"{key_pref}_m")
    elif agency == "Refinitiv":
        val = st.number_input(f"{name} Score (0-5)", 0, 5, 3, key=f"{key_pref}_r")
    else:
        val = st.number_input(f"{name} Score", value=50.0, key=f"{key_pref}_s")
    return convert_to_100(val, agency)

if esg_method == "Overall ESG Score":
    col_e1, col_e2 = st.columns(2)
    with col_e1: esg1_100 = get_agency_input(asset1_name, agency1, "o1")
    with col_e2: esg2_100 = get_agency_input(asset2_name, agency2, "o2")
else:
    st.subheader("Pillar Weights (%)")
    cw1, cw2, cw3 = st.columns(3)
    w_e = cw1.number_input("Environmental Weight", 0, 100, 34)
    w_s = cw2.number_input("Social Weight", 0, 100, 33)
    w_g = cw3.number_input("Governance Weight", 0, 100, 33)
    
    if (w_e + w_s + w_g) != 100:
        st.warning("⚠️ Weights must sum to 100%!")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown(f"**{asset1_name} Pillars**")
        e1 = get_agency_input(f"{asset1_name} E", agency1, "p1e")
        s1 = get_agency_input(f"{asset1_name} S", agency1, "p1s")
        g1 = get_agency_input(f"{asset1_name} G", agency1, "p1g")
        esg1_100 = (w_e/100)*e1 + (w_s/100)*s1 + (w_g/100)*g1
    with col_p2:
        st.markdown(f"**{asset2_name} Pillars**")
        e2 = get_agency_input(f"{asset2_name} E", agency2, "p2e")
        s2 = get_agency_input(f"{asset2_name} S", agency2, "p2s")
        g2 = get_agency_input(f"{asset2_name} G", agency2, "p2g")
        esg2_100 = (w_e/100)*e2 + (w_s/100)*s2 + (w_g/100)*g2

# --- STEP 3: ESG PREFERENCE ---
st.header("3. ESG Preference")
lambda_choice = st.select_slider("Willingness to sacrifice return for ESG alignment:", 
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
    st.error("No portfolios satisfy the ESG threshold.")
else:
    idx_esg = eligible[np.argmax(sharpes[eligible])]

    # --- RESULTS ---
    st.header("4. Results & Impact")
    
    # Portfolio Table
    res_df = pd.DataFrame({
        "Metric": [f"{asset1_name} Weight", f"{asset2_name} Weight", "Expected Return", "Risk (SD)", "Portfolio ESG Score", "Sharpe Ratio"],
        "Optimal (No Constraint)": [f"{weights[idx_all]*100:.2f}%", f"{(1-weights[idx_all])*100:.2f}%", f"{rets[idx_all]*100:.2f}%", f"{vols[idx_all]*100:.2f}%", f"{esgs[idx_all]:.2f}", f"{sharpes[idx_all]:.4f}"],
        "Optimal (With ESG)": [f"{weights[idx_esg]*100:.2f}%", f"{(1-weights[idx_esg])*100:.2f}%", f"{rets[idx_esg]*100:.2f}%", f"{vols[idx_esg]*100:.2f}%", f"{esgs[idx_esg]:.2f}", f"{sharpes[idx_esg]:.4f}"]
    })
    st.table(res_df)

    # Impact Table
    impact_df = pd.DataFrame({
        "Impact of ESG Constraint": ["Return Change", "Risk Change", "ESG Score Change"],
        "Value": [
            f"{(rets[idx_esg] - rets[idx_all])*100:.2f} percentage points",
            f"{(vols[idx_esg] - vols[idx_all])*100:.2f} percentage points",
            f"{(esgs[idx_esg] - esgs[idx_all]):.2f} points"
        ]
    })
    st.table(impact_df)

    # --- PLOTS ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Efficient Frontier & CML
    # Frontier line (wider range for visual)
    w_plot = np.linspace(-0.5, 1.5, 500)
    r_plot = portfolio_return(w_plot, r1, r2)
    v_plot = portfolio_sd(w_plot, sd1, sd2, rho)
    
    ax1.plot(v_plot, r_plot, color="gray", alpha=0.3, label="Frontier")
    
    # CML Lines
    sd_max = max(v_plot)
    sd_range = np.linspace(0, sd_max, 100)
    cml_all = r_free + ((rets[idx_all] - r_free) / vols[idx_all]) * sd_range
    cml_esg = r_free + ((rets[idx_esg] - r_free) / vols[idx_esg]) * sd_range
    
    ax1.plot(sd_range, cml_all, '--', color="blue", label="CML (No ESG)")
    ax1.plot(sd_range, cml_esg, '--', color="green", label="CML (ESG)")
    
    ax1.scatter(vols[idx_all], rets[idx_all], marker="*", s=250, color="blue", zorder=5, label="No ESG")
    ax1.scatter(vols[idx_esg], rets[idx_esg], marker="*", s=250, color="green", zorder=5, label="With ESG")
    ax1.scatter(0, r_free, color="black", marker="s", label="Risk-free")
    
    ax1.set_xlabel("Risk (Standard Deviation)")
    ax1.set_ylabel("Expected Return")
    ax1.set_title("Efficient Frontier & Capital Market Lines")
    ax1.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax1.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: ESG-Sharpe
    ax2.plot(esgs, sharpes, color="red", linewidth=2)
    ax2.axvline(esg_threshold, color="black", linestyle=":", label="Min ESG Threshold")
    ax2.scatter(esgs[idx_all], sharpes[idx_all], marker="*", s=200, color="blue")
    ax2.scatter(esgs[idx_esg], sharpes[idx_esg], marker="*", s=200, color="green")
    ax2.set_xlabel("Portfolio ESG Score")
    ax2.set_ylabel("Sharpe Ratio")
    ax2.set_title("ESG-Sharpe Trade-off")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    st.pyplot(fig)
    
    st.info(f"**Explanation:** The ESG constraint requires a minimum score of **{esg_threshold:.2f}**. " + 
            ("The unconstrained optimal already met this." if idx_all == idx_esg else "The portfolio was adjusted to meet your ESG preferences."))
