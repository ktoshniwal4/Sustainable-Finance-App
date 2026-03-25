import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

# --- CONFIGURATION ---
st.set_page_config(page_title="Sustainable Portfolio Tool", layout="wide")

# --- HELPER FUNCTIONS (Logic from your original code) ---
def convert_to_100(score, agency):
    agency = agency.lower()
    if agency == "sustainalytics":
        score = float(score)
        if score >= 50: return 0.0
        return max(0.0, min(100.0, 100 - (score / 50) * 100))
    elif agency == "msci":
        msci_map = {"ccc": 0.0, "b": 16.7, "bb": 33.4, "bbb": 50.1, "a": 66.8, "aa": 83.5, "aaa": 100.0}
        return msci_map.get(str(score).strip().lower(), 0.0)
    elif agency == "refinitiv":
        refinitiv_map = {0: 0.0, 1: 10.0, 2: 25.0, 3: 50.0, 4: 75.0, 5: 95.0}
        return refinitiv_map.get(int(float(score)), 0.0)
    elif agency == "s&p":
        return max(0.0, min(100.0, float(score)))
    return 0.0

def portfolio_return(w1, r1, r2): return w1 * r1 + (1 - w1) * r2
def portfolio_sd(w1, sd1, sd2, rho):
    return np.sqrt(w1**2 * sd1**2 + (1-w1)**2 * sd2**2 + 2 * rho * w1 * (1-w1) * sd1 * sd2)
def portfolio_esg(w1, esg1, esg2): return w1 * esg1 + (1 - w1) * esg2

# --- STREAMLIT UI ---
st.title("🌱 Sustainable Finance Portfolio Tool")
st.markdown("Compare two investments based on financial performance, risk, and ESG preferences.")

# --- SIDEBAR: ESG METHOD & RISK PREFERENCE ---
with st.sidebar:
    st.header("1. Preferences")
    
    # ESG Method
    esg_method = st.radio("ESG Information Method", 
                          ["Overall ESG score", "Separate E, S, and G scores"])
    use_separate = (esg_method == "Separate E, S, and G scores")
    
    w_e, w_s, w_g = 33.3, 33.3, 33.4
    if use_separate:
        st.subheader("Pillar Weights (%)")
        w_e = st.number_input("Environmental", 0, 100, 33)
        w_s = st.number_input("Social", 0, 100, 33)
        w_g = st.number_input("Governance", 0, 100, 34)
        if (w_e + w_s + w_g) != 100:
            st.error("Weights must sum to 100%!")

    # Risk Questionnaire
    st.markdown("---")
    st.subheader("Risk Preference (Gamma)")
    know_gamma = st.radio("Do you know your Gamma?", ["Yes", "Not Sure (Take Quiz)"])
    
    if know_gamma == "Yes":
        gamma = st.slider("Select Gamma (-10 to 10)", -10.0, 10.0, 2.0)
    else:
        with st.expander("Risk Questionnaire"):
            q1 = st.selectbox("General attitude to risk?", [1,2,3,4,5], format_func=lambda x: ["Avoid risk", "Low-risk", "Moderate", "High-return seeking", "High-risk seeker"][x-1])
            q2 = st.selectbox("Prefer slow/steady growth?", [1,2,3,4,5], format_func=lambda x: ["Strongly Agree", "Agree", "In-between", "Disagree", "Strongly Disagree"][x-1])
            q3 = st.selectbox("Reaction to 20% drop?", [1,2,3,4,5], format_func=lambda x: ["Sell all", "Sell some", "Wait", "Stay course", "Buy more"][x-1])
            avg = (q1 + q2 + q3) / 3
            if avg <= 1.5: gamma = 8.0
            elif avg <= 2.5: gamma = 4.0
            elif avg <= 3.5: gamma = 0.0
            elif avg <= 4.5: gamma = -4.0
            else: gamma = -8.0
            st.info(f"Calculated Gamma: {gamma}")

    # ESG Preference
    st.markdown("---")
    lambda_choice = st.selectbox("Accept lower return for better ESG?", 
                                 ["No reduction", "Small reduction", "Moderate reduction", "Significant reduction"])
    lambda_esg = {"No reduction": 0.0, "Small reduction": 0.25, "Moderate reduction": 0.75, "Significant reduction": 1.0}[lambda_choice]

# --- MAIN PAGE: ASSET DATA ---
col1, col2 = st.columns(2)

def get_asset_input(suffix, default_name):
    name = st.text_input(f"Asset {suffix} Name", default_name)
    ret = st.number_input(f"{name} Expected Return (%)", value=8.0) / 100
    vol = st.number_input(f"{name} Volatility (%)", value=15.0) / 100
    agency = st.selectbox(f"{name} Agency", ["MSCI", "Sustainalytics", "Refinitiv", "S&P"], key=f"agency_{suffix}")
    
    if use_separate:
        e = st.text_input(f"{name} E Score", "50", key=f"e_{suffix}")
        s = st.text_input(f"{name} S Score", "50", key=f"s_{suffix}")
        g = st.text_input(f"{name} G Score", "50", key=f"g_{suffix}")
        e100 = convert_to_100(e, agency)
        s100 = convert_to_100(s, agency)
        g100 = convert_to_100(g, agency)
        overall100 = (w_e/100)*e100 + (w_s/100)*s100 + (w_g/100)*g100
    else:
        score = st.text_input(f"{name} Overall ESG Score", "50", key=f"score_{suffix}")
        overall100 = convert_to_100(score, agency)
        
    return name, ret, vol, overall100

with col1:
    n1, r1, sd1, esg1_100 = get_asset_input("1", "Apple")
with col2:
    n2, r2, sd2, esg2_100 = get_asset_input("2", "Tesla")

rho = st.slider("Correlation Coefficient", -1.0, 1.0, 0.2)
r_free = st.number_input("Risk-free Rate (%)", value=2.0) / 100

# --- CALCULATIONS ---
if st.button("🚀 Run Portfolio Analysis"):
    weights = np.linspace(0, 1, 1000)
    esg_threshold = min(esg1_100, esg2_100) + lambda_esg * (max(esg1_100, esg2_100) - min(esg1_100, esg2_100))
    
    res = []
    for w in weights:
        p_ret = portfolio_return(w, r1, r2)
        p_sd = portfolio_sd(w, sd1, sd2, rho)
        p_esg = portfolio_esg(w, esg1_100, esg2_100)
        sharpe = (p_ret - r_free) / p_sd if p_sd > 0 else 0
        res.append([w, p_ret, p_sd, p_esg, sharpe])
    
    df = pd.DataFrame(res, columns=['w1', 'ret', 'sd', 'esg', 'sharpe'])
    
    # Optimal Portfolios
    opt_no_esg = df.iloc[df['sharpe'].idxmax()]
    eligible = df[df['esg'] >= esg_threshold]
    
    if eligible.empty:
        st.error("No portfolios satisfy the ESG threshold.")
    else:
        opt_esg = eligible.iloc[eligible['sharpe'].idxmax()]
        
        # Display Tables
        st.subheader("Analysis Results")
        comp_data = {
            "Metric": [f"{n1} Weight", f"{n2} Weight", "Return", "Risk", "ESG Score", "Sharpe Ratio"],
            "Unconstrained": [f"{opt_no_esg['w1']*100:.1f}%", f"{(1-opt_no_esg['w1'])*100:.1f}%", f"{opt_no_esg['ret']*100:.2f}%", f"{opt_no_esg['sd']*100:.2f}%", f"{opt_no_esg['esg']:.1f}", f"{opt_no_esg['sharpe']:.3f}"],
            "ESG Constrained": [f"{opt_esg['w1']*100:.1f}%", f"{(1-opt_esg['w1'])*100:.1f}%", f"{opt_esg['ret']*100:.2f}%", f"{opt_esg['sd']*100:.2f}%", f"{opt_esg['esg']:.1f}", f"{opt_esg['sharpe']:.3f}"]
        }
        st.table(pd.DataFrame(comp_data))

        # Plots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Efficient Frontier
        ax1.plot(df['sd'], df['ret'], color='gray', linestyle='--', label='Possible Portfolios')
        ax1.plot(eligible['sd'], eligible['ret'], color='green', label='ESG Eligible')
        ax1.scatter(opt_no_esg['sd'], opt_no_esg['ret'], marker='*', s=200, label='Optimal (No ESG)')
        ax1.scatter(opt_esg['sd'], opt_esg['ret'], marker='*', s=200, color='green', label='Optimal (ESG)')
        ax1.set_xlabel("Risk (SD)"); ax1.set_ylabel("Return")
        ax1.legend()
        
        # ESG vs Sharpe
        ax2.plot(df['esg'], df['sharpe'], color='red')
        ax2.axvline(esg_threshold, color='black', linestyle=':', label='Min ESG')
        ax2.set_xlabel("ESG Score"); ax2.set_ylabel("Sharpe Ratio")
        
        st.pyplot(fig)
